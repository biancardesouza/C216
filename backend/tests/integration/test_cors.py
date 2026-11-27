import pytest

ORIGEM_DO_FRONTEND = "http://localhost:5173"


def _preflight(client, origem, metodo):
    # Antes de um PUT/DELETE/POST com JSON, o navegador pergunta à API (OPTIONS)
    # se aquela origem pode usar aquele método.
    return client.options(
        "/produtos",
        headers={
            "Origin": origem,
            "Access-Control-Request-Method": metodo,
            "Access-Control-Request-Headers": "content-type",
        },
    )


@pytest.mark.parametrize("metodo", ["GET", "POST", "PUT", "DELETE"])
def test_preflight_libera_metodos_usados_pelo_frontend(client, metodo):
    response = _preflight(client, ORIGEM_DO_FRONTEND, metodo)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ORIGEM_DO_FRONTEND
    assert metodo in response.headers["access-control-allow-methods"]


def test_preflight_recusa_metodo_nao_usado(client):
    response = _preflight(client, ORIGEM_DO_FRONTEND, "PATCH")

    assert response.status_code == 400


def test_preflight_recusa_origem_desconhecida(client):
    response = _preflight(client, "http://site-malicioso.com", "GET")

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_resposta_simples_inclui_cabecalho_cors(client):
    response = client.get("/produtos", headers={"Origin": ORIGEM_DO_FRONTEND})

    assert response.headers["access-control-allow-origin"] == ORIGEM_DO_FRONTEND
