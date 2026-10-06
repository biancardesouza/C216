from fastapi import APIRouter

from app.api.routes import health, tarefas

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(tarefas.router)
