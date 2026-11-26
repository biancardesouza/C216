from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
)


def _normalizar_sku(valor):
    # Roda antes da validação: " can-001 " vira "CAN-001" e só então é checado.
    return valor.strip().upper() if isinstance(valor, str) else valor


Texto = Annotated[str, StringConstraints(strip_whitespace=True)]
# SKU sempre em maiúsculas, só com letras, números e hífen (ex.: CAN-001).
Sku = Annotated[
    str,
    BeforeValidator(_normalizar_sku),
    StringConstraints(min_length=3, max_length=30, pattern=r"^[A-Z0-9-]+$"),
]


class ProdutoBase(BaseModel):
    sku: Sku
    nome: Annotated[Texto, Field(min_length=2, max_length=100)]
    categoria: Annotated[Texto, Field(min_length=2, max_length=50)]
    preco: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    estoque_minimo: Annotated[int, Field(ge=0)] = 0


class ProdutoCreate(ProdutoBase):
    """Dados para cadastrar um produto. A quantidade sempre começa em zero."""


class ProdutoUpdate(ProdutoBase):
    """Dados para editar um produto. A quantidade só muda por movimentação."""


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    nome: str
    categoria: str
    preco: Decimal
    quantidade: int
    estoque_minimo: int
    criado_em: datetime
    atualizado_em: datetime

    @computed_field
    @property
    def estoque_baixo(self) -> bool:
        return self.quantidade <= self.estoque_minimo
