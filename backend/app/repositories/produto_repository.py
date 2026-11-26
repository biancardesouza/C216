from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ProdutoModel


class ProdutoRepository:
    """Único lugar que conversa com a tabela `produtos` pelo SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def listar(self) -> list[ProdutoModel]:
        consulta = select(ProdutoModel).order_by(ProdutoModel.nome)
        return list(self.session.scalars(consulta))

    def buscar_por_id(self, produto_id: int) -> ProdutoModel | None:
        return self.session.get(ProdutoModel, produto_id)

    def buscar_por_sku(self, sku: str) -> ProdutoModel | None:
        consulta = select(ProdutoModel).where(ProdutoModel.sku == sku)
        return self.session.scalar(consulta)

    def criar(self, dados: dict) -> ProdutoModel:
        produto = ProdutoModel(**dados)
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def atualizar(self, produto: ProdutoModel, dados: dict) -> ProdutoModel:
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def excluir(self, produto: ProdutoModel) -> None:
        self.session.delete(produto)
        self.session.commit()
