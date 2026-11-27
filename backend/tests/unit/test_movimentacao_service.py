from types import SimpleNamespace

import pytest

from app.schemas.movimentacao import MovimentacaoCreate
from app.services.erros import EstoqueInsuficienteError, ProdutoNaoEncontradoError
from app.services.movimentacao_service import MovimentacaoService


class RepositorioEmMemoria:
    """Substitui o repositório real para testar as regras sem banco de dados."""

    def __init__(self):
        self.produtos = {1: SimpleNamespace(id=1, quantidade=0)}
        self.movimentacoes = []

    def buscar_produto(self, produto_id):
        return self.produtos.get(produto_id)

    def buscar_produto_com_trava(self, produto_id):
        return self.produtos.get(produto_id)

    def registrar(self, produto, novo_saldo, dados):
        produto.quantidade = novo_saldo
        movimentacao = SimpleNamespace(
            id=len(self.movimentacoes) + 1, produto_id=produto.id, **dados
        )
        self.movimentacoes.append(movimentacao)
        return movimentacao

    def listar_por_produto(self, produto_id):
        doproduto = [m for m in self.movimentacoes if m.produto_id == produto_id]
        return list(reversed(doproduto))


@pytest.fixture
def repositorio():
    return RepositorioEmMemoria()


@pytest.fixture
def service(repositorio):
    return MovimentacaoService(repositorio)


def _mov(tipo, quantidade):
    return MovimentacaoCreate(tipo=tipo, quantidade=quantidade)


def _saldo(repositorio):
    return repositorio.produtos[1].quantidade


def test_entrada_soma_ao_saldo(service, repositorio):
    service.registrar(1, _mov("entrada", 10))
    service.registrar(1, _mov("entrada", 5))

    assert _saldo(repositorio) == 15


def test_saida_subtrai_do_saldo(service, repositorio):
    service.registrar(1, _mov("entrada", 10))

    movimentacao = service.registrar(1, _mov("saida", 4))

    assert movimentacao.tipo == "saida"
    assert _saldo(repositorio) == 6


def test_saida_de_todo_o_saldo_e_permitida(service, repositorio):
    service.registrar(1, _mov("entrada", 3))

    service.registrar(1, _mov("saida", 3))

    assert _saldo(repositorio) == 0


def test_saida_maior_que_o_saldo_falha_e_nao_altera_nada(service, repositorio):
    service.registrar(1, _mov("entrada", 3))

    with pytest.raises(EstoqueInsuficienteError) as erro:
        service.registrar(1, _mov("saida", 4))

    assert "há 3 unidade(s)" in erro.value.mensagem
    assert _saldo(repositorio) == 3
    assert len(repositorio.movimentacoes) == 1


def test_saida_sem_estoque_falha(service):
    with pytest.raises(EstoqueInsuficienteError):
        service.registrar(1, _mov("saida", 1))


def test_movimentar_produto_inexistente_falha(service):
    with pytest.raises(ProdutoNaoEncontradoError):
        service.registrar(99, _mov("entrada", 1))


def test_historico_vem_do_mais_recente_para_o_mais_antigo(service):
    service.registrar(1, _mov("entrada", 10))
    service.registrar(1, _mov("saida", 2))

    historico = service.listar_historico(1)

    assert [m.tipo for m in historico] == ["saida", "entrada"]


def test_historico_de_produto_inexistente_falha(service):
    with pytest.raises(ProdutoNaoEncontradoError):
        service.listar_historico(99)
