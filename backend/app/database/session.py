from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# pool_pre_ping descarta conexões que o PostgreSQL já encerrou (ex.: após reiniciar).
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Abre uma sessão por requisição e garante que ela seja fechada ao final."""
    with SessionLocal() as session:
        yield session
