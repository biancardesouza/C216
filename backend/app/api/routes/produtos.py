from fastapi import APIRouter, status

from app.api.dependencies import ProdutoServiceDep
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate

router = APIRouter(prefix="/produtos", tags=["produtos"])

RESPOSTA_404 = {404: {"description": "Produto não encontrado"}}


@router.get("", response_model=list[ProdutoResponse])
def listar_produtos(service: ProdutoServiceDep):
    return service.listar()


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "SKU já cadastrado"}},
)
def criar_produto(dados: ProdutoCreate, service: ProdutoServiceDep):
    return service.criar(dados)


@router.get("/{produto_id}", response_model=ProdutoResponse, responses=RESPOSTA_404)
def buscar_produto(produto_id: int, service: ProdutoServiceDep):
    return service.buscar(produto_id)


@router.put(
    "/{produto_id}",
    response_model=ProdutoResponse,
    responses=RESPOSTA_404 | {409: {"description": "SKU já cadastrado"}},
)
def atualizar_produto(
    produto_id: int, dados: ProdutoUpdate, service: ProdutoServiceDep
):
    return service.atualizar(produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPOSTA_404 | {409: {"description": "Produto ainda tem estoque"}},
)
def excluir_produto(produto_id: int, service: ProdutoServiceDep):
    service.excluir(produto_id)
