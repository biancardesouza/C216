from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou de um arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "C216 Backend"
    app_version: str = "0.1.0"
    # Valor padrão para rodar localmente com o PostgreSQL do Docker Compose.
    database_url: str = "postgresql+psycopg://c216:c216@localhost:5432/c216"
    # Origens que podem chamar a API pelo navegador, separadas por vírgula.
    # Sempre explícitas (nunca "*"): apenas os endereços do frontend.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origem.strip().rstrip("/")
            for origem in self.cors_origins.split(",")
            if origem.strip()
        ]


settings = Settings()
