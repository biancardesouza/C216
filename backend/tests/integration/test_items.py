import pytest

from app.models.item import ItemModel

CADERNO = {"nome": "Caderno", "descricao": "Capa dura"}


@pytest.fixture
def item(client):
    return client.post("/items/", json=CADERNO).json()


# GET /items/
def test_list_items_empty(client):
    response = client.get("/items/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_items_ordered_by_id(client):
    client.post("/items/", json={"nome": "Caneta", "descricao": "Azul"})
    client.post("/items/", json=CADERNO)

    response = client.get("/items/")

    assert [i["nome"] for i in response.json()] == ["Caneta", "Caderno"]


# GET /items/{item_id}
def test_get_item(client, item):
    response = client.get(f"/items/{item['id']}")

    assert response.status_code == 200
    assert response.json() == item


def test_get_item_not_found(client):
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item 999 não encontrado"}


# POST /items/
def test_create_item(client):
    response = client.post("/items/", json=CADERNO)

    assert response.status_code == 201
    assert response.json() == {"id": 1, **CADERNO}


def test_create_item_strips_whitespace(client):
    response = client.post("/items/", json={"nome": "  Lápis ", "descricao": " HB "})

    assert response.json() == {"id": 1, "nome": "Lápis", "descricao": "HB"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"nome": "Caderno"},
        {"nome": "ab", "descricao": "curto"},
        {"nome": "   abc   ", "descricao": "   "},
        {"nome": "x" * 51, "descricao": "longo"},
        {"nome": "Caderno", "descricao": "x" * 201},
    ],
)
def test_create_item_rejects_invalid_payload(client, payload):
    response = client.post("/items/", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("nome", ["Caderno", "CADERNO", "  caderno  "])
def test_create_item_rejects_duplicated_nome(client, item, nome):
    response = client.post("/items/", json={"nome": nome, "descricao": "Outro"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe um item com esse nome."}
    assert len(client.get("/items/").json()) == 1


# PUT /items/{item_id}
def test_update_item(client, item):
    payload = {"nome": "Caderno universitário", "descricao": "200 folhas"}

    response = client.put(f"/items/{item['id']}", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": item["id"], **payload}


def test_update_item_keeps_own_nome(client, item):
    response = client.put(
        f"/items/{item['id']}", json={"nome": "CADERNO", "descricao": "Nova"}
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "CADERNO"


def test_update_item_rejects_nome_of_another_item(client, item):
    outro = client.post("/items/", json={"nome": "Caneta", "descricao": "Azul"})

    response = client.put(
        f"/items/{outro.json()['id']}", json={"nome": "caderno", "descricao": "x"}
    )

    assert response.status_code == 409


def test_update_item_not_found(client):
    response = client.put("/items/999", json=CADERNO)

    assert response.status_code == 404


# DELETE /items/{item_id}
def test_delete_item(client, item):
    response = client.delete(f"/items/{item['id']}")

    assert response.status_code == 204
    assert client.get(f"/items/{item['id']}").status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/items/999")

    assert response.status_code == 404


# Persistência
def test_created_item_is_stored_in_database(client, session_factory):
    item = client.post("/items/", json=CADERNO).json()

    with session_factory() as session:
        stored = session.get(ItemModel, item["id"])

    assert stored is not None
    assert stored.nome == "Caderno"
