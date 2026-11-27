from alembic import command
from sqlalchemy import inspect


def _colunas(engine, tabela):
    return {coluna["name"] for coluna in inspect(engine).get_columns(tabela)}


def test_migracoes_criam_tabela_produtos(engine):
    assert _colunas(engine, "produtos") == {
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


def test_migracoes_criam_tabela_movimentacoes(engine):
    assert _colunas(engine, "movimentacoes") == {
        "id",
        "produto_id",
        "tipo",
        "quantidade",
        "observacao",
        "criado_em",
    }


def test_movimentacoes_referencia_produtos_com_cascade(engine):
    [chave] = inspect(engine).get_foreign_keys("movimentacoes")

    assert chave["referred_table"] == "produtos"
    assert chave["constrained_columns"] == ["produto_id"]
    assert chave["options"]["ondelete"] == "CASCADE"


def test_downgrade_e_upgrade_funcionam(alembic_config, engine):
    command.downgrade(alembic_config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]

    command.upgrade(alembic_config, "head")
    assert {"produtos", "movimentacoes"} <= set(inspect(engine).get_table_names())
