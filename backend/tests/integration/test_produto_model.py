from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import ProdutoModel


def _produto(**campos):
    dados = {
        "sku": "CAN-001",
        "nome": "Caneta azul",
        "categoria": "Papelaria",
        "preco": Decimal("2.50"),
    }
    return ProdutoModel(**(dados | campos))


def test_produto_novo_comeca_com_quantidade_zero(session):
    produto = _produto()
    session.add(produto)
    session.commit()

    assert produto.id == 1
    assert produto.quantidade == 0
    assert produto.estoque_minimo == 0
    assert produto.criado_em is not None


def test_sku_duplicado_e_rejeitado_pelo_banco(session):
    session.add(_produto())
    session.commit()

    session.add(_produto(nome="Outra caneta"))
    with pytest.raises(IntegrityError):
        session.commit()


@pytest.mark.parametrize(
    "campos",
    [
        {"preco": Decimal("0")},
        {"quantidade": -1},
        {"estoque_minimo": -5},
    ],
)
def test_valores_invalidos_sao_rejeitados_pelo_banco(session, campos):
    session.add(_produto(**campos))

    with pytest.raises(IntegrityError):
        session.commit()
