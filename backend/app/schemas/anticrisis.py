from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class BalanceCreate(BaseModel):
    noncurrent_assets: float = 0
    current_assets: float = 0
    equity: float = 0
    long_term_liabilities: float = 0
    short_term_liabilities: float = 0
    receivables: float = 0
    payables: float = 0
    cash: float = 0


class BDRCreate(BaseModel):
    revenue: float = 0
    cost_of_sales: float = 0
    operating_expenses: float = 0
    other_income: float = 0
    other_expenses: float = 0


class BDDSCreate(BaseModel):
    cash_begin: float = 0
    inflows_operating: float = 0
    inflows_investing: float = 0
    inflows_financing: float = 0
    outflows_operating: float = 0
    outflows_investing: float = 0
    outflows_financing: float = 0
    cash_end: float = 0


class PeriodCreate(BaseModel):
    period_type: str = "month"
    period_start: datetime
    period_end: datetime
    label: str = ""


class PeriodResponse(BaseModel):
    id: int
    organization_id: int
    period_type: str
    period_start: datetime
    period_end: datetime
    label: str

    class Config:
        from_attributes = True


class CoefficientsResponse(BaseModel):
    current_ratio: float
    quick_ratio: float
    absolute_liquidity: float
    autonomy: float
    debt_to_equity: float
    roa: float
    roe: float
    profit_margin: float


class CrisisClassification(BaseModel):
    crisis_type_code: str
    crisis_type_name: str
    confidence: float
    reasoning: str


class PlanItemCreate(BaseModel):
    title: str
    stage: str = ""
    due_date: Optional[date] = None
    status: str = "not_started"


class PlanItemResponse(BaseModel):
    id: int
    plan_id: int
    title: str
    stage: str
    due_date: Optional[date] = None
    status: str
    completed: bool
    sort_order: int

    class Config:
        from_attributes = True


class PlanCreate(BaseModel):
    crisis_type_code: str = ""
    title: str
    items: list[PlanItemCreate] = []


class PlanResponse(BaseModel):
    id: int
    organization_id: int
    crisis_type_code: str
    title: str
    created_at: datetime
    items: list[PlanItemResponse] = []

    class Config:
        from_attributes = True


class PlanItemUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[date] = None
