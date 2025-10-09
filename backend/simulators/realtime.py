import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from algorithms.base_algorithm import BaseAlgorithm
from algorithms.simple_momentum import SimpleMomentumStrategy
from models.portfolio import Portfolio, Trade, PerformanceMetrics
from data.crypto_data import CryptoDataProvider

class RealtimeSimulator:
    def __init__(self, simulation_id: str, algorithm_name: str, initial_capital: float, symbols: List[str]):
        self.simulation_id = simulation_id
        self.algorithm_name = algorithm_name
        self.initial_capital = initial_capital
        self.symbols = symbols
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            total_value=initial_capital,
            cash=initial_capital,
            positions={},
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            timestamp=datetime.now()
        )
        
        # Trading history
        self.trades = []
        self.portfolio_history = []
        self.price_history = {symbol: [] for symbol in symbols}
        
        # Data provider
        self.data_provider = CryptoDataProvider()
        
        # Initialize algorithm
        self.algorithm = self._create_algorithm()
        
        # Performance tracking
        self.peak_value = initial_capital
        self.max_drawdown = 0.0
        self.is_running = False
        
        # Real-time data storage
        self.current_prices = {}
        self.historical_data_cache = {}
        
    def _create_algorithm(self) -> BaseAlgorithm:
        """Create algorithm instance based on name"""
        algorithm_map = {
            'SimpleMomentumStrategy': SimpleMomentumStrategy
        }
        
        algorithm_class = algorithm_map.get(self.algorithm_name)
        if not algorithm_class:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
        
        return algorithm_class()
    
    async def run(self):
        """Run the real-time simulation"""
        print(f"Starting real-time simulation {self.simulation_id}")
        self.is_running = True
        
        try:
            # Initialize with some historical data for technical indicators
            await self._initialize_historical_data()
            
            # Start real-time data streaming
            await self.data_provider.stream_realtime_data(
                self.symbols, 
                self._process_realtime_update
            )
            
        except Exception as e:
            print(f"Error in real-time simulation: {e}")
            self.is_running = False
            raise
    
    async def _initialize_historical_data(self):
        """Initialize with historical data for technical indicators"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        for symbol in self.symbols:
            try:
                data = await self.data_provider.get_historical_data(symbol, start_date, end_date)
                if not data.empty:
                    data = self.data_provider.calculate_technical_indicators(data)
                    self.historical_data_cache[symbol] = data
                    print(f"Initialized historical data for {symbol}")
            except Exception as e:
                print(f"Error initializing data for {symbol}: {e}")
    
    async def _process_realtime_update(self, prices: Dict[str, float]):
        """Process real-time price updates"""
        if not self.is_running:
            return
        
        self.current_prices = prices
        current_time = datetime.now()
        
        # Update price history
        for symbol, price in prices.items():
            if symbol in self.price_history:
                self.price_history[symbol].append({
                    'timestamp': current_time,
                    'price': price
                })
                
                # Keep only last 1000 data points
                if len(self.price_history[symbol]) > 1000:
                    self.price_history[symbol] = self.price_history[symbol][-1000:]
        
        # Update portfolio value
        self._update_portfolio_value(prices)
        
        # Update historical data cache with new price
        await self._update_historical_cache(current_time, prices)
        
        # Generate trading signals
        signals = await self._generate_signals(current_time)
        
        # Execute trades
        for symbol, signal in signals.items():
            if symbol in prices:
                await self._execute_trade(symbol, signal, prices[symbol], current_time)
        
        # Store portfolio state
        self.portfolio_history.append({
            'timestamp': current_time,
            'total_value': self.portfolio.total_value,
            'cash': self.portfolio.cash,
            'positions': self.portfolio.positions.copy(),
            'unrealized_pnl': self.portfolio.unrealized_pnl,
            'realized_pnl': self.portfolio.realized_pnl
        })
        
        # Keep only last 1000 portfolio states
        if len(self.portfolio_history) > 1000:
            self.portfolio_history = self.portfolio_history[-1000:]
    
    async def _update_historical_cache(self, timestamp: datetime, prices: Dict[str, float]):
        """Update historical data cache with new price data"""
        for symbol, price in prices.items():
            if symbol in self.historical_data_cache:
                # Add new row to the dataframe
                new_row = pd.DataFrame({
                    'open': [price],
                    'high': [price],
                    'low': [price],
                    'close': [price],
                    'volume': [0]  # Real-time data doesn't have volume
                }, index=[timestamp])
                
                # Append to existing data
                self.historical_data_cache[symbol] = pd.concat([
                    self.historical_data_cache[symbol], 
                    new_row
                ])
                
                # Keep only last 1000 rows
                if len(self.historical_data_cache[symbol]) > 1000:
                    self.historical_data_cache[symbol] = self.historical_data_cache[symbol].tail(1000)
                
                # Recalculate technical indicators
                self.historical_data_cache[symbol] = self.data_provider.calculate_technical_indicators(
                    self.historical_data_cache[symbol]
                )
    
    async def _generate_signals(self, timestamp: datetime) -> Dict[str, Dict[str, Any]]:
        """Generate trading signals from algorithm"""
        try:
            return self.algorithm.generate_signals(timestamp, self.historical_data_cache, self.portfolio)
        except Exception as e:
            print(f"Error generating signals: {e}")
            return {}
    
    def _update_portfolio_value(self, current_prices: Dict[str, float]):
        """Update portfolio value based on current prices"""
        total_value = self.portfolio.cash
        
        for symbol, quantity in self.portfolio.positions.items():
            if symbol in current_prices:
                position_value = quantity * current_prices[symbol]
                total_value += position_value
        
        self.portfolio.total_value = total_value
        
        # Update peak value and max drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        
        current_drawdown = (self.peak_value - total_value) / self.peak_value
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
    
    async def _execute_trade(self, symbol: str, signal: Dict[str, Any], price: float, timestamp: datetime):
        """Execute a trade based on algorithm signal"""
        if signal['action'] == 'buy' and signal['quantity'] > 0:
            # Calculate how much we can buy
            available_cash = self.portfolio.cash
            max_quantity = available_cash / price
            
            quantity = min(signal['quantity'], max_quantity)
            cost = quantity * price
            
            if cost <= available_cash:
                # Execute buy order
                self.portfolio.cash -= cost
                if symbol not in self.portfolio.positions:
                    self.portfolio.positions[symbol] = 0
                self.portfolio.positions[symbol] += quantity
                
                # Record trade
                trade = Trade(
                    timestamp=timestamp,
                    symbol=symbol,
                    side='buy',
                    quantity=quantity,
                    price=price,
                    value=cost,
                    algorithm=self.algorithm_name
                )
                self.trades.append(trade)
                print(f"BUY: {quantity} {symbol} at ${price:.2f}")
        
        elif signal['action'] == 'sell' and signal['quantity'] > 0:
            # Calculate how much we can sell
            available_quantity = self.portfolio.positions.get(symbol, 0)
            quantity = min(signal['quantity'], available_quantity)
            
            if quantity > 0:
                # Execute sell order
                proceeds = quantity * price
                self.portfolio.cash += proceeds
                self.portfolio.positions[symbol] -= quantity
                
                # Record trade
                trade = Trade(
                    timestamp=timestamp,
                    symbol=symbol,
                    side='sell',
                    quantity=quantity,
                    price=price,
                    value=proceeds,
                    algorithm=self.algorithm_name
                )
                self.trades.append(trade)
                print(f"SELL: {quantity} {symbol} at ${price:.2f}")
    
    def stop(self):
        """Stop the real-time simulation"""
        self.is_running = False
        print(f"Stopped real-time simulation {self.simulation_id}")
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio state"""
        return {
            'total_value': self.portfolio.total_value,
            'cash': self.portfolio.cash,
            'positions': self.portfolio.positions,
            'unrealized_pnl': self.portfolio.unrealized_pnl,
            'realized_pnl': self.portfolio.realized_pnl,
            'timestamp': self.portfolio.timestamp.isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.portfolio_history:
            return {}
        
        # Calculate returns
        initial_value = self.initial_capital
        final_value = self.portfolio.total_value
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate daily returns
        portfolio_values = [p['total_value'] for p in self.portfolio_history]
        if len(portfolio_values) > 1:
            daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
            avg_daily_return = np.mean(daily_returns)
            volatility = np.std(daily_returns)
            sharpe_ratio = avg_daily_return / volatility if volatility > 0 else 0
        else:
            avg_daily_return = 0
            volatility = 0
            sharpe_ratio = 0
        
        # Win rate
        winning_trades = [t for t in self.trades if self._is_winning_trade(t)]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        return {
            'total_return': total_return,
            'daily_return': avg_daily_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': win_rate,
            'volatility': volatility,
            'total_trades': len(self.trades),
            'is_running': self.is_running
        }
    
    def _is_winning_trade(self, trade: Trade) -> bool:
        """Determine if a trade was profitable"""
        # This is a simplified version - in reality you'd track entry/exit pairs
        return trade.side == 'sell'  # Simplified logic
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades"""
        recent_trades = self.trades[-limit:] if self.trades else []
        return [
            {
                'timestamp': trade.timestamp.isoformat(),
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'value': trade.value,
                'algorithm': trade.algorithm
            }
            for trade in recent_trades
        ]
    
    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """Get portfolio history for charting"""
        return self.portfolio_history
    
    def get_price_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get price history for all symbols"""
        return {
            symbol: [
                {
                    'timestamp': point['timestamp'].isoformat(),
                    'price': point['price']
                }
                for point in history
            ]
            for symbol, history in self.price_history.items()
        }
