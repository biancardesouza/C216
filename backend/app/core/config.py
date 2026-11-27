from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Estoque API"
    app_version: str = "0.1.0"
    # Padrão para desenvolvimento local, com o PostgreSQL do Docker Compose.
    database_url: str = "postgresql+psycopg://estoque:estoque@localhost:5432/estoque"
    # Endereços do frontend que podem chamar a API pelo navegador, separados
    # por vírgula. Sempre explícitos, nunca "*".
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origem.strip().rstrip("/")
            for origem in self.cors_origins.split(",")
            if origem.strip()
        ]


settings = Settings()
