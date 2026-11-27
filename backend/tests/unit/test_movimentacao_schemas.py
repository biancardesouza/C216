import pytest
from pydantic import ValidationError

from app.schemas.movimentacao import MovimentacaoCreate


@pytest.mark.parametrize("tipo", ["entrada", "saida"])
def test_tipos_validos_sao_aceitos(tipo):
    assert MovimentacaoCreate(tipo=tipo, quantidade=1).tipo == tipo


@pytest.mark.parametrize(
    "dados",
    [
        {"tipo": "ajuste", "quantidade": 1},
        {"tipo": "ENTRADA", "quantidade": 1},
        {"tipo": "entrada", "quantidade": 0},
        {"tipo": "saida", "quantidade": -5},
        {"tipo": "entrada", "quantidade": 100_001},
        {"tipo": "entrada", "quantidade": 1, "observacao": "x" * 201},
        {"quantidade": 1},
    ],
)
def test_dados_invalidos_sao_rejeitados(dados):
    with pytest.raises(ValidationError):
        MovimentacaoCreate(**dados)


def test_observacao_e_opcional():
    assert MovimentacaoCreate(tipo="entrada", quantidade=1).observacao is None


@pytest.mark.parametrize(
    ("enviada", "esperada"),
    [("  Compra do fornecedor  ", "Compra do fornecedor"), ("   ", None), ("", None)],
)
def test_observacao_e_limpa(enviada, esperada):
    dados = MovimentacaoCreate(tipo="entrada", quantidade=1, observacao=enviada)

    assert dados.observacao == esperada
