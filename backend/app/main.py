from fastapi import FastAPI

from app.api.errors import registrar_tratadores_de_erro
from app.api.router import api_router
from app.core.config import Settings, settings


def create_app(config: Settings = settings) -> FastAPI:
    application = FastAPI(title=config.app_name, version=config.app_version)
    application.include_router(api_router)
    registrar_tratadores_de_erro(application)
    return application


app = create_app()
