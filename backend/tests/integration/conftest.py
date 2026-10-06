import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_tarefa_repository
from app.main import app
from app.repositories.tarefa_repository import TarefaRepository


@pytest.fixture
def client():
    # Cada teste recebe um repositório novo, evitando estado compartilhado entre testes.
    repository = TarefaRepository()
    app.dependency_overrides[get_tarefa_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def tarefa(client):
    response = client.post(
        "/tarefas", json={"titulo": "Estudar FastAPI", "descricao": "Prática 4"}
    )
    return response.json()
