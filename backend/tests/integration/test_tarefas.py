import pytest


# GET /tarefas
def test_list_tarefas_empty(client):
    response = client.get("/tarefas")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tarefas_filters_by_concluida(client):
    client.post("/tarefas", json={"titulo": "Aberta"})
    client.post("/tarefas", json={"titulo": "Feita", "concluida": True})

    response = client.get("/tarefas", params={"concluida": True})

    assert response.status_code == 200
    assert [t["titulo"] for t in response.json()] == ["Feita"]


def test_list_tarefas_paginates(client):
    for i in range(5):
        client.post("/tarefas", json={"titulo": f"Tarefa {i}"})

    response = client.get("/tarefas", params={"offset": 1, "limit": 2})

    assert [t["titulo"] for t in response.json()] == ["Tarefa 1", "Tarefa 2"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_tarefas_rejects_invalid_query(client, params):
    response = client.get("/tarefas", params=params)

    assert response.status_code == 422


# GET /tarefas/{tarefa_id}
def test_get_tarefa(client, tarefa):
    response = client.get(f"/tarefas/{tarefa['id']}")

    assert response.status_code == 200
    assert response.json() == tarefa


def test_get_tarefa_not_found(client):
    response = client.get("/tarefas/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarefa 999 não encontrada"}


@pytest.mark.parametrize("tarefa_id", ["0", "-1", "abc"])
def test_get_tarefa_rejects_invalid_id(client, tarefa_id):
    response = client.get(f"/tarefas/{tarefa_id}")

    assert response.status_code == 422


# POST /tarefas
def test_create_tarefa(client):
    response = client.post("/tarefas", json={"titulo": "Nova tarefa"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "titulo": "Nova tarefa",
        "descricao": None,
        "concluida": False,
    }


@pytest.mark.parametrize("payload", [{}, {"titulo": ""}, {"titulo": "x" * 101}])
def test_create_tarefa_rejects_invalid_payload(client, payload):
    response = client.post("/tarefas", json=payload)

    assert response.status_code == 422


# PUT /tarefas/{tarefa_id}
def test_replace_tarefa(client, tarefa):
    payload = {"titulo": "Substituída", "concluida": True}

    response = client.put(f"/tarefas/{tarefa['id']}", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": tarefa["id"],
        "titulo": "Substituída",
        "descricao": None,
        "concluida": True,
    }


def test_replace_tarefa_requires_titulo(client, tarefa):
    response = client.put(f"/tarefas/{tarefa['id']}", json={"concluida": True})

    assert response.status_code == 422


def test_replace_tarefa_not_found(client):
    response = client.put("/tarefas/999", json={"titulo": "Qualquer"})

    assert response.status_code == 404


# PATCH /tarefas/{tarefa_id}
def test_update_tarefa_changes_only_sent_fields(client, tarefa):
    response = client.patch(f"/tarefas/{tarefa['id']}", json={"concluida": True})

    assert response.status_code == 200
    assert response.json() == {**tarefa, "concluida": True}


@pytest.mark.parametrize(
    "payload", [{"titulo": None}, {"concluida": None}, {"campo_invalido": 1}]
)
def test_update_tarefa_rejects_invalid_payload(client, tarefa, payload):
    response = client.patch(f"/tarefas/{tarefa['id']}", json=payload)

    assert response.status_code == 422


def test_update_tarefa_not_found(client):
    response = client.patch("/tarefas/999", json={"concluida": True})

    assert response.status_code == 404


# DELETE /tarefas/{tarefa_id}
def test_delete_tarefa(client, tarefa):
    response = client.delete(f"/tarefas/{tarefa['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/tarefas/{tarefa['id']}").status_code == 404


def test_delete_tarefa_not_found(client):
    response = client.delete("/tarefas/999")

    assert response.status_code == 404
