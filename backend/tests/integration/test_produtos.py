import pytest

NOVO_PRODUTO = {
    "sku": "CAN-001",
    "nome": "Caneta azul",
    "categoria": "Papelaria",
    "preco": "2.50",
    "estoque_minimo": 10,
}


@pytest.fixture
def produto(client):
    return client.post("/produtos", json=NOVO_PRODUTO).json()


def _dar_entrada(client, produto_id, quantidade):
    client.post(
        f"/produtos/{produto_id}/movimentacoes",
        json={"tipo": "entrada", "quantidade": quantidade},
    )


# ---------- POST /produtos ----------


def test_criar_produto_retorna_201(client):
    response = client.post("/produtos", json=NOVO_PRODUTO)

    assert response.status_code == 201
    corpo = response.json()
    assert corpo["id"] == 1
    assert corpo["sku"] == "CAN-001"
    assert corpo["preco"] == "2.50"
    assert corpo["quantidade"] == 0
    assert corpo["estoque_baixo"] is True
    assert "criado_em" in corpo


def test_criar_ignora_quantidade_enviada(client):
    response = client.post("/produtos", json=NOVO_PRODUTO | {"quantidade": 100})

    assert response.json()["quantidade"] == 0


def test_criar_com_sku_duplicado_retorna_409(client, produto):
    response = client.post(
        "/produtos", json=NOVO_PRODUTO | {"sku": "can-001", "nome": "Outra"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe um produto com o SKU CAN-001."}


@pytest.mark.parametrize(
    "campos",
    [{"sku": "x"}, {"nome": ""}, {"preco": "0"}, {"estoque_minimo": -1}],
)
def test_criar_com_dados_invalidos_retorna_422(client, campos):
    response = client.post("/produtos", json=NOVO_PRODUTO | campos)

    assert response.status_code == 422


def test_criar_sem_campos_obrigatorios_retorna_422(client):
    response = client.post("/produtos", json={})

    assert response.status_code == 422


# ---------- GET /produtos ----------


def test_listar_sem_produtos_retorna_lista_vazia(client):
    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == []


def test_listar_retorna_produtos_por_nome(client):
    client.post("/produtos", json=NOVO_PRODUTO | {"sku": "LAP-001", "nome": "Lápis"})
    client.post("/produtos", json=NOVO_PRODUTO | {"sku": "BOR-001", "nome": "Borracha"})

    nomes = [p["nome"] for p in client.get("/produtos").json()]

    assert nomes == ["Borracha", "Lápis"]


# ---------- GET /produtos/{id} ----------


def test_buscar_produto(client, produto):
    response = client.get(f"/produtos/{produto['id']}")

    assert response.status_code == 200
    assert response.json()["nome"] == "Caneta azul"


def test_buscar_produto_inexistente_retorna_404(client):
    response = client.get("/produtos/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto 999 não encontrado."}


def test_buscar_com_id_invalido_retorna_422(client):
    assert client.get("/produtos/abc").status_code == 422


# ---------- PUT /produtos/{id} ----------


def test_atualizar_produto(client, produto):
    response = client.put(
        f"/produtos/{produto['id']}",
        json=NOVO_PRODUTO | {"nome": "Caneta preta", "preco": "3.00"},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Caneta preta"
    assert response.json()["preco"] == "3.00"
    assert client.get(f"/produtos/{produto['id']}").json()["nome"] == "Caneta preta"


def test_atualizar_nao_altera_quantidade(client, produto):
    _dar_entrada(client, produto["id"], 7)

    response = client.put(
        f"/produtos/{produto['id']}", json=NOVO_PRODUTO | {"quantidade": 0}
    )

    assert response.json()["quantidade"] == 7


def test_atualizar_para_sku_de_outro_produto_retorna_409(client, produto):
    outro = client.post(
        "/produtos", json=NOVO_PRODUTO | {"sku": "LAP-001", "nome": "Lápis"}
    ).json()

    response = client.put(f"/produtos/{outro['id']}", json=NOVO_PRODUTO)

    assert response.status_code == 409


def test_atualizar_produto_inexistente_retorna_404(client):
    response = client.put("/produtos/999", json=NOVO_PRODUTO)

    assert response.status_code == 404


def test_atualizar_com_dados_invalidos_retorna_422(client, produto):
    response = client.put(
        f"/produtos/{produto['id']}", json=NOVO_PRODUTO | {"preco": "-1"}
    )

    assert response.status_code == 422


# ---------- DELETE /produtos/{id} ----------


def test_excluir_produto_sem_estoque_retorna_204(client, produto):
    response = client.delete(f"/produtos/{produto['id']}")

    assert response.status_code == 204
    assert client.get(f"/produtos/{produto['id']}").status_code == 404


def test_excluir_produto_com_estoque_retorna_409(client, produto):
    _dar_entrada(client, produto["id"], 3)

    response = client.delete(f"/produtos/{produto['id']}")

    assert response.status_code == 409
    assert "3 unidade(s)" in response.json()["detail"]
    assert client.get(f"/produtos/{produto['id']}").status_code == 200


def test_excluir_produto_inexistente_retorna_404(client):
    assert client.delete("/produtos/999").status_code == 404
