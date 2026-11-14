import pytest
from pydantic import ValidationError

from app.schemas.item import ItemCreate


def test_item_create_strips_whitespace():
    item = ItemCreate(nome="  Caderno ", descricao=" Capa dura ")

    assert (item.nome, item.descricao) == ("Caderno", "Capa dura")


@pytest.mark.parametrize("nome", ["", "ab", "  ab  ", "x" * 51])
def test_item_create_rejects_invalid_nome(nome):
    with pytest.raises(ValidationError):
        ItemCreate(nome=nome, descricao="ok")


@pytest.mark.parametrize("descricao", ["", "   ", "x" * 201])
def test_item_create_rejects_invalid_descricao(descricao):
    with pytest.raises(ValidationError):
        ItemCreate(nome="Caderno", descricao=descricao)


def test_item_create_accepts_limits():
    item = ItemCreate(nome="x" * 50, descricao="y" * 200)

    assert len(item.nome) == 50
    assert len(item.descricao) == 200
