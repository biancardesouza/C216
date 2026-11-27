from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.repositories.produto_repository import ProdutoRepository
from app.services.movimentacao_service import MovimentacaoService
from app.services.produto_service import ProdutoService

SessaoDb = Annotated[Session, Depends(get_db)]


def get_produto_service(session: SessaoDb) -> ProdutoService:
    # Monta a cadeia sessão -> repositório -> serviço a cada requisição.
    return ProdutoService(ProdutoRepository(session))


def get_movimentacao_service(session: SessaoDb) -> MovimentacaoService:
    return MovimentacaoService(MovimentacaoRepository(session))


ProdutoServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]
MovimentacaoServiceDep = Annotated[
    MovimentacaoService, Depends(get_movimentacao_service)
]
