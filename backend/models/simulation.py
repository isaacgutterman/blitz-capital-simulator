from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SimulationType(str, Enum):
    HISTORICAL = "historical"
    REALTIME = "realtime"

class SimulationRequest(BaseModel):
    algorithm_name: str
    initial_capital: float
    symbols: List[str]
    start_date: Optional[str] = None  # For historical simulations
    end_date: Optional[str] = None    # For historical simulations

class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    message: str

class SimulationStatus(BaseModel):
    simulation_id: str
    status: str
    portfolio: Dict[str, Any]
    performance: Dict[str, Any]
    trades: List[Dict[str, Any]]

class Portfolio(BaseModel):
    total_value: float
    cash: float
    positions: Dict[str, float]  # symbol -> quantity
    unrealized_pnl: float
    realized_pnl: float

class Trade(BaseModel):
    timestamp: datetime
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    price: float
    value: float
    algorithm: str

class PerformanceMetrics(BaseModel):
    total_return: float
    daily_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float

class AlgorithmConfig(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
