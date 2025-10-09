import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from algorithms.base_algorithm import BaseAlgorithm
from algorithms.simple_momentum import SimpleMomentumStrategy
from models.portfolio import Portfolio, Trade, PerformanceMetrics
from data.crypto_data import CryptoDataProvider

class HistoricalSimulator:
    def __init__(self, simulation_id: str, algorithm_name: str, initial_capital: float, 
                 start_date: str, end_date: str, symbols: List[str]):
        self.simulation_id = simulation_id
        self.algorithm_name = algorithm_name
        self.initial_capital = initial_capital
        self.start_date = start_date
        self.end_date = end_date
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
        
        # Data provider
        self.data_provider = CryptoDataProvider()
        
        # Initialize algorithm
        self.algorithm = self._create_algorithm()
        
        # Performance tracking
        self.peak_value = initial_capital
        self.max_drawdown = 0.0
        
        # Benchmark tracking for alpha analysis
        self.benchmark_values = []
        self.benchmark_returns = []
        self.last_benchmark_date = None
        
    def reset_benchmark(self):
        """Reset benchmark tracking for new simulation"""
        self.benchmark_values = []
        self.benchmark_returns = []
        self.last_benchmark_date = None
    
    def reset_simulation(self):
        """Reset all simulation state for a fresh start"""
        # Reset portfolio
        self.portfolio = Portfolio(self.initial_capital)
        
        # Reset tracking
        self.trades = []
        self.portfolio_history = []
        self.peak_value = self.initial_capital
        self.max_drawdown = 0.0
        
        # Reset benchmark
        self.reset_benchmark()
        
        # Recreate algorithm
        self.algorithm = self._create_algorithm()
        
        print(f"Reset simulation state for {self.simulation_id}")
        
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
        """Run the historical simulation"""
        print(f"Starting historical simulation {self.simulation_id}")
        
        # Reset all simulation state for fresh start
        self.reset_simulation()
        
        print(f"Simulator state after reset: portfolio_value={self.portfolio.total_value}, trades_count={len(self.trades)}")
        
        try:
            
            # Get historical data for all symbols
            historical_data = {}
            for symbol in self.symbols:
                print(f"Fetching data for {symbol}...")
                data = await self.data_provider.get_historical_data(
                    symbol, self.start_date, self.end_date
                )
                if not data.empty:
                    # Calculate technical indicators
                    data = self.data_provider.calculate_technical_indicators(data)
                    historical_data[symbol] = data
                else:
                    print(f"No data found for {symbol}")
            
            if not historical_data:
                raise ValueError("No historical data available for any symbol")
            
            # Find common date range
            min_date = max(df.index.min() for df in historical_data.values())
            max_date = min(df.index.max() for df in historical_data.values())
            
            print(f"Simulating from {min_date} to {max_date}")
            
            # Run simulation day by day
            current_date = min_date
            while current_date <= max_date:
                await self._process_day(current_date, historical_data)
                current_date += timedelta(hours=1)  # Process hourly
                
                # Calculate benchmark performance (equal weight portfolio)
                benchmark_value = self._calculate_benchmark_value(current_date, historical_data)
                self.benchmark_values.append(benchmark_value)
                
                # Store portfolio state
                self.portfolio_history.append({
                    'timestamp': current_date,
                    'total_value': self.portfolio.total_value,
                    'cash': self.portfolio.cash,
                    'positions': self.portfolio.positions.copy(),
                    'unrealized_pnl': self.portfolio.unrealized_pnl,
                    'realized_pnl': self.portfolio.realized_pnl,
                    'benchmark_value': benchmark_value
                })
            
            print(f"Historical simulation completed. Final portfolio value: ${self.portfolio.total_value:.2f}")
            
        except Exception as e:
            print(f"Error in historical simulation: {e}")
            # Status will be updated by the main.py handler
            raise
    
    def _calculate_benchmark_value(self, current_date: datetime, historical_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate benchmark value (equal weight portfolio)"""
        try:
            if not self.benchmark_values:
                # First day - initialize with equal weights
                self.last_benchmark_date = current_date
                return self.initial_capital
            
            # Get previous benchmark value
            prev_benchmark = self.benchmark_values[-1]
            
            # Calculate returns for each symbol
            total_return = 0
            valid_symbols = 0
            
            for symbol in self.symbols:
                if symbol in historical_data and current_date in historical_data[symbol].index:
                    try:
                        # Get current price
                        current_price = historical_data[symbol].loc[current_date, 'close']
                        
                        # Find previous price using last_benchmark_date
                        if self.last_benchmark_date and self.last_benchmark_date in historical_data[symbol].index:
                            prev_price = historical_data[symbol].loc[self.last_benchmark_date, 'close']
                            if prev_price > 0:
                                symbol_return = (current_price - prev_price) / prev_price
                                total_return += symbol_return
                                valid_symbols += 1
                    except Exception as e:
                        print(f"Error calculating benchmark for {symbol}: {e}")
                        continue
            
            # Update last benchmark date
            self.last_benchmark_date = current_date
            
            if valid_symbols > 0:
                # Equal weight portfolio return
                avg_return = total_return / valid_symbols
                new_benchmark = prev_benchmark * (1 + avg_return)
                return new_benchmark
            else:
                return prev_benchmark
                
        except Exception as e:
            print(f"Error calculating benchmark: {e}")
            return self.benchmark_values[-1] if self.benchmark_values else self.initial_capital
    
    async def _process_day(self, current_date: datetime, historical_data: Dict[str, pd.DataFrame]):
        """Process a single day of the simulation"""
        # Get current prices for all symbols
        current_prices = {}
        for symbol, data in historical_data.items():
            if current_date in data.index:
                current_prices[symbol] = data.loc[current_date, 'close']
        
        # Update portfolio value
        self._update_portfolio_value(current_prices)
        
        # Get algorithm signals
        signals = self.algorithm.generate_signals(current_date, historical_data, self.portfolio)
        
        # Execute trades based on signals
        for symbol, signal in signals.items():
            if symbol in current_prices:
                await self._execute_trade(symbol, signal, current_prices[symbol], current_date)
    
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
            # Handle division by zero and invalid values
            daily_returns = []
            for i in range(1, len(portfolio_values)):
                if portfolio_values[i-1] != 0:
                    daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                    if not np.isnan(daily_return) and not np.isinf(daily_return):
                        daily_returns.append(daily_return)
            
            if daily_returns:
                avg_daily_return = np.mean(daily_returns)
                volatility = np.std(daily_returns)
                sharpe_ratio = avg_daily_return / volatility if volatility > 0 else 0
            else:
                avg_daily_return = 0
                volatility = 0
                sharpe_ratio = 0
        else:
            avg_daily_return = 0
            volatility = 0
            sharpe_ratio = 0
        
        # Win rate
        winning_trades = [t for t in self.trades if self._is_winning_trade(t)]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        # Alpha analysis
        alpha_metrics = self._calculate_alpha_metrics()
        
        # Ensure all values are finite and JSON-serializable
        def safe_float(value):
            if np.isnan(value) or np.isinf(value):
                return 0.0
            return float(value)
        
        return {
            'total_return': safe_float(total_return),
            'daily_return': safe_float(avg_daily_return),
            'sharpe_ratio': safe_float(sharpe_ratio),
            'max_drawdown': safe_float(self.max_drawdown),
            'win_rate': safe_float(win_rate),
            'volatility': safe_float(volatility),
            'total_trades': len(self.trades),
            **alpha_metrics  # Add alpha metrics
        }
    
    def _calculate_alpha_metrics(self) -> Dict[str, float]:
        """Calculate alpha and benchmark comparison metrics"""
        try:
            if len(self.portfolio_history) < 2 or len(self.benchmark_values) < 2:
                print(f"Not enough data for alpha calculation: portfolio={len(self.portfolio_history)}, benchmark={len(self.benchmark_values)}")
                return {
                    'benchmark_return': 0.0,
                    'alpha': 0.0,
                    'beta': 0.0,
                    'excess_return': 0.0,
                    'information_ratio': 0.0,
                    'tracking_error': 0.0
                }
            
            # Calculate portfolio and benchmark returns
            portfolio_values = [p['total_value'] for p in self.portfolio_history]
            portfolio_returns = []
            benchmark_returns = []
            
            for i in range(1, len(portfolio_values)):
                if portfolio_values[i-1] != 0 and self.benchmark_values[i-1] != 0:
                    port_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                    bench_return = (self.benchmark_values[i] - self.benchmark_values[i-1]) / self.benchmark_values[i-1]
                    
                    if not np.isnan(port_return) and not np.isnan(bench_return):
                        portfolio_returns.append(port_return)
                        benchmark_returns.append(bench_return)
            
            if len(portfolio_returns) < 2:
                return {
                    'benchmark_return': 0.0,
                    'alpha': 0.0,
                    'beta': 0.0,
                    'excess_return': 0.0,
                    'information_ratio': 0.0,
                    'tracking_error': 0.0
                }
            
            # Calculate metrics
            portfolio_returns = np.array(portfolio_returns)
            benchmark_returns = np.array(benchmark_returns)
            
            # Total returns
            total_portfolio_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
            total_benchmark_return = (self.benchmark_values[-1] - self.benchmark_values[0]) / self.benchmark_values[0]
            
            # Alpha and Beta (CAPM model)
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            alpha = np.mean(portfolio_returns) - beta * np.mean(benchmark_returns)
            
            # Excess return
            excess_return = total_portfolio_return - total_benchmark_return
            
            # Tracking error and Information Ratio
            excess_returns = portfolio_returns - benchmark_returns
            tracking_error = np.std(excess_returns)
            information_ratio = np.mean(excess_returns) / tracking_error if tracking_error > 0 else 0
            
            return {
                'benchmark_return': float(total_benchmark_return),
                'alpha': float(alpha),
                'beta': float(beta),
                'excess_return': float(excess_return),
                'information_ratio': float(information_ratio),
                'tracking_error': float(tracking_error)
            }
            
        except Exception as e:
            print(f"Error calculating alpha metrics: {e}")
            return {
                'benchmark_return': 0.0,
                'alpha': 0.0,
                'beta': 0.0,
                'excess_return': 0.0,
                'information_ratio': 0.0,
                'tracking_error': 0.0
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
