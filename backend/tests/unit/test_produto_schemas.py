from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.produto import ProdutoCreate, ProdutoResponse

DADOS_VALIDOS = {
    "sku": "CAN-001",
    "nome": "Caneta azul",
    "categoria": "Papelaria",
    "preco": "2.50",
    "estoque_minimo": 10,
}


def test_produto_valido_e_aceito():
    produto = ProdutoCreate(**DADOS_VALIDOS)

    assert produto.preco == Decimal("2.50")
    assert produto.estoque_minimo == 10


def test_sku_e_normalizado_para_maiusculas_sem_espacos():
    produto = ProdutoCreate(**(DADOS_VALIDOS | {"sku": "  can-001 "}))

    assert produto.sku == "CAN-001"


def test_estoque_minimo_tem_padrao_zero():
    dados = {
        campo: v for campo, v in DADOS_VALIDOS.items() if campo != "estoque_minimo"
    }

    assert ProdutoCreate(**dados).estoque_minimo == 0


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("sku", "AB"),
        ("sku", "CAN 001"),
        ("sku", "CAN_001"),
        ("nome", "   "),
        ("nome", "x" * 101),
        ("categoria", "A"),
        ("preco", "0"),
        ("preco", "-3"),
        ("preco", "2.555"),
        ("estoque_minimo", -1),
    ],
)
def test_dados_invalidos_sao_rejeitados(campo, valor):
    with pytest.raises(ValidationError):
        ProdutoCreate(**(DADOS_VALIDOS | {campo: valor}))


def test_quantidade_nao_e_aceita_no_cadastro():
    produto = ProdutoCreate(**(DADOS_VALIDOS | {"quantidade": 50}))

    assert "quantidade" not in produto.model_dump()


@pytest.mark.parametrize(
    ("quantidade", "estoque_minimo", "esperado"),
    [(3, 10, True), (10, 10, True), (11, 10, False), (0, 0, True)],
)
def test_estoque_baixo_quando_quantidade_chega_ao_minimo(
    quantidade, estoque_minimo, esperado
):
    agora = datetime.now(UTC)
    produto = SimpleNamespace(
        id=1,
        sku="CAN-001",
        nome="Caneta azul",
        categoria="Papelaria",
        preco=Decimal("2.50"),
        quantidade=quantidade,
        estoque_minimo=estoque_minimo,
        criado_em=agora,
        atualizado_em=agora,
    )

    resposta = ProdutoResponse.model_validate(produto)

    assert resposta.estoque_baixo is esperado
    assert resposta.model_dump()["estoque_baixo"] is esperado
