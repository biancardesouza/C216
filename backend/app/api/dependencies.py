from app.repositories.tarefa_repository import TarefaRepository

_tarefa_repository = TarefaRepository()


def get_tarefa_repository() -> TarefaRepository:
    return _tarefa_repository
