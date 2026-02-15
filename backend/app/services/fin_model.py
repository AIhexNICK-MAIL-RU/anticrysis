"""
Финансовая модель: расчёты только по входным данным веб-сервиса (баланс, БДР, БДДС).
Соответствует логике из «Рабочая тетрадь_Фин модель.xlsx» (ТБУ, маржа, денежные потоки).
Входы — те же поля, что пользователь вводит в таблицах отчётности.
"""
from __future__ import annotations

from typing import Any


def _f(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def run_fin_model(
    balance: dict[str, Any],
    bdr: dict[str, Any],
    bdds: dict[str, Any],
) -> dict[str, float]:
    """
    Принимает словари balance, bdr, bdds (поля как в таблицах веб-сервиса).
    Возвращает словарь рассчитанных показателей (прибыль, маржа, ТБУ, потоки и т.д.).
    """
    # Баланс
    na = _f(balance.get("noncurrent_assets"))
    ca = _f(balance.get("current_assets"))
    eq = _f(balance.get("equity"))
    ltl = _f(balance.get("long_term_liabilities"))
    stl = _f(balance.get("short_term_liabilities"))
    rec = _f(balance.get("receivables"))
    pay = _f(balance.get("payables"))
    cash = _f(balance.get("cash"))

    # БДР
    rev = _f(bdr.get("revenue"))
    cos = _f(bdr.get("cost_of_sales"))
    opex = _f(bdr.get("operating_expenses"))
    oth_inc = _f(bdr.get("other_income"))
    oth_exp = _f(bdr.get("other_expenses"))

    # БДДС
    cash_beg = _f(bdds.get("cash_begin"))
    in_op = _f(bdds.get("inflows_operating"))
    out_op = _f(bdds.get("outflows_operating"))
    in_inv = _f(bdds.get("inflows_investing"))
    out_inv = _f(bdds.get("outflows_investing"))
    in_fin = _f(bdds.get("inflows_financing"))
    out_fin = _f(bdds.get("outflows_financing"))
    cash_end = _f(bdds.get("cash_end"))

    # --- Итоги по балансу ---
    total_assets = na + ca
    total_liabilities = ltl + stl
    equity_ratio = (total_assets and eq / total_assets) or 0.0

    # --- БДР: прибыль и маржи ---
    profit = rev - cos - opex + oth_inc - oth_exp
    profit_margin = (rev and profit / rev) or 0.0
    gross_profit = rev - cos
    gross_margin = (rev and gross_profit / rev) or 0.0
    # ТБУ по выручке: выручка, при которой прибыль = 0. При margin > 0: break_even_revenue = постоянные / (1 - доля переменных).
    # Упрощение: если profit_margin > 0, то break_even_revenue ≈ opex / (1 - (cos/rev)) при rev > 0; иначе через margin: rev_be = opex / profit_margin
    if profit_margin > 0 and rev > 0:
        break_even_revenue = opex / profit_margin
    elif rev > 0 and (rev - cos) > 0:
        # Маржа после себестоимости: (rev - cos)/rev. ТБУ: opex / ((rev - cos)/rev)
        contribution_ratio = (rev - cos) / rev
        if contribution_ratio > 0:
            break_even_revenue = opex / contribution_ratio
        else:
            break_even_revenue = 0.0
    else:
        break_even_revenue = 0.0

    # --- БДДС: потоки ---
    operating_cash_flow = in_op - out_op
    investing_cash_flow = in_inv - out_inv
    financing_cash_flow = in_fin - out_fin
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    # Расчётный остаток на конец, если не задан
    cash_end_calc = cash_beg + net_cash_flow

    return {
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "equity_ratio": round(equity_ratio, 4),
        "profit": round(profit, 2),
        "profit_margin": round(profit_margin, 4),
        "gross_profit": round(gross_profit, 2),
        "gross_margin": round(gross_margin, 4),
        "break_even_revenue": round(break_even_revenue, 2),
        "operating_cash_flow": round(operating_cash_flow, 2),
        "investing_cash_flow": round(investing_cash_flow, 2),
        "financing_cash_flow": round(financing_cash_flow, 2),
        "net_cash_flow": round(net_cash_flow, 2),
        "cash_end_calculated": round(cash_end_calc, 2),
    }
