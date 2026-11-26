from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ProdutoModel(Base):
    """Tabela `produtos`: cada linha é um produto controlado pelo estoque."""

    __tablename__ = "produtos"
    # Regras garantidas também pelo banco, mesmo que alguém escreva direto nele.
    __table_args__ = (
        CheckConstraint("preco > 0", name="ck_produtos_preco_positivo"),
        CheckConstraint("quantidade >= 0", name="ck_produtos_quantidade_nao_negativa"),
        CheckConstraint(
            "estoque_minimo >= 0", name="ck_produtos_estoque_minimo_nao_negativo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(30), unique=True)
    nome: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[str] = mapped_column(String(50))
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    # A quantidade só muda por movimentações (entrada/saída), nunca pela edição.
    quantidade: Mapped[int] = mapped_column(default=0, server_default="0")
    estoque_minimo: Mapped[int] = mapped_column(default=0, server_default="0")
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
