from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base


class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    period_type: Mapped[str] = mapped_column(String(20), default="month")  # month, quarter, year
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    label: Mapped[str] = mapped_column(String(100), default="")  # e.g. "Январь 2026"

    organization: Mapped["Organization"] = relationship("Organization", back_populates="periods")
    balance: Mapped["Balance"] = relationship(back_populates="period", uselist=False, cascade="all, delete-orphan")
    bdr: Mapped["BDR"] = relationship(back_populates="period", uselist=False, cascade="all, delete-orphan")
    bdds: Mapped["BDDS"] = relationship(back_populates="period", uselist=False, cascade="all, delete-orphan")
    coefficients: Mapped["Coefficients"] = relationship(back_populates="period", uselist=False, cascade="all, delete-orphan")


class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"), unique=True)

    noncurrent_assets: Mapped[float] = mapped_column(Float, default=0)
    current_assets: Mapped[float] = mapped_column(Float, default=0)
    equity: Mapped[float] = mapped_column(Float, default=0)
    long_term_liabilities: Mapped[float] = mapped_column(Float, default=0)
    short_term_liabilities: Mapped[float] = mapped_column(Float, default=0)
    receivables: Mapped[float] = mapped_column(Float, default=0)
    payables: Mapped[float] = mapped_column(Float, default=0)
    cash: Mapped[float] = mapped_column(Float, default=0)

    period: Mapped["Period"] = relationship(back_populates="balance")


class BDR(Base):
    __tablename__ = "bdr"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"), unique=True)

    revenue: Mapped[float] = mapped_column(Float, default=0)
    cost_of_sales: Mapped[float] = mapped_column(Float, default=0)
    operating_expenses: Mapped[float] = mapped_column(Float, default=0)
    other_income: Mapped[float] = mapped_column(Float, default=0)
    other_expenses: Mapped[float] = mapped_column(Float, default=0)

    period: Mapped["Period"] = relationship(back_populates="bdr")


class BDDS(Base):
    __tablename__ = "bdds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"), unique=True)

    cash_begin: Mapped[float] = mapped_column(Float, default=0)
    inflows_operating: Mapped[float] = mapped_column(Float, default=0)
    inflows_investing: Mapped[float] = mapped_column(Float, default=0)
    inflows_financing: Mapped[float] = mapped_column(Float, default=0)
    outflows_operating: Mapped[float] = mapped_column(Float, default=0)
    outflows_investing: Mapped[float] = mapped_column(Float, default=0)
    outflows_financing: Mapped[float] = mapped_column(Float, default=0)
    cash_end: Mapped[float] = mapped_column(Float, default=0)

    period: Mapped["Period"] = relationship(back_populates="bdds")


class Coefficients(Base):
    __tablename__ = "coefficients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"), unique=True)

    current_ratio: Mapped[float] = mapped_column(Float, default=0)
    quick_ratio: Mapped[float] = mapped_column(Float, default=0)
    absolute_liquidity: Mapped[float] = mapped_column(Float, default=0)
    autonomy: Mapped[float] = mapped_column(Float, default=0)
    debt_to_equity: Mapped[float] = mapped_column(Float, default=0)
    roa: Mapped[float] = mapped_column(Float, default=0)
    roe: Mapped[float] = mapped_column(Float, default=0)
    profit_margin: Mapped[float] = mapped_column(Float, default=0)

    period: Mapped["Period"] = relationship(back_populates="coefficients")


class CrisisType(Base):
    __tablename__ = "crisis_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")


class PlanTemplate(Base):
    __tablename__ = "plan_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crisis_type_code: Mapped[str] = mapped_column(String(50), default="")
    name: Mapped[str] = mapped_column(String(255))
    items_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON array of {title, stage}


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    crisis_type_code: Mapped[str] = mapped_column(String(50), default="")
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="plans")
    items: Mapped[list["PlanItem"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    title: Mapped[str] = mapped_column(String(500))
    stage: Mapped[str] = mapped_column(String(100), default="")
    due_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="not_started")  # not_started, in_progress, done, cancelled
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    plan: Mapped["Plan"] = relationship(back_populates="items")
