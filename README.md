# 🚀 Delta Exchange Trading Bot - Full Stack Application

A comprehensive full-stack trading bot for Delta Exchange India that implements moving average strategies with a modern web interface.

## ✨ Features

- **🤖 Automated Trading**: Implements SMA and EMA crossover strategies
- **🌐 Web Dashboard**: Real-time trading dashboard with live updates
- **📊 Technical Analysis**: Moving average calculations and signal detection
- **⚡ Real-time Updates**: WebSocket-based live price and signal updates
- **🎯 Manual Trading**: Manual buy/sell controls for immediate execution
- **📈 Live Charts**: Real-time price charts with Chart.js
- **🛡️ Risk Management**: Built-in position sizing and risk controls
- **📝 Trading Logs**: Comprehensive logging of all trading activities

## 🏗️ Architecture

```
4FullstackTradeApp/
├── backend/
│   ├── app.py              # Flask backend with WebSocket support
│   └── templates/
│       └── index.html      # Frontend dashboard
├── strategymovingaverage.py # Core trading strategy implementation
├── main.py                 # Application launcher
├── requirements.txt        # Python dependencies
├── config.env.example     # Environment configuration template
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

Copy the example configuration file and update with your credentials:

```bash
cp config.env.example .env
```

Edit `.env` file with your Delta Exchange API credentials:

```env
DELTA_API_KEY=your_actual_api_key
DELTA_API_SECRET=your_actual_api_secret
TRADING_SYMBOL=BTCUSD
```

### 3. Run the Application

```bash
python main.py
```

The web dashboard will be available at: **http://localhost:5003**

## 🎯 Trading Strategies

### Moving Average Crossover Strategy

The bot implements two complementary strategies:

1. **SMA Crossover (Primary)**:
   - Short SMA: 9 periods
   - Long SMA: 10 periods
   - Golden Cross: Buy signal when short SMA crosses above long SMA
   - Death Cross: Sell signal when short SMA crosses below long SMA

2. **EMA Crossover (Secondary)**:
   - Short EMA: 9 periods
   - Long EMA: 10 periods
   - Used as confirmation for SMA signals

### Risk Management

- **Position Sizing**: Automatic position size calculation based on account balance
- **Stop Loss**: 2% stop loss on all positions
- **Take Profit**: 4% take profit target
- **Daily Loss Limit**: 5% maximum daily loss
- **Signal Cooldown**: 5-minute cooldown between signals

## 🌐 Web Dashboard Features

### Real-time Monitoring
- **Bot Status**: Running/Stopped indicator
- **Current Price**: Live price updates
- **Position Info**: Current position details and P&L
- **Trading Signals**: SMA and EMA signal indicators

### Manual Controls
- **Start/Stop Bot**: Control automated trading
- **Manual Trading**: Buy/Sell buttons for immediate execution
- **Close Position**: Close current position manually
- **Symbol Selection**: Choose trading pair

### Live Charts
- **Price Chart**: Real-time price visualization
- **Signal Indicators**: Visual signal representation
- **Trading Logs**: Comprehensive activity logging

## 🔧 API Endpoints

### Bot Control
- `POST /api/start` - Start the trading bot
- `POST /api/stop` - Stop the trading bot
- `GET /api/status` - Get current bot status

### Trading Operations
- `POST /api/manual-trade` - Execute manual trade
- `POST /api/close-position` - Close current position
- `GET /api/positions` - Get current positions
- `GET /api/orders` - Get current orders

### WebSocket Events
- `status_update` - Real-time status updates
- `trade_executed` - Trade execution notifications
- `bot_error` - Error notifications
- `bot_stopped` - Bot stop notifications

## ⚙️ Configuration

### Environment Variables

```env
# API Credentials
DELTA_API_KEY=your_api_key
DELTA_API_SECRET=your_api_secret

# Trading Configuration
TRADING_SYMBOL=BTCUSD

# Risk Management
MAX_POSITION_SIZE=10
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.04
MAX_DAILY_LOSS=0.05

# Strategy Parameters
SHORT_MA_PERIOD=9
LONG_MA_PERIOD=10
EMA_SHORT_PERIOD=9
EMA_LONG_PERIOD=10
CANDLE_RESOLUTION=1h
LOOKBACK_HOURS=24
```

### Supported Trading Symbols

- BTCUSD (Bitcoin)
- ETHUSD (Ethereum)
- BNBUSD (Binance Coin)
- ADAUSD (Cardano)
- SOLUSD (Solana)

## 🛡️ Security Features

- **API Key Protection**: Secure credential storage
- **Input Validation**: All inputs are validated
- **Error Handling**: Comprehensive error handling
- **Rate Limiting**: Built-in API rate limiting
- **Position Limits**: Maximum position size controls

## 📊 Technical Details

### Backend (Flask)
- **Framework**: Flask with SocketIO
- **Real-time**: WebSocket support for live updates
- **API**: RESTful API endpoints
- **Logging**: Comprehensive logging system

### Frontend (HTML/CSS/JavaScript)
- **UI**: Modern, responsive design
- **Charts**: Chart.js for price visualization
- **WebSocket**: Real-time data updates
- **Mobile**: Mobile-responsive interface

### Trading Engine
- **Strategy**: Moving average crossover
- **Data**: Real-time price feeds
- **Execution**: Market order execution
- **Risk**: Built-in risk management

## 🚨 Important Notes

### ⚠️ Risk Warning
- **High Risk**: Cryptocurrency trading involves significant risk
- **Test First**: Always test with small amounts first
- **Monitor**: Continuously monitor your positions
- **API Limits**: Be aware of exchange API rate limits

### 🔒 Security Best Practices
- **API Keys**: Never share your API credentials
- **Environment**: Use environment variables for sensitive data
- **Network**: Use secure networks when trading
- **Updates**: Keep the application updated

## 🐛 Troubleshooting

### Common Issues

1. **Bot won't start**:
   - Check API credentials in `.env` file
   - Verify internet connection
   - Check Delta Exchange API status

2. **No signals generated**:
   - Ensure sufficient historical data
   - Check moving average periods
   - Verify symbol is supported

3. **WebSocket connection issues**:
   - Check firewall settings
   - Verify port 5003 is available
   - Try refreshing the browser

### Logs
- Check `trading_bot.log` for detailed logs
- Web dashboard shows real-time logs
- Console output for immediate feedback

## 📈 Performance Optimization

- **Data Caching**: Efficient price data management
- **Signal Cooldown**: Prevents overtrading
- **Position Sizing**: Optimized position calculations
- **Memory Management**: Limited data retention

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Check Delta Exchange documentation
4. Create an issue in the repository

---

**⚠️ Disclaimer**: This software is for educational purposes only. Cryptocurrency trading involves significant risk. Always test with small amounts and never trade with money you cannot afford to lose.
