from app.core.config import Settings


def test_settings_tem_valores_padrao():
    config = Settings(_env_file=None)

    assert config.app_name == "Estoque API"
    assert config.app_version == "0.1.0"


def test_settings_le_variaveis_de_ambiente(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Outro Nome")

    assert Settings(_env_file=None).app_name == "Outro Nome"
