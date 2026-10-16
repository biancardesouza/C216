from app.models.tarefa import TarefaModel
from app.repositories.tarefa_repository import TarefaRepository
from app.schemas.tarefa import TarefaCreate, TarefaPatch, TarefaUpdate


class TarefaNotFoundError(Exception):
    def __init__(self, tarefa_id: int) -> None:
        super().__init__(f"Tarefa {tarefa_id} não encontrada")
        self.tarefa_id = tarefa_id


class TarefaService:
    """Regras de negócio de Tarefa: converte schemas em modelos e usa o repository."""

    def __init__(self, repository: TarefaRepository) -> None:
        self.repository = repository

    def list(
        self, concluida: bool | None = None, offset: int = 0, limit: int = 10
    ) -> list[TarefaModel]:
        return self.repository.list(concluida=concluida, offset=offset, limit=limit)

    def get(self, tarefa_id: int) -> TarefaModel:
        tarefa = self.repository.get(tarefa_id)
        if tarefa is None:
            raise TarefaNotFoundError(tarefa_id)
        return tarefa

    def create(self, data: TarefaCreate) -> TarefaModel:
        return self.repository.add(TarefaModel(**data.model_dump()))

    def replace(self, tarefa_id: int, data: TarefaUpdate) -> TarefaModel:
        # PUT substitui todos os campos, inclusive os omitidos (que voltam ao padrão).
        return self._apply(tarefa_id, data.model_dump())

    def update(self, tarefa_id: int, data: TarefaPatch) -> TarefaModel:
        # PATCH altera apenas os campos enviados na requisição.
        return self._apply(tarefa_id, data.model_dump(exclude_unset=True))

    def delete(self, tarefa_id: int) -> None:
        self.repository.delete(self.get(tarefa_id))

    def _apply(self, tarefa_id: int, fields: dict) -> TarefaModel:
        tarefa = self.get(tarefa_id)
        for field, value in fields.items():
            setattr(tarefa, field, value)
        return self.repository.save(tarefa)
