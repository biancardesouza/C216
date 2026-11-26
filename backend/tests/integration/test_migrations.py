from alembic import command
from sqlalchemy import inspect


def test_migracoes_criam_tabela_produtos(engine):
    colunas = {coluna["name"] for coluna in inspect(engine).get_columns("produtos")}

    assert colunas == {
        "id",
        "sku",
        "nome",
        "categoria",
        "preco",
        "quantidade",
        "estoque_minimo",
        "criado_em",
        "atualizado_em",
    }


def test_downgrade_e_upgrade_funcionam(alembic_config, engine):
    command.downgrade(alembic_config, "base")
    assert "produtos" not in inspect(engine).get_table_names()

    command.upgrade(alembic_config, "head")
    assert "produtos" in inspect(engine).get_table_names()
