#!/usr/bin/env bash
# Запуск бэкенда из корня проекта (единое окружение в .venv).
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/backend:${PYTHONPATH:-}"
# Рабочая директория backend — чтобы БД и .env были в backend/
cd "$ROOT/backend"
if [[ -x "$ROOT/.venv/bin/uvicorn" ]]; then
  exec "$ROOT/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000
fi
export PATH="${HOME}/.local/bin:${PATH}"
exec uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
