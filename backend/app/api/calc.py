"""
API расчётного модуля (фин. модель из Excel → JSON).
Доступен авторизованному пользователю.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models import User
from app.calc_model.runner import get_model_metadata, run_calculation

router = APIRouter(prefix="/calc", tags=["calc"])


class CalcRunInput(BaseModel):
    """Входы для расчёта: адрес ячейки → число (например B2=100)."""
    inputs: dict[str, float] = {}


@router.get("/model")
def get_calc_model(_: User = Depends(get_current_user)):
    """Метаданные расчётной модели: листы, наличие данных."""
    return get_model_metadata()


@router.post("/run")
def run_calc(data: CalcRunInput, _: User = Depends(get_current_user)):
    """
    Запуск расчёта с заданными входами.
    inputs: { "B2": 1000, "B3": 400, "Данные!C2": 500 } — подстановка в ячейки.
    Возвращает все ячейки после вычисления формул.
    """
    return run_calculation(inputs=data.inputs or {})
