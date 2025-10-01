import hashlib
import hmac
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
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

class DeltaExchangeAPI:
    """Delta Exchange API client for trading operations"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://api.india.delta.exchange', symbol: str = None):
        logger.info(f"DeltaExchangeAPI initialized with Base URL: {base_url}")
        logger.info(f"DeltaExchangeAPI initialized with Symbol: {symbol}")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.symbol = symbol
        
    def generate_signature(self, secret: str, message: str) -> str:
        """Generate HMAC SHA256 signature for API authentication"""
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        hash_obj = hmac.new(secret, message, hashlib.sha256)
        return hash_obj.hexdigest()
    
    def make_request(self, method: str, path: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make authenticated API request"""
        timestamp = str(int(time.time()))
        url = f"{self.base_url}{path}"
        
        # Prepare query string
        query_string = ''
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            if query_string:
                query_string = '?' + query_string
        
        # Prepare payload
        payload = ''
        if data:
            payload = json.dumps(data)
        
        # Generate signature
        signature_data = method + timestamp + path + query_string + payload
        signature = self.generate_signature(self.api_secret, signature_data)
        
        # Prepare headers
        headers = {
            'api-key': self.api_key,
            'timestamp': timestamp,
            'signature': signature,
            'User-Agent': 'python-trading-bot',
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Making API request: {method} {url}")
            logger.info(f"Request params: {params}")
            logger.info(f"Request payload: {payload}")
            # Don't log headers to avoid exposing API credentials
            logger.debug(f"Request -> {method} {url} params={params} payload={payload}")
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, data=payload, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=30)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                # Log status code and response body for debugging
                body = None
                try:
                    body = response.json()
                except Exception:
                    body = response.text
                logger.error(f"API request failed: {http_err} - status: {response.status_code} - body: {body}")
                return {'success': False, 'error': str(http_err), 'status_code': response.status_code, 'body': body}

            # Successful response
            try:
                return response.json()
            except ValueError:
                return {'success': True, 'result': response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_candles(self, symbol: str, resolution: str, start: int, end: int) -> List[Dict]:
        """Get historical OHLC candle data"""
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'start': start,
            'end': end
        }
        
        response = self.make_request('GET', '/v2/history/candles', params=params)
        if response.get('success'):
            return response.get('result', [])
        else:
            logger.error(f"Failed to get candles: {response}")
            return []
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        response = self.make_request('GET', f'/v2/tickers/{symbol}')
        if response.get('success'):
            return response.get('result', {})
        else:
            logger.error(f"Failed to get ticker: {response}")
            return {}
    
    def place_order(self, product_symbol: str, side: str, size: int, order_type: str = 'market_order', 
                   limit_price: str = None, stop_price: str = None) -> Dict:
        """Place a trading order"""
        order_data = {
            'product_symbol': product_symbol,
            'side': side,
            'size': size,
            'order_type': order_type
        }
        
        if limit_price and order_type == 'limit_order':
            order_data['limit_price'] = limit_price
        
        if stop_price:
            order_data['stop_price'] = stop_price
            order_data['stop_order_type'] = 'stop_loss_order'
        
        response = self.make_request('POST', '/v2/orders', data=order_data)
        if response.get('success'):
            logger.info(f"Order placed successfully: {response['result']}")
            return response['result']
        else:
            logger.error(f"Failed to place order: {response}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions for the trading symbol"""
        # Use the correct endpoint from official documentation
        response = self.make_request('GET', '/v2/positions/margined', params={})
        if response.get('success'):
            logger.info("Successfully fetched positions from /v2/positions/margined")
            return response.get('result', [])
        else:
            logger.error(f"Failed to get positions: {response}")
            return []
    
    def get_orders(self, product_symbol: str = None, state: str = 'open') -> List[Dict]:
        """Get orders"""
        params = {'state': state}
        if product_symbol:
            params['product_symbol'] = product_symbol
            
        response = self.make_request('GET', '/v2/orders', params=params)
        if response.get('success'):
            return response.get('result', [])
        else:
            logger.error(f"Failed to get orders: {response}")
            return []

class TechnicalIndicators:
    """Technical analysis indicators for trading strategies"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(avg)
        
        return sma_values
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA for the first value
        sma_first = sum(prices[:period]) / period
        ema_values.append(sma_first)
        
        # Calculate EMA for remaining values
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def detect_crossover(short_ma: List[float], long_ma: List[float]) -> Tuple[bool, bool]:
        """Detect golden cross (bullish) and death cross (bearish) signals"""
        if len(short_ma) < 2 or len(long_ma) < 2:
            return False, False
        
        # Current and previous values
        short_current, short_prev = short_ma[-1], short_ma[-2]
        long_current, long_prev = long_ma[-1], long_ma[-2]
        
        # Golden cross: short MA crosses above long MA
        golden_cross = short_prev <= long_prev and short_current > long_current
        
        # Death cross: short MA crosses below long MA
        death_cross = short_prev >= long_prev and short_current < long_current
        
        return golden_cross, death_cross

class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(self, max_position_size: int = 10, stop_loss_pct: float = 0.02, 
                 take_profit_pct: float = 0.04, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.last_reset_date = datetime.now().date()
    
    def reset_daily_counters(self):
        """Reset daily counters if new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_pnl = 0.0
            self.trades_today = 0
            self.last_reset_date = current_date
            logger.info("Daily counters reset")
    
    def can_trade(self) -> bool:
        """Check if trading is allowed based on risk parameters"""
        self.reset_daily_counters()
        
        if abs(self.daily_pnl) >= self.max_daily_loss:
            logger.warning(f"Daily loss limit reached: {self.daily_pnl:.4f}")
            return False
        
        return True
    
    def calculate_position_size(self, current_price: float, account_balance: float) -> int:
        """Calculate appropriate position size based on risk management"""
        return 1
        if not self.can_trade():
            return 0
        
        # Use a percentage of account balance for position sizing
        risk_amount = account_balance * 0.01  # 1% of account per trade
        position_value = risk_amount / self.stop_loss_pct
        position_size = int(position_value / current_price)
        
        # Ensure position size doesn't exceed maximum
        return min(position_size, self.max_position_size)
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == 'buy':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        if side == 'buy':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

class MovingAverageTradingBot:
    """Main trading bot class implementing moving average strategies"""
    
    def __init__(self, api_key: str, api_secret: str, symbol: str = 'BTCUSD'):
        logger.info(f"MovingAverageTradingBot initialized with Symbol: {symbol}")
        
        self.symbol = symbol
        self.api = DeltaExchangeAPI(api_key, api_secret, symbol=self.symbol)
        self.risk_manager = RiskManager()
        self.indicators = TechnicalIndicators()
        
        # Strategy parameters
        self.short_ma_period = 9
        self.long_ma_period = 10
        self.ema_short_period = 9
        self.ema_long_period = 10
        self.candle_resolution = '1h'
        self.lookback_hours = 24
        
        # Trading state
        self.current_position = None
        self.last_signal_time = 0
        self.signal_cooldown = 300  # 5 minutes between signals
        
        # Data storage
        self.price_data = []
        self.timestamps = []
        
        logger.info(f"Trading bot initialized for {symbol}")
    
    def fetch_historical_data(self) -> bool:
        """Fetch historical candle data for analysis"""
        try:
            end_time = int(time.time())
            start_time = end_time - (self.lookback_hours * 3600)
            
            candles = self.api.get_candles(self.symbol, self.candle_resolution, start_time, end_time)
            
            if not candles:
                logger.error("No historical data received")
                return False
            
            # Extract price data
            self.price_data = [float(candle['close']) for candle in candles]
            self.timestamps = [candle['time'] for candle in candles]
            
            logger.info(f"Fetched {len(self.price_data)} candles for analysis")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return False
    
    def update_current_price(self) -> Optional[float]:
        """Get current market price"""
        try:
            ticker = self.api.get_ticker(self.symbol)
            if ticker and 'close' in ticker:
                current_price = float(ticker['close'])
                
                # Add to price data
                self.price_data.append(current_price)
                self.timestamps.append(int(time.time()))
                
                # Keep only recent data
                max_data_points = 200
                if len(self.price_data) > max_data_points:
                    self.price_data = self.price_data[-max_data_points:]
                    self.timestamps = self.timestamps[-max_data_points:]
                
                return current_price
            
        except Exception as e:
            logger.error(f"Error updating current price: {e}")
        
        return None
    
    def calculate_signals(self) -> Dict:
        """Calculate trading signals based on moving averages"""
        if len(self.price_data) < max(self.long_ma_period, self.ema_long_period):
            return {'sma_signal': None, 'ema_signal': None}
        
        # Calculate SMAs
        sma_short = self.indicators.sma(self.price_data, self.short_ma_period)
        sma_long = self.indicators.sma(self.price_data, self.long_ma_period)
        
        # Calculate EMAs
        ema_short = self.indicators.ema(self.price_data, self.ema_short_period)
        ema_long = self.indicators.ema(self.price_data, self.ema_long_period)
        
        # Detect crossovers
        sma_golden, sma_death = self.indicators.detect_crossover(sma_short, sma_long)
        ema_golden, ema_death = self.indicators.detect_crossover(ema_short, ema_long)
        
        signals = {
            'sma_signal': 'buy' if sma_golden else 'sell' if sma_death else None,
            'ema_signal': 'buy' if ema_golden else 'sell' if ema_death else None,
            'sma_short': sma_short[-1] if sma_short else None,
            'sma_long': sma_long[-1] if sma_long else None,
            'ema_short': ema_short[-1] if ema_short else None,
            'ema_long': ema_long[-1] if ema_long else None,
            'current_price': self.price_data[-1]
        }
        
        return signals
    
    def get_current_position(self) -> Optional[Dict]:
        """Get current position for the trading symbol"""
        try:
            positions = self.api.get_positions()
            for position in positions:
                if position.get('product_symbol') == self.symbol:
                    if float(position.get('size', 0)) != 0:
                        return position
            return None
            
        except Exception as e:
            logger.error(f"Error getting current position: {e}")
            return None
    
    def execute_trade(self, signal: str, current_price: float) -> bool:
        """Execute trade based on signal"""
        try:
            # Check if we can trade
            if not self.risk_manager.can_trade():
                return False
            
            # Check signal cooldown
            current_time = time.time()
            if current_time - self.last_signal_time < self.signal_cooldown:
                return False
            
            # Get current position
            current_position = self.get_current_position()
            
            # Determine trade action
            if signal == 'buy':
                if current_position and float(current_position.get('size', 0)) > 0:
                    logger.info("Already in long position, skipping buy signal")
                    return False
                
                # Close short position if exists
                if current_position and float(current_position.get('size', 0)) < 0:
                    self.close_position(current_position)
                
                # Open long position
                return self.open_long_position(current_price)
                
            elif signal == 'sell':
                if current_position and float(current_position.get('size', 0)) < 0:
                    logger.info("Already in short position, skipping sell signal")
                    return False
                
                # Close long position if exists
                if current_position and float(current_position.get('size', 0)) > 0:
                    self.close_position(current_position)
                
                # Open short position
                return self.open_short_position(current_price)
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
        
        return False
    
    def open_long_position(self, current_price: float) -> bool:
        """Open a long position"""
        try:
            # Calculate position size (assuming account balance of 10000 for demo)
            position_size = self.risk_manager.calculate_position_size(current_price, 10000)
            
            if position_size <= 0:
                logger.warning("Position size is 0, skipping trade")
                return False
            
            # Place market buy order
            order = self.api.place_order(
                product_symbol=self.symbol,
                side='buy',
                size=position_size,
                order_type='market_order'
            )
            
            if order:
                logger.info(f"Long position opened: {position_size} units at ~{current_price}")
                self.last_signal_time = time.time()
                return True
                
        except Exception as e:
            logger.error(f"Error opening long position: {e}")
        
        return False
    
    def open_short_position(self, current_price: float) -> bool:
        """Open a short position"""
        try:
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(current_price, 10000)
            
            if position_size <= 0:
                logger.warning("Position size is 0, skipping trade")
                return False
            
            # Place market sell order
            order = self.api.place_order(
                product_symbol=self.symbol,
                side='sell',
                size=position_size,
                order_type='market_order'
            )
            
            if order:
                logger.info(f"Short position opened: {position_size} units at ~{current_price}")
                self.last_signal_time = time.time()
                return True
                
        except Exception as e:
            logger.error(f"Error opening short position: {e}")
        
        return False
    
    def close_position(self, position: Dict) -> bool:
        """Close an existing position"""
        try:
            position_size = abs(int(float(position.get('size', 0))))
            current_side = 'buy' if float(position.get('size', 0)) < 0 else 'sell'
            
            order = self.api.place_order(
                product_symbol=self.symbol,
                side=current_side,
                size=position_size,
                order_type='market_order'
            )
            
            if order:
                logger.info(f"Position closed: {position_size} units")
                return True
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
        
        return False
    
    def log_status(self, signals: Dict):
        """Log current trading status"""
        current_position = self.get_current_position()
        position_info = "No position"
        
        if current_position:
            size = float(current_position.get('size', 0))
            side = "Long" if size > 0 else "Short"
            position_info = f"{side} {abs(size)} units"
        
        sma_short_str = f"{signals['sma_short']:.2f}" if signals['sma_short'] is not None else "N/A"
        sma_long_str = f"{signals['sma_long']:.2f}" if signals['sma_long'] is not None else "N/A"
        logger.info(
            f"Status - Price: {signals['current_price']:.2f}, "
            f"SMA({self.short_ma_period}): {sma_short_str}, "
            f"SMA({self.long_ma_period}): {sma_long_str}, "
            f"Position: {position_info}"
        )
    
    def run(self):
        """Main trading loop"""
        logger.info("Starting Moving Average Trading Bot")
        
        # Fetch initial historical data
        if not self.fetch_historical_data():
            logger.error("Failed to fetch historical data, exiting")
            return
        
        try:
            while True:
                # Update current price
                current_price = self.update_current_price()
                if not current_price:
                    logger.warning("Failed to get current price, retrying...")
                    time.sleep(30)
                    continue
                
                # Calculate signals
                signals = self.calculate_signals()
                
                # Log current status
                self.log_status(signals)
                
                # Check for trading signals
                primary_signal = signals['sma_signal']  # Use SMA as primary signal
                secondary_signal=signals['ema_signal']
                if primary_signal:
                    logger.info(f"Trading signal detected: {primary_signal.upper()}")
                    
                    # Execute trade
                    if self.execute_trade(primary_signal, current_price):
                        logger.info(f"Trade executed successfully: {primary_signal}")
                        break
                    else:
                        logger.warning(f"Failed to execute trade: {primary_signal}")
                elif secondary_signal:
                    logger.info(f"Trading signal detected: {secondary_signal.upper()}")
                    
                    # Execute trade
                    if self.execute_trade(secondary_signal, current_price):
                        logger.info(f"Trade executed successfully: {secondary_signal}")
                        break
                    else:
                        logger.warning(f"Failed to execute trade: {secondary_signal}")
                # Wait before next iteration
                time.sleep(10)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")

def main():
    """Main function to run the trading bot"""
    
    # Configuration - REPLACE WITH YOUR ACTUAL API CREDENTIALS
    load_dotenv()
    API_KEY = os.getenv('DELTA_API_KEY')
    
    API_SECRET = os.getenv('DELTA_API_SECRET')
    TRADING_SYMBOL = os.getenv('TRADING_SYMBOL')  # Change to your preferred trading pair
    
    # Validate configuration
    if API_KEY == 'your_api_key_here' or API_SECRET == 'your_api_secret_here' or API_KEY is None or API_SECRET is None:
        logger.error("Please set your actual API credentials before running the bot")
        return
    
    # Create and run trading bot
    try:
        bot = MovingAverageTradingBot(API_KEY, API_SECRET, TRADING_SYMBOL)
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start trading bot: {e}")

if __name__ == "__main__":
    main()
