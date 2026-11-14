import pytest

from app.models.item import ItemModel
from app.repositories.item_repository import NomeDuplicadoError
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.item_service import ItemJaExisteError, ItemNotFoundError, ItemService


class FakeItemRepository:
    """Repositório em memória, para testar o service sem depender do PostgreSQL."""

    def __init__(self) -> None:
        self.items: dict[int, ItemModel] = {}
        self.proximo_id = 1
        self.falhar_ao_salvar = False

    def list(self):
        return list(self.items.values())

    def get(self, item_id):
        return self.items.get(item_id)

    def get_by_nome(self, nome):
        return next(
            (i for i in self.items.values() if i.nome.lower() == nome.lower()), None
        )

    def add(self, item):
        item.id = self.proximo_id
        self.proximo_id += 1
        self.items[item.id] = item
        return self.save(item)

    def save(self, item):
        if self.falhar_ao_salvar:
            raise NomeDuplicadoError
        return item

    def delete(self, item):
        del self.items[item.id]


@pytest.fixture
def repository():
    return FakeItemRepository()


@pytest.fixture
def service(repository):
    return ItemService(repository)


def test_create_converts_schema_into_model(service):
    item = service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))

    assert isinstance(item, ItemModel)
    assert (item.id, item.nome, item.descricao) == (1, "Caderno", "Capa dura")


def test_create_rejects_duplicated_nome_ignoring_case(service):
    service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))

    with pytest.raises(ItemJaExisteError, match="Já existe um item com esse nome."):
        service.create(ItemCreate(nome="CADERNO", descricao="Outro"))


def test_create_translates_database_conflict(service, repository):
    # Simula outra requisição gravando o mesmo nome entre a checagem e o commit.
    repository.falhar_ao_salvar = True

    with pytest.raises(ItemJaExisteError):
        service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))


def test_get_raises_when_missing(service):
    with pytest.raises(ItemNotFoundError, match="Item 7 não encontrado"):
        service.get(7)


def test_update_changes_fields(service):
    item = service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))

    atualizado = service.update(item.id, ItemUpdate(nome="Agenda", descricao="2027"))

    assert (atualizado.nome, atualizado.descricao) == ("Agenda", "2027")


def test_update_allows_keeping_own_nome(service):
    item = service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))

    atualizado = service.update(item.id, ItemUpdate(nome="caderno", descricao="x"))

    assert atualizado.nome == "caderno"


def test_update_rejects_nome_of_another_item(service):
    service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))
    caneta = service.create(ItemCreate(nome="Caneta", descricao="Azul"))

    with pytest.raises(ItemJaExisteError):
        service.update(caneta.id, ItemUpdate(nome="Caderno", descricao="x"))


def test_delete_removes_item(service, repository):
    item = service.create(ItemCreate(nome="Caderno", descricao="Capa dura"))

    service.delete(item.id)

    assert repository.items == {}


def test_delete_raises_when_missing(service):
    with pytest.raises(ItemNotFoundError):
        service.delete(1)
