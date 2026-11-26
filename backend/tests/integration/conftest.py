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

# Banco exclusivo dos testes, para nunca apagar os dados reais do estoque.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://estoque:estoque@localhost:5432/estoque_test",
)
ALEMBIC_INI = Path(__file__).parents[2] / "alembic.ini"


def _criar_banco_se_nao_existir(url: str) -> None:
    url_banco = make_url(url)
    # CREATE DATABASE não roda dentro de transação, por isso o AUTOCOMMIT.
    admin = create_engine(
        url_banco.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin.connect() as conexao:
        existe = conexao.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"),
            {"nome": url_banco.database},
        )
        if not existe:
            conexao.execute(text(f'CREATE DATABASE "{url_banco.database}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def alembic_config():
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    return config


@pytest.fixture(scope="session")
def engine(alembic_config):
    # A estrutura do banco de testes é criada pelas próprias migrações.
    _criar_banco_se_nao_existir(TEST_DATABASE_URL)
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    # Cada teste começa com as tabelas vazias e os ids reiniciados.
    with engine.begin() as conexao:
        conexao.execute(text("TRUNCATE TABLE produtos RESTART IDENTITY"))


@pytest.fixture
def session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    def get_db_de_teste():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_de_teste
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
