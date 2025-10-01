from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

# Add parent directory to path to import strategy module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategymovingaverage import MovingAverageTradingBot, DeltaExchangeAPI
from news_service.crypto_news_trader import CryptoNewsTrader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
# Try to load from parent directory first, then current directory
env_path = os.environ.get("ENV_FILE_PATH")
if env_path and os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Try parent directory
    parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
    else:
        # Fallback to current directory
        load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for bot state
trading_bot = None
bot_thread = None
bot_running = False
news_trader = None
news_thread = None
news_running = False
bot_status = {
    'running': False,
    'symbol': None,
    'current_price': 0,
    'position': None,
    'signals': {},
    'last_update': None,
    'pnl': 0,
    'trades_today': 0
}

# News data storage
latest_news = {
    'articles': [],
    'signals': {},
    'recommendation': {},
    'last_update': None
}

# Configuration storage
trading_config = {
    # API Credentials
    'api_key': '',
    'api_secret': '',
    'trading_symbol': 'BTCUSD',
    
    # Trading Strategy Settings
    'sma_short_period': 9,
    'sma_long_period': 21,
    'ema_short_period': 9,
    'ema_long_period': 21,
    
    # Risk Management
    'position_size': 1,
    'stop_loss_percent': 2,
    'take_profit_percent': 4,
    'max_daily_trades': 10,
    
    # News Analysis Settings
    'news_confidence_threshold': 0.7,
    'news_update_interval': 5,
    'enable_news_trading': True,
    'news_weight': 0.3,
    
    # Trading Schedule
    'trading_start_time': '09:00',
    'trading_end_time': '17:00',
    'enable_weekend_trading': False,
    'trading_interval': 10,
    
    # Advanced Settings
    'api_timeout': 30,
    'max_retries': 3,
    'log_level': 'INFO',
    'enable_paper_trading': False
}

