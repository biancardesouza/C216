from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.item_repository import ItemRepository
from app.repositories.tarefa_repository import TarefaRepository
from app.services.item_service import ItemService
from app.services.tarefa_service import TarefaService


def get_tarefa_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TarefaRepository:
    return TarefaRepository(session)


def get_tarefa_service(
    repository: Annotated[TarefaRepository, Depends(get_tarefa_repository)],
) -> TarefaService:
    return TarefaService(repository)


def get_item_repository(
    session: Annotated[Session, Depends(get_db)],
) -> ItemRepository:
    return ItemRepository(session)


def get_item_service(
    repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(repository)
