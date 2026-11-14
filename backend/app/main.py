from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.core.config import Settings, settings


def create_app(config: Settings = settings) -> FastAPI:
    application = FastAPI(title=config.app_name, version=config.app_version)
    # O frontend roda em outra origem (porta 5173): o navegador só entrega a
    # resposta se a API devolver o cabeçalho Access-Control-Allow-Origin.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
    )
    application.include_router(api_router)
    register_exception_handlers(application)
    return application


app = create_app()
