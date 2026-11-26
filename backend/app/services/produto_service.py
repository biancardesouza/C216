from app.models import ProdutoModel
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.services.erros import (
    ProdutoComEstoqueError,
    ProdutoNaoEncontradoError,
    SkuDuplicadoError,
)


class ProdutoService:
    """Regras de negócio dos produtos. Não sabe nada de HTTP nem de SQL."""

    def __init__(self, repository: ProdutoRepository):
        self.repository = repository

    def listar(self) -> list[ProdutoModel]:
        return self.repository.listar()

    def buscar(self, produto_id: int) -> ProdutoModel:
        produto = self.repository.buscar_por_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontradoError(produto_id)
        return produto

    def criar(self, dados: ProdutoCreate) -> ProdutoModel:
        if self.repository.buscar_por_sku(dados.sku) is not None:
            raise SkuDuplicadoError(dados.sku)
        return self.repository.criar(dados.model_dump())

    def atualizar(self, produto_id: int, dados: ProdutoUpdate) -> ProdutoModel:
        produto = self.buscar(produto_id)
        # O SKU pode mudar, desde que não seja o de outro produto.
        dono_do_sku = self.repository.buscar_por_sku(dados.sku)
        if dono_do_sku is not None and dono_do_sku.id != produto.id:
            raise SkuDuplicadoError(dados.sku)
        return self.repository.atualizar(produto, dados.model_dump())

    def excluir(self, produto_id: int) -> None:
        produto = self.buscar(produto_id)
        # Excluir um produto com saldo faria o estoque "sumir" sem registro.
        if produto.quantidade > 0:
            raise ProdutoComEstoqueError(produto.quantidade)
        self.repository.excluir(produto)
