"""
Запуск расчёта по экспортированной модели: подстановка входов и получение всех ячеек.
"""
from __future__ import annotations

from typing import Any

from app.calc_model.loader import load_workbook_export
from app.calc_model.evaluator import evaluate_all_sheets


def get_model_metadata(export_dir: str | None = None) -> dict[str, Any]:
    """Метаданные модели: список листов, размерности (для UI)."""
    loaded = load_workbook_export(export_dir)
    wb = loaded.get("workbook", {})
    sheets = []
    for s in wb.get("sheets", []):
        name = s.get("name", "")
        sheets.append({
            "name": name,
            "visibility": s.get("visibility", "visible"),
            "file": s.get("file", ""),
        })
    return {
        "sheets": sheets,
        "active_sheet": wb.get("active_sheet", ""),
        "has_model": len(loaded.get("sheets") or {}) > 0,
    }


def run_calculation(
    inputs: dict[str, float] | None = None,
    export_dir: str | None = None,
) -> dict[str, Any]:
    """
    Загружает модель, подставляет inputs (ключи: 'A1', 'Лист1!B2' и т.д.),
    вычисляет все формулы и возвращает все ячейки.
    inputs — подстановка значений вместо текущих в ячейках (для ввода пользователя).
    """
    loaded = load_workbook_export(export_dir)
    if not loaded.get("sheets"):
        return {"cells": {}, "metadata": get_model_metadata(export_dir)}

    # Подставить входные значения в ячейки перед расчётом
    inputs = inputs or {}
    for sheet_name, sheet_data in loaded["sheets"].items():
        cells = sheet_data.get("cells") or {}
        for coord, info in list(cells.items()):
            key_short = coord
            key_long = f"{sheet_name}!{coord}"
            if key_short in inputs:
                if isinstance(info, dict):
                    sheet_data["cells"][coord] = {
                        **info,
                        "value": inputs[key_short],
                        "formula": None,
                        "data_type": "n",
                    }
                else:
                    sheet_data["cells"][coord] = {"value": inputs[key_short], "formula": None, "data_type": "n"}
            elif key_long in inputs:
                if isinstance(info, dict):
                    sheet_data["cells"][coord] = {
                        **info,
                        "value": inputs[key_long],
                        "formula": None,
                        "data_type": "n",
                    }
                else:
                    sheet_data["cells"][coord] = {"value": inputs[key_long], "formula": None, "data_type": "n"}

    results = evaluate_all_sheets(loaded)
    # Привести к числам где возможно для JSON
    out = {}
    for k, v in results.items():
        if v is None:
            out[k] = None
        elif isinstance(v, float):
            out[k] = round(v, 6) if v == v else v  # keep nan
        else:
            out[k] = v
    return {
        "cells": out,
        "metadata": get_model_metadata(export_dir),
    }
