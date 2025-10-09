from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from models.portfolio import Portfolio

class BaseAlgorithm(ABC):
    """Base class for all trading algorithms"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.parameters = {}
    
    @abstractmethod
    def generate_signals(self, timestamp: datetime, data: Dict[str, pd.DataFrame], 
                        portfolio: Portfolio) -> Dict[str, Dict[str, Any]]:
        """
        Generate trading signals for all symbols
        
        Args:
            timestamp: Current timestamp
            data: Dictionary of symbol -> DataFrame with OHLCV data
            portfolio: Current portfolio state
            
        Returns:
            Dictionary of symbol -> signal dict with 'action' and 'quantity'
        """
        pass
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set algorithm parameters"""
        self.parameters.update(parameters)
    
    def get_parameter(self, key: str, default: Any = None):
        """Get algorithm parameter"""
        return self.parameters.get(key, default)
    
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """Validate that data is sufficient for algorithm"""
        for symbol, df in data.items():
            if df.empty or len(df) < 20:  # Need at least 20 data points
                return False
        return True
