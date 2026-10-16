from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.tarefa_service import TarefaNotFoundError


async def tarefa_not_found_handler(
    request: Request, exc: TarefaNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Traduz as exceções da camada de serviço em respostas HTTP."""
    application.add_exception_handler(TarefaNotFoundError, tarefa_not_found_handler)
