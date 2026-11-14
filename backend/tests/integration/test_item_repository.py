import pytest

from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository, NomeDuplicadoError


@pytest.fixture
def repository(session):
    return ItemRepository(session)


def test_get_by_nome_ignores_case(repository):
    caderno = repository.add(ItemModel(nome="Caderno", descricao="Capa dura"))

    assert repository.get_by_nome("CADERNO").id == caderno.id
    assert repository.get_by_nome("Caneta") is None


def test_database_rejects_duplicated_nome(repository):
    # Mesmo sem passar pelo service, o índice único do banco impede duplicados.
    repository.add(ItemModel(nome="Caderno", descricao="Capa dura"))

    with pytest.raises(NomeDuplicadoError):
        repository.add(ItemModel(nome="caderno", descricao="Outro"))

    assert [i.nome for i in repository.list()] == ["Caderno"]
