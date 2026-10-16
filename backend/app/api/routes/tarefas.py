from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.dependencies import get_tarefa_service
from app.schemas.tarefa import Tarefa, TarefaCreate, TarefaPatch, TarefaUpdate
from app.services.tarefa_service import TarefaService

router = APIRouter(prefix="/tarefas", tags=["tarefas"])

Service = Annotated[TarefaService, Depends(get_tarefa_service)]
TarefaId = Annotated[int, Path(gt=0, description="Identificador da tarefa")]


@router.get("", response_model=list[Tarefa])
def list_tarefas(
    service: Service,
    concluida: Annotated[bool | None, Query(description="Filtra pelo status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return service.list(concluida=concluida, offset=offset, limit=limit)


@router.get("/{tarefa_id}", response_model=Tarefa)
def get_tarefa(tarefa_id: TarefaId, service: Service):
    return service.get(tarefa_id)


@router.post("", response_model=Tarefa, status_code=status.HTTP_201_CREATED)
def create_tarefa(payload: TarefaCreate, service: Service):
    return service.create(payload)


@router.put("/{tarefa_id}", response_model=Tarefa)
def replace_tarefa(tarefa_id: TarefaId, payload: TarefaUpdate, service: Service):
    return service.replace(tarefa_id, payload)


@router.patch("/{tarefa_id}", response_model=Tarefa)
def update_tarefa(tarefa_id: TarefaId, payload: TarefaPatch, service: Service):
    return service.update(tarefa_id, payload)


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tarefa(tarefa_id: TarefaId, service: Service):
    service.delete(tarefa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
