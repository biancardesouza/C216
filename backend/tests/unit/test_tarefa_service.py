import pytest

from app.models.tarefa import TarefaModel
from app.schemas.tarefa import TarefaCreate, TarefaPatch, TarefaUpdate
from app.services.tarefa_service import TarefaNotFoundError, TarefaService


class FakeTarefaRepository:
    """Repositório em memória, para testar o service sem depender do PostgreSQL."""

    def __init__(self) -> None:
        self.tarefas: dict[int, TarefaModel] = {}
        self.saved: list[TarefaModel] = []

    def list(self, concluida=None, offset=0, limit=10):
        tarefas = [
            t
            for t in self.tarefas.values()
            if concluida is None or t.concluida == concluida
        ]
        return tarefas[offset : offset + limit]

    def get(self, tarefa_id):
        return self.tarefas.get(tarefa_id)

    def add(self, tarefa):
        tarefa.id = len(self.tarefas) + 1
        self.tarefas[tarefa.id] = tarefa
        return tarefa

    def save(self, tarefa):
        self.saved.append(tarefa)
        return tarefa

    def delete(self, tarefa):
        del self.tarefas[tarefa.id]


@pytest.fixture
def repository():
    return FakeTarefaRepository()


@pytest.fixture
def service(repository):
    return TarefaService(repository)


def test_create_converts_schema_into_model(service):
    tarefa = service.create(TarefaCreate(titulo="A", descricao="desc"))

    assert isinstance(tarefa, TarefaModel)
    assert (tarefa.id, tarefa.titulo, tarefa.descricao) == (1, "A", "desc")
    assert tarefa.concluida is False


def test_list_passes_filters_to_repository(service):
    service.create(TarefaCreate(titulo="A"))
    service.create(TarefaCreate(titulo="B", concluida=True))

    assert [t.titulo for t in service.list(concluida=True)] == ["B"]


@pytest.mark.parametrize(
    "action",
    [
        lambda s: s.get(1),
        lambda s: s.replace(1, TarefaUpdate(titulo="X")),
        lambda s: s.update(1, TarefaPatch(concluida=True)),
        lambda s: s.delete(1),
    ],
    ids=["get", "replace", "update", "delete"],
)
def test_raises_not_found_when_missing(service, action):
    with pytest.raises(TarefaNotFoundError, match="Tarefa 1 não encontrada"):
        action(service)


def test_replace_overwrites_all_fields(service, repository):
    service.create(TarefaCreate(titulo="A", descricao="desc", concluida=True))

    tarefa = service.replace(1, TarefaUpdate(titulo="B"))

    assert (tarefa.titulo, tarefa.descricao, tarefa.concluida) == ("B", None, False)
    assert repository.saved == [tarefa]


def test_update_keeps_unsent_fields(service, repository):
    service.create(TarefaCreate(titulo="A", descricao="desc"))

    tarefa = service.update(1, TarefaPatch(concluida=True))

    assert (tarefa.titulo, tarefa.descricao, tarefa.concluida) == ("A", "desc", True)
    assert repository.saved == [tarefa]


def test_delete_removes_from_repository(service, repository):
    service.create(TarefaCreate(titulo="A"))

    service.delete(1)

    assert repository.tarefas == {}
