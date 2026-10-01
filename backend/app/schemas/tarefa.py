from pydantic import BaseModel, ConfigDict, Field, field_validator


class TarefaBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    concluida: bool = False


class TarefaCreate(TarefaBase):
    pass


class TarefaUpdate(TarefaBase):
    pass


class TarefaPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    concluida: bool | None = None

    @field_validator("titulo", "concluida")
    @classmethod
    def nao_pode_ser_nulo(cls, value):
        # Os campos são opcionais no PATCH, mas não podem ser enviados como null.
        if value is None:
            raise ValueError("campo não pode ser nulo")
        return value


class Tarefa(TarefaBase):
    id: int