class WebTradingBot(MovingAverageTradingBot):
    """Extended trading bot with web interface support"""
    
    def __init__(self, api_key: str, api_secret: str, symbol: str = 'BTCUSD'):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"WebTradingBot initialized with Symbol: {symbol}")
        
        super().__init__(api_key, api_secret, symbol)
        self.last_status_update = 0
        
    def log_status(self, signals: Dict):
        """Override to emit status updates via WebSocket"""
        super().log_status(signals)
        
        # Update global status
        current_position = self.get_current_position()
        position_info = None
        
        if current_position:
            size = float(current_position.get('size', 0))
            side = 'long' if size > 0 else 'short'
            abs_size = abs(size)
            entry_price = float(current_position.get('entry_price', 0) or 0)
            
            # Use realized_pnl from official API response format
            realized_pnl = current_position.get('realized_pnl')
            realized_pnl_value = float(realized_pnl) if realized_pnl is not None else 0.0
            
            # Also try to get unrealized_pnl if available
            api_unrealized = current_position.get('unrealized_pnl')
            unrealized_from_api = float(api_unrealized) if api_unrealized is not None else None
            
            # Compute unrealized P&L if API doesn't provide it, using latest price
            computed_unrealized = None
            try:
                latest_price = float(signals.get('current_price') or 0)
                if entry_price and abs_size and latest_price:
                    if side == 'long':
                        computed_unrealized = (latest_price - entry_price) * abs_size
                    else:
                        computed_unrealized = (entry_price - latest_price) * abs_size
            except Exception:
                computed_unrealized = None
            
            final_unrealized = unrealized_from_api if (unrealized_from_api is not None and unrealized_from_api != 0) else (computed_unrealized or 0.0)
            
            # Total P&L = realized + unrealized
            total_pnl = realized_pnl_value + final_unrealized
            
            position_info = {
                'side': side,
                'size': abs_size,
                'entry_price': entry_price,
                'realized_pnl': realized_pnl_value,
                'unrealized_pnl': final_unrealized,
                'total_pnl': total_pnl
            }
        
        # Update global bot status
        global bot_status
        bot_status.update({
            'running': True,
            'symbol': self.symbol,
            'current_price': signals['current_price'],
            'position': position_info,
            'signals': {
                'sma_signal': signals['sma_signal'],
                'ema_signal': signals['ema_signal'],
                'sma_short': signals['sma_short'],
                'sma_long': signals['sma_long'],
                'ema_short': signals['ema_short'],
                'ema_long': signals['ema_long']
            },
            'last_update': datetime.now().isoformat(),
            'pnl': position_info['total_pnl'] if position_info else 0
        })
        
        # Emit status update via WebSocket
        socketio.emit('status_update', bot_status)
    
    def run(self):
        """Override main loop to work with web interface"""
        global bot_running, bot_status
        
        self.logger.info("Starting Web Trading Bot")
        bot_status['running'] = True
        
        # Fetch initial historical data
        if not self.fetch_historical_data():
            self.logger.error("Failed to fetch historical data")
            bot_status['running'] = False
            return
        
        try:
            while bot_running:
                # Update current price
                current_price = self.update_current_price()
                if not current_price:
                    self.logger.warning("Failed to get current price, retrying...")
                    time.sleep(30)
                    continue
                
                # Calculate signals
                signals = self.calculate_signals()
                
                # Log current status (this will emit WebSocket update)
                self.log_status(signals)
                
                # Check for trading signals
                primary_signal = signals['sma_signal']
                secondary_signal = signals['ema_signal']
                
                # Get news-based recommendation
                news_recommendation = self.get_news_recommendation()
                
                # Combine technical and news signals
                final_signal = self.combine_signals(primary_signal, secondary_signal, news_recommendation)
                
                if final_signal:
                    self.logger.info(f"Trading signal detected: {final_signal.upper()}")
                    self.logger.info(f"Technical: {primary_signal}, News: {news_recommendation}")
                    
                    # Execute trade
                    if self.execute_trade(final_signal, current_price):
                        self.logger.info(f"Trade executed successfully: {final_signal}")
                        socketio.emit('trade_executed', {
                            'signal': final_signal,
                            'price': current_price,
                            'timestamp': datetime.now().isoformat(),
                            'news_sentiment': news_recommendation
                        })
                    else:
                        self.logger.warning(f"Failed to execute trade: {final_signal}")
                        
                elif primary_signal or secondary_signal:
                    self.logger.info(f"Technical signal detected but news sentiment is neutral: {primary_signal or secondary_signal}")
                    self.logger.info(f"News recommendation: {news_recommendation}")
                
                # Wait before next iteration
                time.sleep(10)
                
        except Exception as e:
            self.logger.error(f"Error in trading bot: {e}")
            socketio.emit('bot_error', {'error': str(e)})
        finally:
            bot_status['running'] = False
            socketio.emit('bot_stopped', {})
    
    def get_news_recommendation(self):
        """Get news-based trading recommendation"""
        global latest_news, news_trader
        
        try:
            if not news_trader or not latest_news.get('recommendation'):
                return 'NEUTRAL'
            
            recommendation = latest_news['recommendation']
            
            # Only use high-confidence news signals
            if recommendation.get('overall_confidence', 0) >= 0.7:
                return recommendation.get('recommendation', 'NEUTRAL')
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            self.logger.error(f"Error getting news recommendation: {e}")
            return 'NEUTRAL'
    
    def combine_signals(self, technical_signal, secondary_signal, news_signal):
        """Combine technical analysis with news sentiment"""
        
        # If no technical signal, don't trade
        if not technical_signal and not secondary_signal:
            return None
        
        # Use primary technical signal if available
        signal = technical_signal or secondary_signal
        
        # News signal weighting
        if news_signal == 'NEUTRAL':
            # Proceed with technical signal if news is neutral
            return signal
        elif news_signal == signal.upper():
            # News confirms technical signal - proceed with confidence
            return signal
        elif news_signal != signal.upper():
            # News contradicts technical signal - be more cautious
            # Only trade if both signals are strong
            if technical_signal and secondary_signal and technical_signal == secondary_signal:
                self.logger.warning(f"News sentiment ({news_signal}) contradicts technical signal ({signal})")
                return None  # Don't trade if conflicting signals
            else:
                return None  # Don't trade on conflicting signals
        
        return signal

def news_worker():
    """Background worker for fetching and analyzing crypto news"""
    global news_trader, news_running, latest_news
    
    try:
        logger.info("Starting crypto news service")
        news_trader = CryptoNewsTrader()
        
        while news_running:
            try:
                logger.info("Fetching latest crypto news...")
                
                # Get news from RSS feeds
                all_news = news_trader.get_crypto_news_feeds()
                
                if all_news:
                    # Analyze each news item
                    high_confidence_signals = []
                    
                    for news_item in all_news:
                        try:
                            signal_data = news_trader.generate_trading_signal(news_item)
                            news_trader.save_news_signal(news_item, signal_data)
                            
                            # Collect high-confidence signals
                            if signal_data['confidence'] >= 0.65:
                                high_confidence_signals.append({
                                    'news': news_item,
                                    'signal': signal_data
                                })
                                
                        except Exception as e:
                            logger.error(f"Error processing news item: {e}")
                            continue
                    
                    # Get overall trading recommendation
                    recommendation = news_trader.get_trading_recommendation(min_confidence=0.65)
                    
                    # Update global news data
                    latest_news.update({
                        'articles': all_news[:10],  # Top 10 articles
                        'signals': high_confidence_signals[:5],  # Top 5 signals
                        'recommendation': recommendation,
                        'last_update': datetime.now().isoformat()
                    })
                    
                    # Emit news update via WebSocket
                    socketio.emit('news_update', latest_news)
                    
                    logger.info(f"Updated news: {len(all_news)} articles, {len(high_confidence_signals)} signals")
                
            except Exception as e:
                logger.error(f"Error in news worker: {e}")
                
            # Wait 60 seconds before next update
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"News worker failed: {e}")
        socketio.emit('news_error', {'error': str(e)})
    finally:
        news_running = False

