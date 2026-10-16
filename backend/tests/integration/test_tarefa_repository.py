import pytest

from app.models.tarefa import TarefaModel
from app.repositories.tarefa_repository import TarefaRepository


@pytest.fixture
def repository(session):
    return TarefaRepository(session)


def test_add_assigns_incremental_ids(repository):
    primeira = repository.add(TarefaModel(titulo="A"))
    segunda = repository.add(TarefaModel(titulo="B"))

    assert (primeira.id, segunda.id) == (1, 2)


def test_add_applies_database_defaults(repository):
    tarefa = repository.add(TarefaModel(titulo="A"))

    assert tarefa.descricao is None
    assert tarefa.concluida is False


def test_ids_are_not_reused_after_delete(repository):
    repository.delete(repository.add(TarefaModel(titulo="A")))

    assert repository.add(TarefaModel(titulo="B")).id == 2


def test_get_returns_none_when_missing(repository):
    assert repository.get(1) is None


def test_list_filters_and_paginates(repository):
    for i in range(4):
        repository.add(TarefaModel(titulo=f"T{i}", concluida=i % 2 == 0))

    assert [t.titulo for t in repository.list(concluida=True)] == ["T0", "T2"]
    assert [t.titulo for t in repository.list(offset=1, limit=2)] == ["T1", "T2"]


def test_save_persists_changes(repository, session_factory):
    tarefa = repository.add(TarefaModel(titulo="A"))

    tarefa.concluida = True
    repository.save(tarefa)

    # Uma sessão nova lê direto do banco, provando que a alteração foi persistida.
    with session_factory() as other_session:
        assert other_session.get(TarefaModel, tarefa.id).concluida is True


def test_delete(repository):
    tarefa = repository.add(TarefaModel(titulo="A"))

    repository.delete(tarefa)

    assert repository.get(tarefa.id) is None
