from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version=settings.app_version)
    application.include_router(api_router)
    register_exception_handlers(application)
    return application


app = create_app()
