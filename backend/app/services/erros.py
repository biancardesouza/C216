class ErroDeNegocio(Exception):
    """Base das regras de negócio violadas. A camada de API traduz para HTTP."""

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ProdutoNaoEncontradoError(ErroDeNegocio):
    def __init__(self, produto_id: int):
        super().__init__(f"Produto {produto_id} não encontrado.")


class SkuDuplicadoError(ErroDeNegocio):
    def __init__(self, sku: str):
        super().__init__(f"Já existe um produto com o SKU {sku}.")


class ProdutoComEstoqueError(ErroDeNegocio):
    def __init__(self, quantidade: int):
        super().__init__(
            f"O produto ainda tem {quantidade} unidade(s) em estoque. "
            "Registre a saída antes de excluir."
        )


class EstoqueInsuficienteError(ErroDeNegocio):
    def __init__(self, disponivel: int, solicitado: int):
        super().__init__(
            f"Estoque insuficiente: há {disponivel} unidade(s) disponível(is) "
            f"e a saída pedida foi de {solicitado}."
        )
