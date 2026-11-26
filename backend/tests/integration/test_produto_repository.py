from decimal import Decimal

import pytest

from app.repositories.produto_repository import ProdutoRepository


def _dados(**campos):
    base = {
        "sku": "CAN-001",
        "nome": "Caneta",
        "categoria": "Papelaria",
        "preco": Decimal("2.50"),
    }
    return base | campos


@pytest.fixture
def repositorio(session):
    return ProdutoRepository(session)


def test_criar_e_buscar_por_id(repositorio):
    criado = repositorio.criar(_dados())

    encontrado = repositorio.buscar_por_id(criado.id)

    assert encontrado.sku == "CAN-001"
    assert encontrado.preco == Decimal("2.50")


def test_buscar_por_sku(repositorio):
    repositorio.criar(_dados())

    assert repositorio.buscar_por_sku("CAN-001").nome == "Caneta"
    assert repositorio.buscar_por_sku("NAO-EXISTE") is None


def test_listar_ordenado_por_nome(repositorio):
    repositorio.criar(_dados(sku="LAP-001", nome="Lápis"))
    repositorio.criar(_dados(sku="BOR-001", nome="Borracha"))

    assert [p.nome for p in repositorio.listar()] == ["Borracha", "Lápis"]


def test_atualizar_persiste_alteracoes(repositorio, session_factory):
    produto = repositorio.criar(_dados())

    repositorio.atualizar(produto, {"nome": "Caneta preta", "estoque_minimo": 5})

    with session_factory() as outra_sessao:
        salvo = ProdutoRepository(outra_sessao).buscar_por_id(produto.id)
        assert salvo.nome == "Caneta preta"
        assert salvo.estoque_minimo == 5


def test_excluir_remove_do_banco(repositorio):
    produto = repositorio.criar(_dados())

    repositorio.excluir(produto)

    assert repositorio.buscar_por_id(produto.id) is None
