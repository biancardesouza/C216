from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tarefa import TarefaModel


class TarefaRepository:
    """Acesso aos dados de Tarefa no PostgreSQL via SQLAlchemy.

    Só conhece o modelo ORM e a sessão: não lida com HTTP nem com schemas Pydantic.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self, concluida: bool | None = None, offset: int = 0, limit: int = 10
    ) -> list[TarefaModel]:
        query = select(TarefaModel).order_by(TarefaModel.id)
        if concluida is not None:
            query = query.where(TarefaModel.concluida == concluida)
        return list(self.session.scalars(query.offset(offset).limit(limit)))

    def get(self, tarefa_id: int) -> TarefaModel | None:
        return self.session.get(TarefaModel, tarefa_id)

    def add(self, tarefa: TarefaModel) -> TarefaModel:
        self.session.add(tarefa)
        return self.save(tarefa)

    def save(self, tarefa: TarefaModel) -> TarefaModel:
        self.session.commit()
        self.session.refresh(tarefa)
        return tarefa

    def delete(self, tarefa: TarefaModel) -> None:
        self.session.delete(tarefa)
        self.session.commit()
