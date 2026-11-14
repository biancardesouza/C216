from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.item_service import ItemJaExisteError, ItemNotFoundError
from app.services.tarefa_service import TarefaNotFoundError


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def conflict_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Traduz as exceções da camada de serviço em respostas HTTP."""
    application.add_exception_handler(TarefaNotFoundError, not_found_handler)
    application.add_exception_handler(ItemNotFoundError, not_found_handler)
    application.add_exception_handler(ItemJaExisteError, conflict_handler)
