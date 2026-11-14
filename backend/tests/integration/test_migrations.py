from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import inspect


def test_migrations_create_tarefas_table(engine):
    columns = {c["name"]: c for c in inspect(engine).get_columns("tarefas")}

    assert set(columns) == {"id", "titulo", "descricao", "concluida"}
    assert columns["titulo"]["nullable"] is False
    assert columns["descricao"]["nullable"] is True


def test_migrations_create_items_table_with_unique_nome(engine):
    inspector = inspect(engine)
    columns = {c["name"]: c for c in inspector.get_columns("items")}
    indexes = {i["name"]: i for i in inspector.get_indexes("items")}

    assert set(columns) == {"id", "nome", "descricao"}
    assert not columns["nome"]["nullable"]
    assert not columns["descricao"]["nullable"]
    assert indexes["uq_items_nome_lower"]["unique"]


def test_database_is_at_latest_revision(engine, alembic_config):
    head = ScriptDirectory.from_config(alembic_config).get_current_head()

    with engine.connect() as connection:
        current = connection.exec_driver_sql(
            "SELECT version_num FROM alembic_version"
        ).scalar()

    assert current == head


def test_migrations_downgrade_and_upgrade_again(engine, alembic_config):
    command.downgrade(alembic_config, "base")
    assert not inspect(engine).has_table("tarefas")
    assert not inspect(engine).has_table("items")

    command.upgrade(alembic_config, "head")
    assert inspect(engine).has_table("tarefas")
    assert inspect(engine).has_table("items")
