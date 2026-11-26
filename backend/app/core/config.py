from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Estoque API"
    app_version: str = "0.1.0"
    # Padrão para desenvolvimento local, com o PostgreSQL do Docker Compose.
    database_url: str = "postgresql+psycopg://estoque:estoque@localhost:5432/estoque"


settings = Settings()
