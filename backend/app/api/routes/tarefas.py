from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.api.dependencies import get_tarefa_repository
from app.repositories.tarefa_repository import TarefaRepository
from app.schemas.tarefa import Tarefa, TarefaCreate, TarefaPatch, TarefaUpdate

router = APIRouter(prefix="/tarefas", tags=["tarefas"])

Repository = Annotated[TarefaRepository, Depends(get_tarefa_repository)]
TarefaId = Annotated[int, Path(gt=0, description="Identificador da tarefa")]


def _not_found(tarefa_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarefa {tarefa_id} não encontrada",
    )


@router.get("", response_model=list[Tarefa])
def list_tarefas(
    repository: Repository,
    concluida: Annotated[bool | None, Query(description="Filtra pelo status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return repository.list(concluida=concluida, offset=offset, limit=limit)


@router.get("/{tarefa_id}", response_model=Tarefa)
def get_tarefa(tarefa_id: TarefaId, repository: Repository):
    tarefa = repository.get(tarefa_id)
    if tarefa is None:
        raise _not_found(tarefa_id)
    return tarefa


@router.post("", response_model=Tarefa, status_code=status.HTTP_201_CREATED)
def create_tarefa(payload: TarefaCreate, repository: Repository):
    return repository.create(payload)


@router.put("/{tarefa_id}", response_model=Tarefa)
def replace_tarefa(tarefa_id: TarefaId, payload: TarefaUpdate, repository: Repository):
    tarefa = repository.replace(tarefa_id, payload)
    if tarefa is None:
        raise _not_found(tarefa_id)
    return tarefa


@router.patch("/{tarefa_id}", response_model=Tarefa)
def update_tarefa(tarefa_id: TarefaId, payload: TarefaPatch, repository: Repository):
    tarefa = repository.update(tarefa_id, payload)
    if tarefa is None:
        raise _not_found(tarefa_id)
    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tarefa(tarefa_id: TarefaId, repository: Repository):
    if not repository.delete(tarefa_id):
        raise _not_found(tarefa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
