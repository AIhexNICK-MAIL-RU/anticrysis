# Веб-сервис «Антикризисное управление»

Проект расположен **целиком в этой папке** (`2_feb`). Никакие другие папки не изменяются.

Соответствует ТЗ: веб-сервис для бизнесменов по подписке с модулем антикризисного управления (баланс, БДР, БДДС, коэффициенты, классификация типа кризиса по правилам, планы мероприятий).

## Структура

- **backend/** — API на FastAPI (Python), SQLite, JWT-авторизация, расчёт коэффициентов и классификация кризиса по правилам.
- **frontend/** — SPA на React (TypeScript, Vite), дашборд, ввод отчётности, планы мероприятий.
- **ТЗ_веб-сервис_антикризисное_управление.md** — техническое задание.
- **ПРОМПТ_для_составления_ТЗ_веб-сервиса.md** — промпт для ТЗ.

## Единое окружение (одна папка — корень проекта)

Все зависимости собраны в корне проекта: Python — в `.venv/`, Node — в `node_modules/` (через npm workspaces). Активация одной командой.

### Одна команда активации (macOS / Linux)

Из корня проекта:

```bash
source activate.sh
```

или

```bash
. activate.sh
```

Скрипт при первом запуске создаёт `.venv`, ставит зависимости бэкенда (`backend/requirements.txt`), активирует окружение и выставляет `PYTHONPATH` для запуска бэкенда из корня.

### Ручная настройка (если не используете activate.sh)

**1. Виртуальное окружение Python (в корне):**

```bash
# из корня проекта (2_feb)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r backend/requirements.txt
```

**2. Зависимости фронтенда (из корня):**

```bash
npm install
```

Устанавливаются в `frontend/node_modules/` (workspace). Окружение готово.

**Активация в следующий раз** — только активировать venv:

- **macOS / Linux:** `source .venv/bin/activate`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

Деактивация: `deactivate`.

## Запуск

### Вариант A: Docker (рекомендуется)

Из корня проекта:

```bash
docker compose up --build
```

- Фронтенд: http://localhost (порт 80)
- Бэкенд API: http://localhost:8000
- Документация API: http://localhost:8000/docs

Данные БД сохраняются в volume `backend_data`.

### Вариант B: Локально (единое окружение в корне)

После активации окружения одной командой (`source activate.sh`) и установки фронта (`npm install`):

**Бэкенд** (из корня):

```bash
./run-backend.sh
```

или с уже активированным `.venv`: `PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

**Фронтенд** (из корня):

```bash
npm run dev:frontend
```

или `./run-frontend.sh`

- API: http://127.0.0.1:8000  
- Документация: http://127.0.0.1:8000/docs  
- Фронтенд: http://localhost:5173  

Фронтенд ходит на бэкенд через прокси `/api` → `http://127.0.0.1:8000` (настроено в `frontend/vite.config.ts`).

## Сценарий использования

1. **Регистрация** → **Вход**.
2. **Организации** → создать организацию.
3. **Дашборд** → выбрать организацию → перейти в «Отчётность и коэффициенты».
4. Добавить **период**, ввести данные **Баланса** и **БДР** (и при необходимости БДДС), сохранить.
5. Посмотреть **коэффициенты** и **карту кризиса** (тип кризиса по правилам).
6. **Планы мероприятий** → создать план (привязка к типу кризиса), отмечать выполнение пунктов чек-листа.

## Технологии

- **Backend:** FastAPI, SQLAlchemy 2 (async), SQLite (aiosqlite), JWT, Pydantic.
- **Frontend:** React 18, React Router, TypeScript, Vite.
- **Расчёты:** ликвидность (текущая, быстрая, абсолютная), автономия, долг/капитал, ROA, ROE, рентабельность продаж.
- **Классификация кризиса:** правила по порогам (стагнация, рост, техническое банкротство, фактическое банкротство, старение).

Все файлы проекта лежат только в этой папке.

## Git: как залить проект в репозиторий

Репозиторий инициализирован в этой папке. В `.gitignore` добавлены:

- **Презентации и рабочие тетради:** `*.pdf`, `*.pptx`, `*.ppt`, `*.xlsx`, `*.xls`, `*.ipynb`, `*.doc`, `*.docx`
- **Среда и артефакты:** `venv/`, `node_modules/`, `__pycache__/`, `dist/`, `*.db`, `.env`
- **IDE и OS:** `.idea/`, `.vscode/`, `.DS_Store`

### Первый коммит и пуш в GitHub

1. Добавить файлы и сделать коммит:

```bash
git add .
git status   # проверьте, что в индекс не попали .pdf, .xlsx и т.п.
git commit -m "Initial: веб-сервис антикризисное управление, Docker"
```

2. Связать проект с удалённым репозиторием (если ещё не добавлен remote):

```bash
git remote add origin https://github.com/AIhexNICK-MAIL-RU/anticrysis.git
```

Если `origin` уже есть с другим URL — заменить:  
`git remote set-url origin https://github.com/AIhexNICK-MAIL-RU/anticrysis.git`

3. Загрузить код в GitHub:

```bash
git push -u origin master
```

Git запросит логин и пароль (или токен). Если в репозитории на GitHub уже есть другие коммиты и push отклонится — выполнить:

```bash
git push -u origin master --force-with-lease
```

Для работы по SSH:

```bash
git remote set-url origin git@github.com:AIhexNICK-MAIL-RU/anticrysis.git
git push -u origin master
```
