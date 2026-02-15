"""
Простой вычислитель формул по экспортированным ячейкам.
Поддерживает: числа, ссылки на ячейки (A1, Лист1!A1), диапазоны (A1:A10),
SUM, AVERAGE, арифметику + - * /
"""
from __future__ import annotations

import re
from typing import Any

# Ячейка: буквы столбца + номер строки (не после буквы/цифры, чтобы не съедать оператор)
CELL_RE = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]+)([1-9]\d*)(?=[^\w]|$)")
# Диапазон A1:A10
RANGE_RE = re.compile(r"([A-Za-z]+)([1-9]\d*)\s*:\s*([A-Za-z]+)([1-9]\d*)")
# SUM(A1:A10) или SUM( Лист!A1:A10 )
FUNC_RE = re.compile(r"(SUM|AVERAGE)\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)


def _col_to_num(col: str) -> int:
    n = 0
    for c in col.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


def _num_to_col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(ord("A") + r) + s
    return s or "A"


def _range_cells(col1: str, row1: int, col2: str, row2: int) -> list[tuple[str, int]]:
    c1, c2 = _col_to_num(col1), _col_to_num(col2)
    out = []
    for r in range(min(row1, row2), max(row1, row2) + 1):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            out.append((_num_to_col(c), r))
    return out


def _cell_key(col: str, row: int) -> str:
    return f"{col}{row}"


def _to_number(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(",", "."))
        except ValueError:
            return None
    return None


def get_cell_dependencies(formula: str, sheet_name: str) -> set[str]:
    """Из формулы извлекает множество зависимостей: 'Sheet!A1' или 'A1' (текущий лист)."""
    deps: set[str] = set()
    if not formula or not str(formula).strip().startswith("="):
        return deps
    formula = str(formula).strip()[1:].strip()

    def add_cell(col: str, row: int, sheet: str | None = None):
        key = f"{sheet}!{col}{row}" if sheet else f"{col}{row}"
        deps.add(key)

    # Функции с диапазонами
    for m in FUNC_RE.finditer(formula):
        arg = m.group(2).strip()
        if "!" in arg:
            sheet_part, ref = arg.split("!", 1)
            sheet_part = sheet_part.strip().strip("'")
        else:
            sheet_part = sheet_name
            ref = arg
        range_m = RANGE_RE.search(ref)
        if range_m:
            for col, row in _range_cells(
                range_m.group(1), int(range_m.group(2)),
                range_m.group(3), int(range_m.group(4)),
            ):
                add_cell(col, row, sheet_part or None)
        else:
            cell_m = CELL_RE.search(ref)
            if cell_m:
                add_cell(cell_m.group(1), int(cell_m.group(2)), sheet_part or None)
    # Одиночные ссылки на ячейки (без листа)
    for m in CELL_RE.finditer(formula):
        add_cell(m.group(1), int(m.group(2)), None)
    return deps


def evaluate_formula(
    formula: str,
    get_value: Any,
    sheet_name: str = "",
) -> float | str | None:
    """
    Вычисляет формулу. get_value(sheet_name, col, row) или get_value(cell_key) -> number/None.
    """
    if not formula or not str(formula).strip().startswith("="):
        return _to_number(formula) if formula is not None else None
    formula = str(formula).strip()[1:].strip()

    def cell_value(sheet: str, col: str, row: int) -> float | None:
        key = f"{sheet}!{col}{row}" if sheet else f"{col}{row}"
        if callable(get_value):
            v = get_value(key) if "!" not in key else get_value(key)
            return _to_number(v)
        return None

    def resolve_range(ref: str) -> list[float]:
        ref = ref.strip()
        cur_sheet = sheet_name
        if "!" in ref:
            cur_sheet, ref = ref.split("!", 1)
            cur_sheet = cur_sheet.strip().strip("'")
            ref = ref.strip()
        vals = []
        range_m = RANGE_RE.search(ref)
        if range_m:
            for col, row in _range_cells(
                range_m.group(1), int(range_m.group(2)),
                range_m.group(3), int(range_m.group(4)),
            ):
                v = cell_value(cur_sheet, col, row)
                if v is not None:
                    vals.append(v)
        else:
            cell_m = CELL_RE.search(ref)
            if cell_m:
                v = cell_value(cur_sheet, cell_m.group(1), int(cell_m.group(2)))
                if v is not None:
                    vals.append(v)
        return vals

    # Заменить SUM(...) и AVERAGE(...) на числа
    def replace_func(m: re.Match) -> str:
        func, arg = m.group(1).upper(), m.group(2).strip()
        vals = resolve_range(arg)
        if not vals:
            return "0"
        if func == "SUM":
            return str(sum(vals))
        if func == "AVERAGE":
            return str(sum(vals) / len(vals))
        return "0"

    formula = FUNC_RE.sub(replace_func, formula)

    # Заменить оставшиеся ссылки на ячейки (Лист!A1 или A1)
    def replace_cell(m: re.Match) -> str:
        col, row = m.group(1), int(m.group(2))
        key = f"{sheet_name}!{col}{row}" if sheet_name else f"{col}{row}"
        v = get_value(key) if callable(get_value) else None
        n = _to_number(v)
        return str(n) if n is not None else "0"
    formula = CELL_RE.sub(lambda m: replace_cell(m), formula)

    # Безопасное вычисление: только числа и + - * / ( ) . и пробелы
    formula = formula.replace(",", ".")
    if not re.match(r"^[\d\s+\-*/().]+$", formula):
        return None
    try:
        return float(eval(formula))
    except Exception:
        return None


def build_flat_cells(sheets: dict[str, dict]) -> dict[str, Any]:
    """Строит плоский словарь ячеек: ключ = 'SheetName!A1' или 'A1' (для первого листа)."""
    flat: dict[str, Any] = {}
    sheet_list = list(sheets.keys())
    for sheet_name, data in sheets.items():
        cells = data.get("cells") or {}
        for coord, info in cells.items():
            if sheet_list and sheet_list[0] == sheet_name:
                flat[coord] = info
            flat[f"{sheet_name}!{coord}"] = info
    return flat


def topological_order(cells: dict[str, Any], sheet_name: str) -> list[str]:
    """Возвращает порядок вычисления ячеек (сначала без формул, потом по зависимостям)."""
    formula_cells = []
    for key, info in cells.items():
        if isinstance(info, dict) and info.get("formula"):
            formula_cells.append((key, info["formula"]))
    # Простой порядок: по строке, затем по столбцу (A1, B1, ..., A2, B2, ...)
    def key_order(k: str):
        base = k.split("!")[-1]
        m = CELL_RE.search(base) or re.match(r"([A-Za-z]+)(\d+)", base)
        if m:
            return (_col_to_num(m.group(1)), int(m.group(2)))
        return (0, 0)
    ordered = sorted(set(c for c, _ in formula_cells), key=key_order)
    return ordered


def evaluate_sheet(sheet_name: str, sheet_data: dict, get_value: Any) -> dict[str, float | str | None]:
    """Вычисляет все формулы на листе; get_value уже может возвращать значения ранее вычисленных ячеек."""
    cells = sheet_data.get("cells") or {}
    results: dict[str, float | str | None] = {}

    # Сначала все константы
    for coord, info in cells.items():
        if not isinstance(info, dict):
            continue
        if info.get("data_type") != "f" or not info.get("formula"):
            v = info.get("value")
            n = _to_number(v)
            results[coord] = n if n is not None else v
            results[f"{sheet_name}!{coord}"] = results[coord]

    def getter(cell_key: str):
        if cell_key in results:
            return results[cell_key]
        if sheet_name and "!" not in cell_key:
            full = f"{sheet_name}!{cell_key}"
            if full in results:
                return results[full]
        return get_value(cell_key) if callable(get_value) else None

    # Формулы: несколько проходов, пока все не вычислены (для кросс-зависимостей)
    formula_cells = [
        (coord, info) for coord, info in cells.items()
        if isinstance(info, dict) and info.get("data_type") == "f" and info.get("formula")
    ]
    for _ in range(max(len(formula_cells) * 2, 1)):
        changed = False
        for coord, info in formula_cells:
            if coord in results:
                continue
            val = evaluate_formula(info["formula"], getter, sheet_name)
            results[coord] = val
            results[f"{sheet_name}!{coord}"] = val
            changed = True
        if not changed:
            break
    return results


def evaluate_all_sheets(loaded: dict[str, Any]) -> dict[str, Any]:
    """
    loaded: результат load_workbook_export() — { "workbook": {...}, "sheets": { name: { cells } } }.
    Возвращает: { "SheetName!A1": value, "A1": value, ... } для всех ячеек.
    """
    sheets = loaded.get("sheets") or {}
    all_results: dict[str, Any] = {}

    def get_value(cell_key: str):
        return all_results.get(cell_key)

    sheet_list = loaded.get("workbook", {}).get("sheets", [])
    for s in sheet_list:
        name = s.get("name") if isinstance(s, dict) else s
        if name not in sheets:
            continue
        sheet_results = evaluate_sheet(sheet_name=name, sheet_data=sheets[name], get_value=get_value)
        for k, v in sheet_results.items():
            all_results[k] = v
    return all_results
