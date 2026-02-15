#!/usr/bin/env bash
# Запуск бэкенда (uv). Добавьте $HOME/.local/bin в PATH, если uv не в PATH.
cd "$(dirname "$0")/backend"
export PATH="${HOME}/.local/bin:${PATH}"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
