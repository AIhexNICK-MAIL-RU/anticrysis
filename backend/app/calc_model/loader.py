"""Загрузка экспортированной книги (JSON) из export_excel_to_json.py."""
from __future__ import annotations

import json
import os
from typing import Any

# Каталог экспорта относительно пакета
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exported")


def load_workbook_export(export_dir: str | None = None) -> dict[str, Any]:
    """
    Загружает _workbook.json и все листы из export_dir.
    Возвращает: { "workbook": {...}, "sheets": { "Имя листа": { "cells": {...}, ... } } }
    """
    base = export_dir or EXPORT_DIR
    if not os.path.isdir(base):
        return {"workbook": {"sheets": [], "active_sheet": ""}, "sheets": {}}

    with open(os.path.join(base, "_workbook.json"), "r", encoding="utf-8") as f:
        workbook = json.load(f)

    sheets: dict[str, dict] = {}
    for s in workbook.get("sheets", []):
        fname = s.get("file")
        if not fname:
            continue
        path = os.path.join(base, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            sheets[s["name"]] = json.load(f)
    return {"workbook": workbook, "sheets": sheets}
