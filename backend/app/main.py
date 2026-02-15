from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.config import get_settings
from app.api import auth, organizations, anticrisis
from app.services.crisis_classifier import CRISIS_TYPES


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


settings = get_settings()
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app = FastAPI(
    title="Антикризисное управление",
    description="Веб-сервис для диагностики и планирования антикризисных мероприятий (по ТЗ)",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(anticrisis.router)


@app.get("/crisis-types")
def list_crisis_types_public():
    return [{"code": k, "name": v} for k, v in CRISIS_TYPES.items()]


@app.get("/")
def root():
    return {"service": "anticrisis", "docs": "/docs"}
