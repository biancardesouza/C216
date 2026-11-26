from types import SimpleNamespace

import pytest

from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.services.erros import (
    ProdutoComEstoqueError,
    ProdutoNaoEncontradoError,
    SkuDuplicadoError,
)
from app.services.produto_service import ProdutoService


class RepositorioEmMemoria:
    """Substitui o repositório real para testar as regras sem banco de dados."""

    def __init__(self):
        self.produtos = {}
        self.proximo_id = 1

    def listar(self):
        return sorted(self.produtos.values(), key=lambda p: p.nome)

    def buscar_por_id(self, produto_id):
        return self.produtos.get(produto_id)

    def buscar_por_sku(self, sku):
        return next((p for p in self.produtos.values() if p.sku == sku), None)

    def criar(self, dados):
        produto = SimpleNamespace(id=self.proximo_id, quantidade=0, **dados)
        self.produtos[produto.id] = produto
        self.proximo_id += 1
        return produto

    def atualizar(self, produto, dados):
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        return produto

    def excluir(self, produto):
        del self.produtos[produto.id]


def _dados(**campos):
    base = {"sku": "CAN-001", "nome": "Caneta", "categoria": "Papelaria", "preco": 2}
    return base | campos


@pytest.fixture
def repositorio():
    return RepositorioEmMemoria()


@pytest.fixture
def service(repositorio):
    return ProdutoService(repositorio)


def test_criar_produto(service):
    produto = service.criar(ProdutoCreate(**_dados()))

    assert produto.id == 1
    assert produto.sku == "CAN-001"
    assert produto.quantidade == 0


def test_criar_com_sku_existente_falha(service):
    service.criar(ProdutoCreate(**_dados()))

    with pytest.raises(SkuDuplicadoError):
        service.criar(ProdutoCreate(**_dados(sku="can-001", nome="Outra")))


def test_listar_ordena_por_nome(service):
    service.criar(ProdutoCreate(**_dados(sku="LAP-001", nome="Lápis")))
    service.criar(ProdutoCreate(**_dados(sku="BOR-001", nome="Borracha")))

    assert [p.nome for p in service.listar()] == ["Borracha", "Lápis"]


def test_buscar_produto_inexistente_falha(service):
    with pytest.raises(ProdutoNaoEncontradoError):
        service.buscar(99)


def test_atualizar_produto(service):
    produto = service.criar(ProdutoCreate(**_dados()))

    atualizado = service.atualizar(
        produto.id, ProdutoUpdate(**_dados(nome="Caneta preta", preco=3))
    )

    assert atualizado.nome == "Caneta preta"
    assert atualizado.preco == 3


def test_atualizar_mantendo_o_proprio_sku_e_permitido(service):
    produto = service.criar(ProdutoCreate(**_dados()))

    atualizado = service.atualizar(produto.id, ProdutoUpdate(**_dados()))

    assert atualizado.sku == "CAN-001"


def test_atualizar_para_sku_de_outro_produto_falha(service):
    service.criar(ProdutoCreate(**_dados()))
    lapis = service.criar(ProdutoCreate(**_dados(sku="LAP-001", nome="Lápis")))

    with pytest.raises(SkuDuplicadoError):
        service.atualizar(lapis.id, ProdutoUpdate(**_dados(nome="Lápis")))


def test_atualizar_produto_inexistente_falha(service):
    with pytest.raises(ProdutoNaoEncontradoError):
        service.atualizar(99, ProdutoUpdate(**_dados()))


def test_excluir_produto_sem_estoque(service, repositorio):
    produto = service.criar(ProdutoCreate(**_dados()))

    service.excluir(produto.id)

    assert repositorio.produtos == {}


def test_excluir_produto_com_estoque_falha(service, repositorio):
    produto = service.criar(ProdutoCreate(**_dados()))
    produto.quantidade = 5

    with pytest.raises(ProdutoComEstoqueError):
        service.excluir(produto.id)
    assert produto.id in repositorio.produtos


def test_excluir_produto_inexistente_falha(service):
    with pytest.raises(ProdutoNaoEncontradoError):
        service.excluir(99)
