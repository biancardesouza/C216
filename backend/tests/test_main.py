import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_read_root_returns_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_read_root_returns_expected_body(client):
    response = client.get("/")

    assert response.json() == {"status": "ok"}


def test_read_root_returns_json_content_type(client):
    response = client.get("/")

    assert "application/json" in response.headers["content-type"]


def test_read_root_rejects_post_method(client):
    response = client.post("/")

    assert response.status_code == 405


@pytest.mark.parametrize(
    "path",
    ["/nao-existe", "/status", "/health"],
)
def test_unknown_routes_return_404(client, path):
    response = client.get(path)

    assert response.status_code == 404
