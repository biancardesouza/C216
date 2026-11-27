from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.erros import (
    ErroDeNegocio,
    EstoqueInsuficienteError,
    ProdutoComEstoqueError,
    ProdutoNaoEncontradoError,
    SkuDuplicadoError,
)

# Tradução de cada regra de negócio violada para o código HTTP correspondente.
STATUS_POR_ERRO: dict[type[ErroDeNegocio], int] = {
    ProdutoNaoEncontradoError: status.HTTP_404_NOT_FOUND,
    SkuDuplicadoError: status.HTTP_409_CONFLICT,
    ProdutoComEstoqueError: status.HTTP_409_CONFLICT,
    EstoqueInsuficienteError: status.HTTP_409_CONFLICT,
}


async def tratar_erro_de_negocio(request: Request, erro: ErroDeNegocio):
    codigo = STATUS_POR_ERRO.get(type(erro), status.HTTP_400_BAD_REQUEST)
    # Mesmo formato dos erros do próprio FastAPI: {"detail": ...}
    return JSONResponse(status_code=codigo, content={"detail": erro.mensagem})


def registrar_tratadores_de_erro(application: FastAPI) -> None:
    application.add_exception_handler(ErroDeNegocio, tratar_erro_de_negocio)
