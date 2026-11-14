from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_cors_origins_default_points_to_frontend(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    assert Settings(_env_file=None).cors_origins_list == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_cors_origins_reads_comma_separated_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " http://a.com/ , ,http://b.com:8080")

    assert Settings(_env_file=None).cors_origins_list == [
        "http://a.com",
        "http://b.com:8080",
    ]


def test_create_app_uses_configured_origins():
    app = create_app(Settings(cors_origins="http://outro:3000"))

    # O health check não acessa o banco, então dispensa o PostgreSQL.
    with TestClient(app) as client:
        permitido = client.get("/", headers={"Origin": "http://outro:3000"})
        negado = client.get("/", headers={"Origin": "http://localhost:5173"})

    assert permitido.headers["access-control-allow-origin"] == "http://outro:3000"
    assert "access-control-allow-origin" not in negado.headers