@app.route('/')
def index():
    """Serve the main trading dashboard"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'service': 'Delta Exchange Trading Bot',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)

@app.route('/api/news')
def get_news():
    """Get latest crypto news and signals"""
    return jsonify(latest_news)

@app.route('/api/start-news', methods=['POST'])
def start_news():
    """Start the crypto news service"""
    global news_thread, news_running
    
    if news_running:
        return jsonify({'success': False, 'message': 'News service is already running'})
    
    try:
        news_running = True
        news_thread = threading.Thread(target=news_worker)
        news_thread.daemon = True
        news_thread.start()
        
        logger.info("Crypto news service started")
        return jsonify({'success': True, 'message': 'News service started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting news service: {str(e)}'})

@app.route('/api/stop-news', methods=['POST'])
def stop_news():
    """Stop the crypto news service"""
    global news_running
    
    if not news_running:
        return jsonify({'success': False, 'message': 'News service is not running'})
    
    try:
        news_running = False
        logger.info("Crypto news service stopped")
        return jsonify({'success': True, 'message': 'News service stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping news service: {str(e)}'})

@app.route('/api/crypto-signals/<crypto_symbol>')
def get_crypto_signals(crypto_symbol):
    """Get signals specific to a particular cryptocurrency"""
    try:
        if not news_trader:
            return jsonify({'success': False, 'message': 'News service not initialized'})
        
        signals = news_trader.get_crypto_specific_signals(crypto_symbol.upper())
        return jsonify({'success': True, 'signals': signals})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting crypto signals: {str(e)}'})

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current trading configuration"""
    try:
        return jsonify({'success': True, 'config': trading_config})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting configuration: {str(e)}'})

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save trading configuration"""
    global trading_config
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No configuration data provided'})
        
        # Validate and update configuration
        for key, value in data.items():
            if key in trading_config:
                # Type validation
                if key in ['sma_short_period', 'sma_long_period', 'ema_short_period', 'ema_long_period', 
                          'max_daily_trades', 'news_update_interval', 'trading_interval', 
                          'api_timeout', 'max_retries']:
                    if not isinstance(value, (int, float)) or value <= 0:
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be a positive number'})
                elif key in ['position_size', 'stop_loss_percent', 'take_profit_percent', 
                           'news_confidence_threshold', 'news_weight']:
                    if not isinstance(value, (int, float)) or value < 0:
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be a non-negative number'})
                elif key in ['enable_news_trading', 'enable_weekend_trading', 'enable_paper_trading']:
                    if not isinstance(value, bool):
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be true or false'})
                elif key in ['trading_start_time', 'trading_end_time']:
                    if not isinstance(value, str):
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be a time string'})
                    # Validate time format (HH:MM)
                    try:
                        datetime.strptime(value, '%H:%M')
                    except ValueError:
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be in HH:MM format (e.g., 09:00)'})
                elif key in ['api_key', 'api_secret', 'trading_symbol']:
                    if not isinstance(value, str):
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be a string'})
                    if key in ['api_key', 'api_secret'] and len(value.strip()) == 0:
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: cannot be empty'})
                elif key == 'log_level':
                    if value not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                        return jsonify({'success': False, 'message': f'Invalid value for {key}: must be DEBUG, INFO, WARNING, or ERROR'})
                
                trading_config[key] = value
        
        # Save configuration to file
        save_config_to_file()
        
        logger.info("Trading configuration updated")
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return jsonify({'success': False, 'message': f'Error saving configuration: {str(e)}'})

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    """Reset configuration to default values"""
    global trading_config
    
    try:
        # Reset to default values
        trading_config = {
            'api_key': '',
            'api_secret': '',
            'trading_symbol': 'BTCUSD',
            'sma_short_period': 9,
            'sma_long_period': 21,
            'ema_short_period': 9,
            'ema_long_period': 21,
            'position_size': 1,
            'stop_loss_percent': 2,
            'take_profit_percent': 4,
            'max_daily_trades': 10,
            'news_confidence_threshold': 0.7,
            'news_update_interval': 5,
            'enable_news_trading': True,
            'news_weight': 0.3,
            'trading_start_time': '09:00',
            'trading_end_time': '17:00',
            'enable_weekend_trading': False,
            'trading_interval': 10,
            'api_timeout': 30,
            'max_retries': 3,
            'log_level': 'INFO',
            'enable_paper_trading': False
        }
        
        # Save to file
        save_config_to_file()
        
        logger.info("Trading configuration reset to defaults")
        return jsonify({'success': True, 'message': 'Configuration reset to defaults', 'config': trading_config})
        
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}")
        return jsonify({'success': False, 'message': f'Error resetting configuration: {str(e)}'})

def save_config_to_file():
    """Save configuration to JSON file"""
    try:
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trading_config.json')
        with open(config_file, 'w') as f:
            json.dump(trading_config, f, indent=2)
        logger.info(f"Configuration saved to {config_file}")
    except Exception as e:
        logger.error(f"Error saving configuration to file: {e}")

def load_config_from_file():
    """Load configuration from JSON file"""
    global trading_config
    try:
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trading_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in saved_config.items():
                    if key in trading_config:
                        trading_config[key] = value
            logger.info(f"Configuration loaded from {config_file}")
        else:
            logger.info("No configuration file found, using defaults")
    except Exception as e:
        logger.error(f"Error loading configuration from file: {e}")

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global trading_bot, bot_thread, bot_running, trading_config
    
    if bot_running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        # Get API credentials from configuration
        api_key = trading_config.get('api_key', '').strip()
        api_secret = trading_config.get('api_secret', '').strip()
        symbol = trading_config.get('trading_symbol', 'BTCUSD')
        
        if not api_key or not api_secret:
            return jsonify({'success': False, 'message': 'API credentials not configured. Please set API key and secret in configuration.'})
        
        # Create and start bot
        try:
            logger.info(f"Starting bot with Symbol: {symbol}")
            
            trading_bot = WebTradingBot(api_key, api_secret, symbol)
            bot_running = True
            
            # Start bot in separate thread
            bot_thread = threading.Thread(target=trading_bot.run)
            bot_thread.daemon = True
            bot_thread.start()
            
            logger.info(f"Trading bot started successfully for {symbol}")
        except Exception as e:
            logger.error(f"Failed to create trading bot: {e}")
            return jsonify({'success': False, 'message': f'Failed to create bot: {str(e)}'})
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting bot: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running, trading_bot
    
    if not bot_running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        bot_running = False
        bot_status['running'] = False
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping bot: {str(e)}'})

@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        positions = trading_bot.api.get_positions()
        return jsonify({'success': True, 'positions': positions})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting positions: {str(e)}'})

@app.route('/api/orders')
def get_orders():
    """Get current orders"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        orders = trading_bot.api.get_orders()
        return jsonify({'success': True, 'orders': orders})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting orders: {str(e)}'})

