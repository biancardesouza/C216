from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ItemModel(Base):
    """Modelo ORM: representa a tabela `items` no PostgreSQL."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    descricao: Mapped[str] = mapped_column(String(200))


# Garante no banco que não existam dois itens com o mesmo nome,
# sem diferenciar maiúsculas de minúsculas.
Index("uq_items_nome_lower", func.lower(ItemModel.nome), unique=True)
