from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base de todos os modelos ORM. O Alembic lê as tabelas pelo Base.metadata."""
