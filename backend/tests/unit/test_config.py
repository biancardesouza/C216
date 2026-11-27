from app.core.config import Settings


def test_settings_tem_valores_padrao():
    config = Settings(_env_file=None)

    assert config.app_name == "Estoque API"
    assert config.app_version == "0.1.0"
    assert config.database_url.startswith("postgresql+psycopg://")


def test_settings_le_variaveis_de_ambiente(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Outro Nome")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:s@host:5432/banco")

    config = Settings(_env_file=None)

    assert config.app_name == "Outro Nome"
    assert config.database_url == "postgresql+psycopg://u:s@host:5432/banco"


def test_cors_origins_vira_lista_limpa():
    config = Settings(
        _env_file=None,
        cors_origins=" http://localhost:5173/ , http://exemplo.com,, ",
    )

    assert config.cors_origins_list == ["http://localhost:5173", "http://exemplo.com"]
