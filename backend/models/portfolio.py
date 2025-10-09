from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class Portfolio(BaseModel):
    total_value: float
    cash: float
    positions: Dict[str, float] = {}  # symbol -> quantity
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: datetime = None
    
    def __init__(self, initial_capital: float = 10000, **data):
        if not data:
            data = {
                'total_value': initial_capital,
                'cash': initial_capital,
                'positions': {},
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0,
                'timestamp': datetime.now()
            }
        super().__init__(**data)

class Trade(BaseModel):
    timestamp: datetime
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    price: float
    value: float
    algorithm: str
    commission: float = 0.0

class PerformanceMetrics(BaseModel):
    total_return: float
    daily_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    volatility: float
    alpha: float
    beta: float
