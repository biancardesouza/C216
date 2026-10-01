import pytest
from pydantic import ValidationError

from app.schemas.tarefa import TarefaCreate, TarefaPatch


def test_tarefa_create_defaults():
    tarefa = TarefaCreate(titulo="Estudar")

    assert tarefa.descricao is None
    assert tarefa.concluida is False


@pytest.mark.parametrize("titulo", ["", "x" * 101])
def test_tarefa_create_rejects_invalid_titulo(titulo):
    with pytest.raises(ValidationError):
        TarefaCreate(titulo=titulo)


def test_tarefa_patch_tracks_only_sent_fields():
    patch = TarefaPatch(concluida=True)

    assert patch.model_dump(exclude_unset=True) == {"concluida": True}


def test_tarefa_patch_allows_clearing_descricao():
    patch = TarefaPatch(descricao=None)

    assert patch.model_dump(exclude_unset=True) == {"descricao": None}


@pytest.mark.parametrize("field", ["titulo", "concluida"])
def test_tarefa_patch_rejects_null_required_fields(field):
    with pytest.raises(ValidationError):
        TarefaPatch(**{field: None})


def test_tarefa_patch_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        TarefaPatch(prioridade="alta")
