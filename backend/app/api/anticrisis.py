from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import (
    User,
    UserOrganization,
    Period,
    Balance,
    BDR,
    BDDS,
    Coefficients,
    Plan,
    PlanItem,
)
from app.schemas.anticrisis import (
    PeriodCreate,
    PeriodResponse,
    BalanceCreate,
    BDRCreate,
    BDDSCreate,
    CoefficientsResponse,
    CrisisClassification,
    PeriodTableResponse,
    FinModelResponse,
    PlanCreate,
    PlanResponse,
    PlanItemResponse,
    PlanItemUpdate,
)
from app.services.coefficients import calculate_coefficients
from app.services.crisis_classifier import classify_crisis, CRISIS_TYPES
from app.services.fin_model import run_fin_model
from app.api.deps import get_current_user, get_organization_membership

router = APIRouter(prefix="/orgs/{org_id}/anticrisis", tags=["anticrisis"])


@router.post("/periods", response_model=PeriodResponse)
async def create_period(
    org_id: int,
    data: PeriodCreate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    period = Period(
        organization_id=org_id,
        period_type=data.period_type,
        period_start=data.period_start,
        period_end=data.period_end,
        label=data.label or "",
    )
    db.add(period)
    await db.flush()
    db.add(Balance(period_id=period.id))
    db.add(BDR(period_id=period.id))
    db.add(BDDS(period_id=period.id))
    db.add(Coefficients(period_id=period.id))
    await db.refresh(period)
    return period


@router.get("/periods", response_model=list[PeriodResponse])
async def list_periods(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(
        select(Period).where(Period.organization_id == org_id).order_by(Period.period_start.desc())
    )
    return list(result.scalars().all())


async def _recalc_coefficients(db: AsyncSession, period_id: int, balance: Balance, bdr: BDR):
    coefs = calculate_coefficients(
        noncurrent_assets=balance.noncurrent_assets,
        current_assets=balance.current_assets,
        equity=balance.equity,
        long_term_liabilities=balance.long_term_liabilities,
        short_term_liabilities=balance.short_term_liabilities,
        receivables=balance.receivables,
        payables=balance.payables,
        cash=balance.cash,
        revenue=bdr.revenue,
        cost_of_sales=bdr.cost_of_sales,
        operating_expenses=bdr.operating_expenses,
        other_income=bdr.other_income,
        other_expenses=bdr.other_expenses,
    )
    result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
    row = result.scalar_one_or_none()
    if row:
        for k, v in coefs.items():
            setattr(row, k, v)
    return coefs


@router.put("/periods/{period_id}/balance")
async def update_balance(
    org_id: int,
    period_id: int,
    data: BalanceCreate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(Balance).where(Balance.period_id == period_id))
    balance = result.scalar_one_or_none()
    if not balance:
        balance = Balance(period_id=period_id)
        db.add(balance)
        await db.flush()
    for k, v in data.model_dump().items():
        setattr(balance, k, v)
    result = await db.execute(select(BDR).where(BDR.period_id == period_id))
    bdr = result.scalar_one_or_none() or BDR(period_id=period_id)
    if not bdr.period_id:
        db.add(bdr)
        await db.flush()
    coefs = calculate_coefficients(
        balance.noncurrent_assets, balance.current_assets, balance.equity,
        balance.long_term_liabilities, balance.short_term_liabilities,
        balance.receivables, balance.payables, balance.cash,
        bdr.revenue, bdr.cost_of_sales, bdr.operating_expenses, bdr.other_income, bdr.other_expenses,
    )
    result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
    coef_row = result.scalar_one_or_none()
    if not coef_row:
        coef_row = Coefficients(period_id=period_id)
        db.add(coef_row)
        await db.flush()
    for k, v in coefs.items():
        setattr(coef_row, k, v)
    await db.refresh(balance)
    return {"ok": True}


@router.put("/periods/{period_id}/bdr")
async def update_bdr(
    org_id: int,
    period_id: int,
    data: BDRCreate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(BDR).where(BDR.period_id == period_id))
    bdr = result.scalar_one_or_none()
    if not bdr:
        bdr = BDR(period_id=period_id)
        db.add(bdr)
        await db.flush()
    for k, v in data.model_dump().items():
        setattr(bdr, k, v)
    result = await db.execute(select(Balance).where(Balance.period_id == period_id))
    balance = result.scalar_one_or_none()
    if balance:
        result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
        coef_row = result.scalar_one_or_none()
        if not coef_row:
            coef_row = Coefficients(period_id=period_id)
            db.add(coef_row)
            await db.flush()
        coefs = calculate_coefficients(
            balance.noncurrent_assets, balance.current_assets, balance.equity,
            balance.long_term_liabilities, balance.short_term_liabilities,
            balance.receivables, balance.payables, balance.cash,
            bdr.revenue, bdr.cost_of_sales, bdr.operating_expenses, bdr.other_income, bdr.other_expenses,
        )
        for k, v in coefs.items():
            setattr(coef_row, k, v)
    await db.refresh(bdr)
    return {"ok": True}


@router.put("/periods/{period_id}/bdds")
async def update_bdds(
    org_id: int,
    period_id: int,
    data: BDDSCreate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(BDDS).where(BDDS.period_id == period_id))
    bdds = result.scalar_one_or_none()
    if not bdds:
        bdds = BDDS(period_id=period_id)
        db.add(bdds)
        await db.flush()
    for k, v in data.model_dump().items():
        setattr(bdds, k, v)
    await db.refresh(bdds)
    return {"ok": True}


@router.get("/periods/{period_id}/table", response_model=PeriodTableResponse)
async def get_period_table(
    org_id: int,
    period_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    """Данные для расчётной таблицы: баланс, БДР, БДДС, коэффициенты, карта кризиса."""
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(Balance).where(Balance.period_id == period_id))
    balance = result.scalar_one_or_none()
    result = await db.execute(select(BDR).where(BDR.period_id == period_id))
    bdr = result.scalar_one_or_none()
    result = await db.execute(select(BDDS).where(BDDS.period_id == period_id))
    bdds = result.scalar_one_or_none()
    if not balance or not bdr:
        raise HTTPException(404, "Введите данные баланса и БДР в разделе «Отчётность»")
    coefs = calculate_coefficients(
        balance.noncurrent_assets, balance.current_assets, balance.equity,
        balance.long_term_liabilities, balance.short_term_liabilities,
        balance.receivables, balance.payables, balance.cash,
        bdr.revenue, bdr.cost_of_sales, bdr.operating_expenses, bdr.other_income, bdr.other_expenses,
    )
    result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
    coef_row = result.scalar_one_or_none()
    if coef_row:
        code, confidence, reasoning = classify_crisis(
            current_ratio=coef_row.current_ratio,
            quick_ratio=coef_row.quick_ratio,
            absolute_liquidity=coef_row.absolute_liquidity,
            autonomy=coef_row.autonomy,
            profit_margin=coef_row.profit_margin,
            cash=balance.cash,
            short_term_liabilities=balance.short_term_liabilities,
        )
    else:
        code, confidence, reasoning = classify_crisis(
            current_ratio=coefs["current_ratio"],
            quick_ratio=coefs["quick_ratio"],
            absolute_liquidity=coefs["absolute_liquidity"],
            autonomy=coefs["autonomy"],
            profit_margin=coefs["profit_margin"],
            cash=balance.cash,
            short_term_liabilities=balance.short_term_liabilities,
        )
    balance_dict = {
        "noncurrent_assets": balance.noncurrent_assets,
        "current_assets": balance.current_assets,
        "equity": balance.equity,
        "long_term_liabilities": balance.long_term_liabilities,
        "short_term_liabilities": balance.short_term_liabilities,
        "receivables": balance.receivables,
        "payables": balance.payables,
        "cash": balance.cash,
    }
    bdr_dict = {
        "revenue": bdr.revenue,
        "cost_of_sales": bdr.cost_of_sales,
        "operating_expenses": bdr.operating_expenses,
        "other_income": bdr.other_income,
        "other_expenses": bdr.other_expenses,
        "profit": bdr.revenue - bdr.cost_of_sales - bdr.operating_expenses + bdr.other_income - bdr.other_expenses,
    }
    bdds_dict = {}
    if bdds:
        bdds_dict = {
            "cash_begin": bdds.cash_begin,
            "inflows_operating": bdds.inflows_operating,
            "outflows_operating": bdds.outflows_operating,
            "inflows_investing": bdds.inflows_investing,
            "outflows_investing": bdds.outflows_investing,
            "inflows_financing": bdds.inflows_financing,
            "outflows_financing": bdds.outflows_financing,
            "cash_end": bdds.cash_end,
        }
    fin = run_fin_model(balance_dict, bdr_dict, bdds_dict or {})
    return PeriodTableResponse(
        period=PeriodResponse.model_validate(period),
        balance=balance_dict,
        bdr=bdr_dict,
        bdds=bdds_dict,
        coefficients=CoefficientsResponse(**coefs),
        crisis=CrisisClassification(
            crisis_type_code=code,
            crisis_type_name=CRISIS_TYPES.get(code, code),
            confidence=confidence,
            reasoning=reasoning,
        ),
        fin_model=FinModelResponse(**fin),
    )


@router.get("/periods/{period_id}/coefficients", response_model=CoefficientsResponse)
async def get_coefficients(
    org_id: int,
    period_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
    coef = result.scalar_one_or_none()
    if not coef:
        raise HTTPException(404, "Коэффициенты не рассчитаны")
    return coef


@router.get("/periods/{period_id}/fin-model")
async def get_period_fin_model(
    org_id: int,
    period_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    """Результаты финансовой модели по данным периода (баланс, БДР, БДДС)."""
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(Balance).where(Balance.period_id == period_id))
    balance = result.scalar_one_or_none()
    result = await db.execute(select(BDR).where(BDR.period_id == period_id))
    bdr = result.scalar_one_or_none()
    result = await db.execute(select(BDDS).where(BDDS.period_id == period_id))
    bdds = result.scalar_one_or_none()
    if not balance or not bdr:
        raise HTTPException(404, "Введите данные баланса и БДР в разделе «Отчётность»")
    balance_dict = {k: getattr(balance, k, 0) for k in ["noncurrent_assets", "current_assets", "equity", "long_term_liabilities", "short_term_liabilities", "receivables", "payables", "cash"]}
    bdr_dict = {k: getattr(bdr, k, 0) for k in ["revenue", "cost_of_sales", "operating_expenses", "other_income", "other_expenses"]}
    bdds_dict = {}
    if bdds:
        bdds_dict = {k: getattr(bdds, k, 0) for k in ["cash_begin", "inflows_operating", "outflows_operating", "inflows_investing", "outflows_investing", "inflows_financing", "outflows_financing", "cash_end"]}
    fin = run_fin_model(balance_dict, bdr_dict, bdds_dict)
    return {"period_id": period.id, "period_label": period.label or "", "fin_model": FinModelResponse(**fin)}


@router.get("/periods/{period_id}/crisis", response_model=CrisisClassification)
async def get_crisis_classification(
    org_id: int,
    period_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(
        select(Period).where(Period.id == period_id, Period.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Период не найден")
    result = await db.execute(select(Balance).where(Balance.period_id == period_id))
    balance = result.scalar_one_or_none()
    result = await db.execute(select(Coefficients).where(Coefficients.period_id == period_id))
    coef = result.scalar_one_or_none()
    if not balance or not coef:
        return CrisisClassification(
            crisis_type_code="stagnation",
            crisis_type_name=CRISIS_TYPES["stagnation"],
            confidence=0,
            reasoning="Введите данные баланса и БДР для классификации.",
        )
    code, confidence, reasoning = classify_crisis(
        current_ratio=coef.current_ratio,
        quick_ratio=coef.quick_ratio,
        absolute_liquidity=coef.absolute_liquidity,
        autonomy=coef.autonomy,
        profit_margin=coef.profit_margin,
        cash=balance.cash,
        short_term_liabilities=balance.short_term_liabilities,
    )
    return CrisisClassification(
        crisis_type_code=code,
        crisis_type_name=CRISIS_TYPES.get(code, code),
        confidence=confidence,
        reasoning=reasoning,
    )


@router.get("/crisis-types")
async def list_crisis_types():
    return [{"code": k, "name": v} for k, v in CRISIS_TYPES.items()]


# --- Plans ---
def _plan_to_response(plan: Plan, items: list) -> PlanResponse:
    """Собираем ответ без обращения к relationship (избегаем greenlet в async)."""
    return PlanResponse(
        id=plan.id,
        organization_id=plan.organization_id,
        crisis_type_code=plan.crisis_type_code or "",
        title=plan.title,
        created_at=plan.created_at,
        items=[PlanItemResponse.model_validate(i) for i in items],
    )


@router.post("/plans", response_model=PlanResponse)
async def create_plan(
    org_id: int,
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    plan = Plan(organization_id=org_id, crisis_type_code=data.crisis_type_code or "", title=data.title)
    db.add(plan)
    await db.flush()
    for i, it in enumerate(data.items or []):
        item = PlanItem(
            plan_id=plan.id,
            title=it.title,
            stage=it.stage or "",
            due_date=it.due_date,
            status=it.status or "not_started",
            completed=False,
            sort_order=i,
        )
        db.add(item)
    await db.flush()
    result = await db.execute(select(PlanItem).where(PlanItem.plan_id == plan.id).order_by(PlanItem.sort_order))
    items = list(result.scalars().all())
    return _plan_to_response(plan, items)


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(select(Plan).where(Plan.organization_id == org_id).order_by(Plan.created_at.desc()))
    plans = list(result.scalars().all())
    out = []
    for p in plans:
        r = await db.execute(select(PlanItem).where(PlanItem.plan_id == p.id).order_by(PlanItem.sort_order))
        items = list(r.scalars().all())
        out.append(_plan_to_response(p, items))
    return out


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    org_id: int,
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(select(Plan).where(Plan.id == plan_id, Plan.organization_id == org_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "План не найден")
    result = await db.execute(select(PlanItem).where(PlanItem.plan_id == plan.id).order_by(PlanItem.sort_order))
    items = list(result.scalars().all())
    return _plan_to_response(plan, items)


@router.patch("/plans/{plan_id}/items/{item_id}")
async def update_plan_item(
    org_id: int,
    plan_id: int,
    item_id: int,
    data: PlanItemUpdate,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    if membership.role not in ("owner", "manager", "finance"):
        raise HTTPException(403, "Недостаточно прав")
    result = await db.execute(select(Plan).where(Plan.id == plan_id, Plan.organization_id == org_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "План не найден")
    result = await db.execute(select(PlanItem).where(PlanItem.id == item_id, PlanItem.plan_id == plan_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Пункт не найден")
    if data.title is not None:
        item.title = data.title
    if data.status is not None:
        item.status = data.status
    if data.completed is not None:
        item.completed = data.completed
        item.status = "done" if data.completed else item.status
    if data.due_date is not None:
        item.due_date = data.due_date
    await db.refresh(item)
    return {"ok": True}
