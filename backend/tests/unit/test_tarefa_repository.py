import pytest

from app.repositories.tarefa_repository import TarefaRepository
from app.schemas.tarefa import TarefaCreate, TarefaPatch, TarefaUpdate


@pytest.fixture
def repository():
    return TarefaRepository()


def test_create_assigns_incremental_ids(repository):
    primeira = repository.create(TarefaCreate(titulo="A"))
    segunda = repository.create(TarefaCreate(titulo="B"))

    assert (primeira.id, segunda.id) == (1, 2)


def test_ids_are_not_reused_after_delete(repository):
    repository.create(TarefaCreate(titulo="A"))
    repository.delete(1)

    assert repository.create(TarefaCreate(titulo="B")).id == 2


def test_get_returns_none_when_missing(repository):
    assert repository.get(1) is None


def test_list_filters_and_paginates(repository):
    for i in range(4):
        repository.create(TarefaCreate(titulo=f"T{i}", concluida=i % 2 == 0))

    assert [t.titulo for t in repository.list(concluida=True)] == ["T0", "T2"]
    assert [t.titulo for t in repository.list(offset=1, limit=2)] == ["T1", "T2"]


def test_replace_overwrites_all_fields(repository):
    repository.create(TarefaCreate(titulo="A", descricao="desc"))

    tarefa = repository.replace(1, TarefaUpdate(titulo="B"))

    assert tarefa.titulo == "B"
    assert tarefa.descricao is None


def test_update_keeps_unsent_fields(repository):
    repository.create(TarefaCreate(titulo="A", descricao="desc"))

    tarefa = repository.update(1, TarefaPatch(concluida=True))

    assert (tarefa.titulo, tarefa.descricao, tarefa.concluida) == ("A", "desc", True)


def test_replace_returns_none_when_missing(repository):
    assert repository.replace(1, TarefaUpdate(titulo="X")) is None


def test_update_returns_none_when_missing(repository):
    assert repository.update(1, TarefaPatch(concluida=True)) is None


def test_delete(repository):
    repository.create(TarefaCreate(titulo="A"))

    assert repository.delete(1) is True
    assert repository.delete(1) is False
