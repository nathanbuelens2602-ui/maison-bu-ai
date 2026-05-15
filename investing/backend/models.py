from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date


class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str
    name: str
    quantity: float
    avg_cost: float
    currency: str = "EUR"
    asset_type: str = "ETF"
    target_allocation: float = 0.0
    notes: str = ""
    added_date: str = ""


class DCASettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monthly_amount: float
    day_of_month: int
    enabled: bool = True
    last_reminder: Optional[str] = None


class HoldingCreate(SQLModel):
    ticker: str
    name: str
    quantity: float
    avg_cost: float
    currency: str = "EUR"
    asset_type: str = "ETF"
    target_allocation: float = 0.0
    notes: str = ""


class HoldingUpdate(SQLModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[float] = None
    avg_cost: Optional[float] = None
    currency: Optional[str] = None
    asset_type: Optional[str] = None
    target_allocation: Optional[float] = None
    notes: Optional[str] = None


class HoldingWithMetrics(SQLModel):
    id: Optional[int]
    ticker: str
    name: str
    quantity: float
    avg_cost: float
    currency: str
    asset_type: str
    target_allocation: float
    notes: str
    added_date: str
    current_price: float
    current_value: float
    cost_basis: float
    pnl: float
    pnl_pct: float
    actual_allocation: float


class PortfolioSummary(SQLModel):
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float
    holdings: list[HoldingWithMetrics]
    last_updated: str


class RebalanceSuggestion(SQLModel):
    ticker: str
    name: str
    current_pct: float
    target_pct: float
    diff_pct: float
    action: str  # "BUY" or "HOLD"
    suggested_amount: float
    reason: str
