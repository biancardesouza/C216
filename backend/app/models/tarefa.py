from sqlalchemy import String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TarefaModel(Base):
    """Modelo ORM: representa a tabela `tarefas` no PostgreSQL."""

    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(500))
    concluida: Mapped[bool] = mapped_column(default=False, server_default=false())
