import pytest

NOVO_PRODUTO = {
    "sku": "CAN-001",
    "nome": "Caneta azul",
    "categoria": "Papelaria",
    "preco": "2.50",
    "estoque_minimo": 5,
}


@pytest.fixture
def produto(client):
    return client.post("/produtos", json=NOVO_PRODUTO).json()


def _movimentar(client, produto_id, tipo, quantidade, **extra):
    return client.post(
        f"/produtos/{produto_id}/movimentacoes",
        json={"tipo": tipo, "quantidade": quantidade, **extra},
    )


def _produto_atual(client, produto_id):
    return client.get(f"/produtos/{produto_id}").json()


# ---------- POST /produtos/{id}/movimentacoes ----------


def test_entrada_retorna_201_e_aumenta_o_saldo(client, produto):
    response = _movimentar(
        client, produto["id"], "entrada", 20, observacao="Compra inicial"
    )

    assert response.status_code == 201
    corpo = response.json()
    assert corpo["tipo"] == "entrada"
    assert corpo["quantidade"] == 20
    assert corpo["observacao"] == "Compra inicial"
    assert corpo["produto_id"] == produto["id"]
    assert _produto_atual(client, produto["id"])["quantidade"] == 20


def test_saida_diminui_o_saldo(client, produto):
    _movimentar(client, produto["id"], "entrada", 20)

    response = _movimentar(client, produto["id"], "saida", 8)

    assert response.status_code == 201
    assert _produto_atual(client, produto["id"])["quantidade"] == 12


def test_saida_maior_que_o_saldo_retorna_409(client, produto):
    _movimentar(client, produto["id"], "entrada", 5)

    response = _movimentar(client, produto["id"], "saida", 6)

    assert response.status_code == 409
    assert "Estoque insuficiente" in response.json()["detail"]
    assert _produto_atual(client, produto["id"])["quantidade"] == 5


def test_estoque_baixo_acompanha_as_movimentacoes(client, produto):
    _movimentar(client, produto["id"], "entrada", 6)
    assert _produto_atual(client, produto["id"])["estoque_baixo"] is False

    _movimentar(client, produto["id"], "saida", 1)
    assert _produto_atual(client, produto["id"])["estoque_baixo"] is True


def test_movimentar_produto_inexistente_retorna_404(client):
    response = _movimentar(client, 999, "entrada", 1)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "dados",
    [
        {"tipo": "ajuste", "quantidade": 1},
        {"tipo": "entrada", "quantidade": 0},
        {"tipo": "saida"},
    ],
)
def test_movimentacao_invalida_retorna_422(client, produto, dados):
    response = client.post(f"/produtos/{produto['id']}/movimentacoes", json=dados)

    assert response.status_code == 422


# ---------- GET /produtos/{id}/movimentacoes ----------


def test_historico_vazio(client, produto):
    response = client.get(f"/produtos/{produto['id']}/movimentacoes")

    assert response.status_code == 200
    assert response.json() == []


def test_historico_do_mais_recente_para_o_mais_antigo(client, produto):
    _movimentar(client, produto["id"], "entrada", 10)
    _movimentar(client, produto["id"], "saida", 3)
    _movimentar(client, produto["id"], "saida", 2)

    historico = client.get(f"/produtos/{produto['id']}/movimentacoes").json()

    assert [(m["tipo"], m["quantidade"]) for m in historico] == [
        ("saida", 2),
        ("saida", 3),
        ("entrada", 10),
    ]


def test_historico_mostra_so_o_produto_pedido(client, produto):
    outro = client.post(
        "/produtos", json=NOVO_PRODUTO | {"sku": "LAP-001", "nome": "Lápis"}
    ).json()
    _movimentar(client, produto["id"], "entrada", 10)
    _movimentar(client, outro["id"], "entrada", 4)

    historico = client.get(f"/produtos/{outro['id']}/movimentacoes").json()

    assert len(historico) == 1
    assert historico[0]["quantidade"] == 4


def test_historico_de_produto_inexistente_retorna_404(client):
    assert client.get("/produtos/999/movimentacoes").status_code == 404


# ---------- Integração com a exclusão de produtos ----------


def test_produto_zerado_por_saida_pode_ser_excluido(client, produto):
    _movimentar(client, produto["id"], "entrada", 4)
    assert client.delete(f"/produtos/{produto['id']}").status_code == 409

    _movimentar(client, produto["id"], "saida", 4)

    assert client.delete(f"/produtos/{produto['id']}").status_code == 204
    assert client.get(f"/produtos/{produto['id']}/movimentacoes").status_code == 404
