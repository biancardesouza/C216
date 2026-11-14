from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

# Os limites são os mesmos validados pelo formulário do frontend.
Nome = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)
]
Descricao = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class ItemCreate(BaseModel):
    nome: Nome
    descricao: Descricao


class ItemUpdate(ItemCreate):
    pass


class Item(ItemCreate):
    # Permite montar a resposta a partir do modelo ORM (ItemModel).
    model_config = ConfigDict(from_attributes=True)

    id: int
