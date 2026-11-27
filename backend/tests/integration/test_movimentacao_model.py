from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import MovimentacaoModel, ProdutoModel


@pytest.fixture
def produto(session):
    produto = ProdutoModel(
        sku="CAN-001", nome="Caneta", categoria="Papelaria", preco=Decimal("2.50")
    )
    session.add(produto)
    session.commit()
    return produto


def test_movimentacao_fica_ligada_ao_produto(session, produto):
    session.add(MovimentacaoModel(produto_id=produto.id, tipo="entrada", quantidade=5))
    session.commit()
    session.refresh(produto)

    [movimentacao] = produto.movimentacoes
    assert movimentacao.tipo == "entrada"
    assert movimentacao.produto.sku == "CAN-001"
    assert movimentacao.criado_em is not None


@pytest.mark.parametrize(
    "campos",
    [
        {"tipo": "ajuste", "quantidade": 5},
        {"tipo": "entrada", "quantidade": 0},
        {"tipo": "saida", "quantidade": -2},
    ],
)
def test_valores_invalidos_sao_rejeitados_pelo_banco(session, produto, campos):
    session.add(MovimentacaoModel(produto_id=produto.id, **campos))

    with pytest.raises(IntegrityError):
        session.commit()


def test_movimentacao_de_produto_inexistente_e_rejeitada(session):
    session.add(MovimentacaoModel(produto_id=999, tipo="entrada", quantidade=1))

    with pytest.raises(IntegrityError):
        session.commit()


def test_excluir_produto_apaga_o_historico(session, produto):
    session.add(MovimentacaoModel(produto_id=produto.id, tipo="entrada", quantidade=1))
    session.commit()

    session.delete(produto)
    session.commit()

    assert session.scalars(select(MovimentacaoModel)).all() == []
