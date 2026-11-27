from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

TIPOS_DE_MOVIMENTACAO = ("entrada", "saida")


class MovimentacaoModel(Base):
    """Tabela `movimentacoes`: histórico de entradas e saídas de cada produto."""

    __tablename__ = "movimentacoes"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('entrada', 'saida')", name="ck_movimentacoes_tipo_valido"
        ),
        CheckConstraint("quantidade > 0", name="ck_movimentacoes_quantidade_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Ao excluir um produto (só permitido com saldo zero), o histórico vai junto.
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[str] = mapped_column(String(10))
    quantidade: Mapped[int]
    observacao: Mapped[str | None] = mapped_column(String(200))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    produto: Mapped["ProdutoModel"] = relationship(  # noqa: F821
        back_populates="movimentacoes"
    )
