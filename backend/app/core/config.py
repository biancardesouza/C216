from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou de um arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "C216 Backend"
    app_version: str = "0.1.0"
    # Valor padrão para rodar localmente com o PostgreSQL do Docker Compose.
    database_url: str = "postgresql+psycopg://c216:c216@localhost:5432/c216"


settings = Settings()
