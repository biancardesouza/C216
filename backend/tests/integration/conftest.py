import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.database.session import get_db
from app.main import app

# Os testes usam um banco separado (c216_test) para nunca apagar os dados da aplicação.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+psycopg://c216:c216@localhost:5432/c216_test"
)
ALEMBIC_INI = Path(__file__).parents[2] / "alembic.ini"


def _create_database_if_missing(url: str) -> None:
    database_url = make_url(url)
    admin_engine = create_engine(
        database_url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin_engine.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": database_url.database},
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{database_url.database}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def alembic_config():
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    return config


@pytest.fixture(scope="session")
def engine(alembic_config):
    # Recria a estrutura do banco do zero usando as migrations do Alembic.
    _create_database_if_missing(TEST_DATABASE_URL)
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    # Limpa os dados (e reinicia os ids) para que cada teste comece com o banco vazio.
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE tarefas RESTART IDENTITY"))


@pytest.fixture
def session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def tarefa(client):
    response = client.post(
        "/tarefas", json={"titulo": "Estudar FastAPI", "descricao": "Prática 5"}
    )
    return response.json()
