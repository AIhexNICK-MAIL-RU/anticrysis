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


class FinModelResponse(BaseModel):
    """Результаты финансовой модели (расчёты по балансу, БДР, БДДС)."""
    total_assets: float
    total_liabilities: float
    equity_ratio: float
    profit: float
    profit_margin: float
    gross_profit: float
    gross_margin: float
    break_even_revenue: float
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float
    net_cash_flow: float
    cash_end_calculated: float


class PeriodTableResponse(BaseModel):
    """Данные для расчётной таблицы по периоду: баланс, БДР, БДДС, коэффициенты, кризис, фин. модель."""
    period: PeriodResponse
    balance: dict  # ББЛ
    bdr: dict
    bdds: dict
    coefficients: CoefficientsResponse
    crisis: CrisisClassification
    fin_model: FinModelResponse | None = None


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
