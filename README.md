# 🚀 Blitz Capital Hedge Fund Simulation System

A comprehensive platform for testing crypto trading algorithms with both historical backtesting and real-time simulation capabilities.

## 🎯 Features

- **📊 Historical Simulation**: Backtest algorithms using past year crypto data
- **⚡ Real-time Simulation**: Run algorithms live with fake money on real crypto markets
- **🤖 Algorithm Framework**: Easy-to-use framework for implementing trading strategies
- **📈 Performance Analytics**: Comprehensive portfolio tracking and performance metrics
- **🎨 Modern Dashboard**: Beautiful React frontend for monitoring simulations
- **🔌 Real-time Updates**: WebSocket connections for live data streaming

## 🏗️ Project Structure
```
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app entry point
│   ├── simulators/         # Market simulators
│   │   ├── historical.py   # Historical data simulator
│   │   └── realtime.py     # Real-time data simulator
│   ├── algorithms/         # Trading algorithms
│   │   ├── base_algorithm.py
│   │   ├── simple_momentum.py
│   │   ├── mean_reversion.py
│   │   └── rsi_strategy.py
│   ├── data/              # Data fetching and processing
│   │   └── crypto_data.py
│   └── models/            # Pydantic models
│       ├── simulation.py
│       └── portfolio.py
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json
├── requirements.txt       # Python dependencies
├── start.sh             # Linux/Mac startup script
└── start.bat            # Windows startup script
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**For Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**For Windows:**
```cmd
start.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies
   cd frontend
   npm install
   cd ..
   ```

2. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```

3. **Start Frontend** (in new terminal)
   ```bash
   cd frontend
   npm start
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Available Algorithm

### Simple Momentum Strategy
- **Description**: Trades based on price momentum over a lookback period
- **Parameters**: 
  - `lookback_period`: Number of periods to look back (default: 20)
  - `threshold`: Minimum momentum threshold (default: 0.02)
  - `position_size`: Percentage of portfolio per position (default: 0.1)


## 🔌 API Endpoints

### Simulations
- `GET /api/simulations` - List all simulations
- `POST /api/simulations/historical` - Start historical simulation
- `POST /api/simulations/realtime` - Start real-time simulation
- `GET /api/simulations/{id}/status` - Get simulation status
- `GET /api/simulations/{id}/portfolio` - Get portfolio data

### Algorithms
- `GET /api/algorithms` - List available algorithms

### WebSocket
- `WS /ws/{simulation_id}` - Real-time simulation updates

## 📈 Supported Cryptocurrencies

The system supports major crypto pairs including:
- BTC/USDT, ETH/USDT, BNB/USDT
- ADA/USDT, SOL/USDT, XRP/USDT
- DOT/USDT, DOGE/USDT, AVAX/USDT
- MATIC/USDT, and more...

## 🛠️ Customizing Algorithms

To create your own trading algorithm:

1. Create a new file in `backend/algorithms/`
2. Inherit from `BaseAlgorithm`
3. Implement the `generate_signals` method
4. Add your algorithm to the algorithm map in the simulators

Example:
```python
from algorithms.base_algorithm import BaseAlgorithm

class MyCustomStrategy(BaseAlgorithm):
    def generate_signals(self, timestamp, data, portfolio):
        # Your trading logic here
        return signals
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```
API_HOST=0.0.0.0
API_PORT=8000
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
```

### Frontend Configuration
The frontend automatically connects to `http://localhost:8000`. To change this, update the `API_BASE_URL` in `frontend/src/services/api.js`.

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:
- **Total Return**: Overall portfolio performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Volatility**: Standard deviation of returns
- **Alpha/Beta**: Risk metrics vs benchmark

## 🚨 Important Notes

- **Paper Trading Only**: This system uses fake money for all simulations
- **API Rate Limits**: Be mindful of exchange API rate limits
- **Data Accuracy**: Historical data quality depends on the data source
- **Risk Management**: Always implement proper risk management in your algorithms

