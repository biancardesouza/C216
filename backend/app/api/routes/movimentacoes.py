from fastapi import APIRouter, status

from app.api.dependencies import MovimentacaoServiceDep
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse

router = APIRouter(
    prefix="/produtos/{produto_id}/movimentacoes", tags=["movimentacoes"]
)

RESPOSTA_404 = {404: {"description": "Produto não encontrado"}}


@router.get("", response_model=list[MovimentacaoResponse], responses=RESPOSTA_404)
def listar_movimentacoes(produto_id: int, service: MovimentacaoServiceDep):
    """Histórico do produto, da movimentação mais recente para a mais antiga."""
    return service.listar_historico(produto_id)


@router.post(
    "",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    responses=RESPOSTA_404 | {409: {"description": "Estoque insuficiente"}},
)
def registrar_movimentacao(
    produto_id: int, dados: MovimentacaoCreate, service: MovimentacaoServiceDep
):
    """Registra uma entrada ou saída e atualiza a quantidade do produto."""
    return service.registrar(produto_id, dados)
