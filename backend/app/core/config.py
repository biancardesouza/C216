from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Estoque API"
    app_version: str = "0.1.0"


settings = Settings()
