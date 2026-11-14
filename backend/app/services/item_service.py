from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository, NomeDuplicadoError
from app.schemas.item import ItemCreate, ItemUpdate


class ItemNotFoundError(Exception):
    def __init__(self, item_id: int) -> None:
        super().__init__(f"Item {item_id} não encontrado")
        self.item_id = item_id


class ItemJaExisteError(Exception):
    def __init__(self) -> None:
        super().__init__("Já existe um item com esse nome.")


class ItemService:
    """Regras de negócio de Item: o nome não pode se repetir (sem diferenciar caixa)."""

    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def list(self) -> list[ItemModel]:
        return self.repository.list()

    def get(self, item_id: int) -> ItemModel:
        item = self.repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    def create(self, data: ItemCreate) -> ItemModel:
        self._garantir_nome_unico(data.nome)
        try:
            return self.repository.add(ItemModel(**data.model_dump()))
        except NomeDuplicadoError as exc:
            raise ItemJaExisteError from exc

    def update(self, item_id: int, data: ItemUpdate) -> ItemModel:
        item = self.get(item_id)
        self._garantir_nome_unico(data.nome, ignorar_id=item_id)
        item.nome = data.nome
        item.descricao = data.descricao
        try:
            return self.repository.save(item)
        except NomeDuplicadoError as exc:
            raise ItemJaExisteError from exc

    def delete(self, item_id: int) -> None:
        self.repository.delete(self.get(item_id))

    def _garantir_nome_unico(self, nome: str, ignorar_id: int | None = None) -> None:
        existente = self.repository.get_by_nome(nome)
        if existente is not None and existente.id != ignorar_id:
            raise ItemJaExisteError
