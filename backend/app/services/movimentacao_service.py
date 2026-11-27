from app.models import MovimentacaoModel
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.schemas.movimentacao import MovimentacaoCreate
from app.services.erros import EstoqueInsuficienteError, ProdutoNaoEncontradoError


class MovimentacaoService:
    """Regras de entrada e saída: é o único caminho que altera a quantidade."""

    def __init__(self, repository: MovimentacaoRepository):
        self.repository = repository

    def registrar(
        self, produto_id: int, dados: MovimentacaoCreate
    ) -> MovimentacaoModel:
        produto = self.repository.buscar_produto_com_trava(produto_id)
        if produto is None:
            raise ProdutoNaoEncontradoError(produto_id)

        if dados.tipo == "entrada":
            novo_saldo = produto.quantidade + dados.quantidade
        else:
            # Regra principal do estoque: nunca sai mais do que existe.
            if dados.quantidade > produto.quantidade:
                raise EstoqueInsuficienteError(produto.quantidade, dados.quantidade)
            novo_saldo = produto.quantidade - dados.quantidade

        return self.repository.registrar(produto, novo_saldo, dados.model_dump())

    def listar_historico(self, produto_id: int) -> list[MovimentacaoModel]:
        if self.repository.buscar_produto(produto_id) is None:
            raise ProdutoNaoEncontradoError(produto_id)
        return self.repository.listar_por_produto(produto_id)