@app.route('/api/manual-trade', methods=['POST'])
def manual_trade():
    """Execute manual trade"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        data = request.get_json()
        side = data.get('side')  # 'buy' or 'sell'
        size = data.get('size', 1)
        order_type = data.get('order_type', 'market_order')
        
        if not side:
            return jsonify({'success': False, 'message': 'Side (buy/sell) required'})
        
        # Get current price
        current_price = trading_bot.update_current_price()
        if not current_price:
            return jsonify({'success': False, 'message': 'Could not get current price'})
        
        # Execute trade
        if side == 'buy':
            success = trading_bot.open_long_position(current_price)
        else:
            success = trading_bot.open_short_position(current_price)
        
        if success:
            return jsonify({'success': True, 'message': f'{side.capitalize()} order executed'})
        else:
            return jsonify({'success': False, 'message': 'Failed to execute order'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error executing trade: {str(e)}'})

@app.route('/api/close-position', methods=['POST'])
def close_position():
    """Close current position"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        position = trading_bot.get_current_position()
        if not position:
            return jsonify({'success': False, 'message': 'No position to close'})
        
        success = trading_bot.close_position(position)
        
        if success:
            return jsonify({'success': True, 'message': 'Position closed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to close position'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error closing position: {str(e)}'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status_update', bot_status)
    emit('news_update', latest_news)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Load configuration from file
    load_config_from_file()
    
    # Run the Flask app with SocketIO
    port = int(os.environ.get('PORT', 5003))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
