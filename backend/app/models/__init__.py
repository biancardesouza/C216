# Importar os modelos aqui registra todos eles no Base.metadata,
# que é o que o Alembic compara com o banco no --autogenerate.
from app.models.tarefa import TarefaModel

__all__ = ["TarefaModel"]
