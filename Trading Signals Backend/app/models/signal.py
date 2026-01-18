from pydantic import BaseModel
from typing import List, Optional


class Signal(BaseModel):
    symbol: str
    action: str  # "BUY" or "SELL"
    price: float
    target: float
    stoploss: float
    timestamp: str


class SignalsResponse(BaseModel):
    signals: List[Signal]
    total: int
    is_paid: bool
    cached: bool
    message: Optional[str]