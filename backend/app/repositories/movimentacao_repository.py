from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MovimentacaoModel, ProdutoModel


class MovimentacaoRepository:
    """Acesso ao banco para o histórico de movimentações de estoque."""

    def __init__(self, session: Session):
        self.session = session

    def buscar_produto(self, produto_id: int) -> ProdutoModel | None:
        return self.session.get(ProdutoModel, produto_id)

    def buscar_produto_com_trava(self, produto_id: int) -> ProdutoModel | None:
        # SELECT ... FOR UPDATE: se duas saídas chegarem ao mesmo tempo, a segunda
        # espera a primeira terminar e já enxerga o saldo atualizado.
        return self.session.get(ProdutoModel, produto_id, with_for_update=True)

    def registrar(
        self, produto: ProdutoModel, novo_saldo: int, dados: dict
    ) -> MovimentacaoModel:
        # A movimentação e o novo saldo são gravados no mesmo commit:
        # ou os dois ficam salvos, ou nenhum.
        movimentacao = MovimentacaoModel(produto_id=produto.id, **dados)
        produto.quantidade = novo_saldo
        self.session.add(movimentacao)
        self.session.commit()
        self.session.refresh(movimentacao)
        return movimentacao

    def listar_por_produto(self, produto_id: int) -> list[MovimentacaoModel]:
        consulta = (
            select(MovimentacaoModel)
            .where(MovimentacaoModel.produto_id == produto_id)
            .order_by(MovimentacaoModel.criado_em.desc(), MovimentacaoModel.id.desc())
        )
        return list(self.session.scalars(consulta))
