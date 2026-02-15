"""
Расчётный модуль по экспортированной финансовой модели (Excel → JSON).
Позволяет запускать расчёты по структуре книги без Excel.
"""
from app.calc_model.loader import load_workbook_export
from app.calc_model.runner import run_calculation, get_model_metadata

__all__ = ["load_workbook_export", "run_calculation", "get_model_metadata"]
