#!/usr/bin/env bash
# Активация единого окружения проекта (из корня репозитория).
# Использование: source activate.sh   или   . activate.sh
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" && pwd | tr -d '\r')"
cd "$ROOT" || exit 1
if [[ ! -d .venv ]]; then
  echo "Создаём виртуальное окружение в $ROOT/.venv ..."
  (uv venv --python 3.12 2>/dev/null) || python3 -m venv .venv
  echo "Устанавливаем зависимости бэкенда..."
  source .venv/bin/activate
  (uv pip install -r backend/requirements.txt 2>/dev/null) || .venv/bin/pip install -r backend/requirements.txt
fi
source .venv/bin/activate
echo "Окружение активировано. Backend: ./run-backend.sh  |  Frontend: npm run dev:frontend"
export PYTHONPATH="$ROOT/backend:${PYTHONPATH:-}"
