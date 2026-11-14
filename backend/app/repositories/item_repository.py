from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.item import ItemModel


class NomeDuplicadoError(Exception):
    """O banco recusou o item porque já existe outro com o mesmo nome."""


class ItemRepository:
    """Acesso aos dados de Item no PostgreSQL via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> list[ItemModel]:
        return list(self.session.scalars(select(ItemModel).order_by(ItemModel.id)))

    def get(self, item_id: int) -> ItemModel | None:
        return self.session.get(ItemModel, item_id)

    def get_by_nome(self, nome: str) -> ItemModel | None:
        query = select(ItemModel).where(func.lower(ItemModel.nome) == nome.lower())
        return self.session.scalars(query).first()

    def add(self, item: ItemModel) -> ItemModel:
        self.session.add(item)
        return self.save(item)

    def save(self, item: ItemModel) -> ItemModel:
        try:
            self.session.commit()
        except IntegrityError as exc:
            # Cobre duas requisições simultâneas com o mesmo nome:
            # o índice único do banco recusa a segunda.
            self.session.rollback()
            raise NomeDuplicadoError from exc
        self.session.refresh(item)
        return item

    def delete(self, item: ItemModel) -> None:
        self.session.delete(item)
        self.session.commit()
