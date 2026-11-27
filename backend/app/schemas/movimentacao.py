from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _texto_vazio_vira_none(valor):
    if isinstance(valor, str):
        valor = valor.strip()
        return valor or None
    return valor


TipoMovimentacao = Literal["entrada", "saida"]


class MovimentacaoCreate(BaseModel):
    tipo: TipoMovimentacao
    quantidade: Annotated[int, Field(gt=0, le=100_000)]
    # O limite vale só para o texto; texto em branco vira None antes de validar.
    observacao: Annotated[
        Annotated[str, Field(max_length=200)] | None,
        BeforeValidator(_texto_vazio_vira_none),
    ] = None


class MovimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int
    observacao: str | None
    criado_em: datetime
