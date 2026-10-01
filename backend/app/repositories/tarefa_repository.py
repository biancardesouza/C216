from app.schemas.tarefa import Tarefa, TarefaCreate, TarefaPatch, TarefaUpdate


class TarefaRepository:
    """Repositório em memória para o recurso Tarefa."""

    def __init__(self) -> None:
        self._tarefas: dict[int, Tarefa] = {}
        self._next_id = 1

    def list(
        self, concluida: bool | None = None, offset: int = 0, limit: int = 10
    ) -> list[Tarefa]:
        tarefas = list(self._tarefas.values())
        if concluida is not None:
            tarefas = [tarefa for tarefa in tarefas if tarefa.concluida == concluida]
        return tarefas[offset : offset + limit]

    def get(self, tarefa_id: int) -> Tarefa | None:
        return self._tarefas.get(tarefa_id)

    def create(self, data: TarefaCreate) -> Tarefa:
        tarefa = Tarefa(id=self._next_id, **data.model_dump())
        self._tarefas[tarefa.id] = tarefa
        self._next_id += 1
        return tarefa

    def replace(self, tarefa_id: int, data: TarefaUpdate) -> Tarefa | None:
        if tarefa_id not in self._tarefas:
            return None
        tarefa = Tarefa(id=tarefa_id, **data.model_dump())
        self._tarefas[tarefa_id] = tarefa
        return tarefa

    def update(self, tarefa_id: int, data: TarefaPatch) -> Tarefa | None:
        tarefa = self._tarefas.get(tarefa_id)
        if tarefa is None:
            return None
        updated = tarefa.model_copy(update=data.model_dump(exclude_unset=True))
        self._tarefas[tarefa_id] = updated
        return updated

    def delete(self, tarefa_id: int) -> bool:
        return self._tarefas.pop(tarefa_id, None) is not None
