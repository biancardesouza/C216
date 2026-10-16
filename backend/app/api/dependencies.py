from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.tarefa_repository import TarefaRepository
from app.services.tarefa_service import TarefaService


def get_tarefa_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TarefaRepository:
    return TarefaRepository(session)


def get_tarefa_service(
    repository: Annotated[TarefaRepository, Depends(get_tarefa_repository)],
) -> TarefaService:
    return TarefaService(repository)
