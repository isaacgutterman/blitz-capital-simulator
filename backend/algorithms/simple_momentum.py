import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any
from algorithms.base_algorithm import BaseAlgorithm
from models.portfolio import Portfolio

class SimpleMomentumStrategy(BaseAlgorithm):
    """Simple momentum strategy based on price changes"""
    
    def __init__(self):
        super().__init__()
        self.parameters = {
            'lookback_period': 20,
            'threshold': 0.02,  # 2% price change threshold
            'position_size': 0.1  # 10% of portfolio per position
        }
    
    def generate_signals(self, timestamp: datetime, data: Dict[str, pd.DataFrame], 
                        portfolio: Portfolio) -> Dict[str, Dict[str, Any]]:
        """Generate momentum-based trading signals"""
        signals = {}
        
        if not self.validate_data(data):
            return signals
        
        for symbol, df in data.items():
            if len(df) < self.parameters['lookback_period']:
                continue
            
            try:
                # Calculate momentum
                current_price = df['close'].iloc[-1]
                past_price = df['close'].iloc[-self.parameters['lookback_period']]
                momentum = (current_price - past_price) / past_price
                
                # Calculate position size
                portfolio_value = portfolio.total_value
                position_value = portfolio_value * self.parameters['position_size']
                quantity = position_value / current_price
                
                # Generate signal
                if momentum > self.parameters['threshold']:
                    # Positive momentum - buy signal
                    signals[symbol] = {
                        'action': 'buy',
                        'quantity': quantity,
                        'reason': f'Momentum: {momentum:.3f}'
                    }
                elif momentum < -self.parameters['threshold']:
                    # Negative momentum - sell signal
                    current_position = portfolio.positions.get(symbol, 0)
                    signals[symbol] = {
                        'action': 'sell',
                        'quantity': min(quantity, current_position),
                        'reason': f'Momentum: {momentum:.3f}'
                    }
                else:
                    # No signal
                    signals[symbol] = {
                        'action': 'hold',
                        'quantity': 0,
                        'reason': f'Momentum: {momentum:.3f}'
                    }
                    
            except Exception as e:
                print(f"Error generating momentum signal for {symbol}: {e}")
                signals[symbol] = {'action': 'hold', 'quantity': 0, 'reason': 'Error'}
        
        return signals
