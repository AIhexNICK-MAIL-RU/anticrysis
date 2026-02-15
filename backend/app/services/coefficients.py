"""Расчёт коэффициентов по балансу и БДР (ликвидность, платёжеспособность, рентабельность)."""


def calculate_coefficients(
    noncurrent_assets: float,
    current_assets: float,
    equity: float,
    long_term_liabilities: float,
    short_term_liabilities: float,
    receivables: float,
    payables: float,
    cash: float,
    revenue: float,
    cost_of_sales: float,
    operating_expenses: float,
    other_income: float,
    other_expenses: float,
) -> dict:
    total_assets = noncurrent_assets + current_assets
    total_liabilities = long_term_liabilities + short_term_liabilities
    # Ликвидность
    current_ratio = (short_term_liabilities and current_assets / short_term_liabilities) or 0
    quick_assets = current_assets  # упрощённо; можно вычесть запасы при наличии
    quick_ratio = (short_term_liabilities and quick_assets / short_term_liabilities) or 0
    absolute_liquidity = (short_term_liabilities and cash / short_term_liabilities) or 0

    # Финансовая устойчивость
    autonomy = (total_assets and equity / total_assets) or 0
    debt_to_equity = (equity and (long_term_liabilities + short_term_liabilities) / equity) or 0

    # Прибыль для рентабельности
    profit = revenue - cost_of_sales - operating_expenses + other_income - other_expenses

    roa = (total_assets and profit / total_assets) or 0
    roe = (equity and profit / equity) or 0
    profit_margin = (revenue and profit / revenue) or 0

    return {
        "current_ratio": round(current_ratio, 4),
        "quick_ratio": round(quick_ratio, 4),
        "absolute_liquidity": round(absolute_liquidity, 4),
        "autonomy": round(autonomy, 4),
        "debt_to_equity": round(debt_to_equity, 4),
        "roa": round(roa, 4),
        "roe": round(roe, 4),
        "profit_margin": round(profit_margin, 4),
    }
