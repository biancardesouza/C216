import pytest


def test_read_root_returns_ok(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "application/json" in response.headers["content-type"]


def test_read_root_rejects_post_method(client):
    response = client.post("/")

    assert response.status_code == 405


@pytest.mark.parametrize("path", ["/nao-existe", "/status", "/health"])
def test_unknown_routes_return_404(client, path):
    response = client.get(path)

    assert response.status_code == 404
