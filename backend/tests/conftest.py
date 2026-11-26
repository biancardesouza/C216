from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
TIPOS_DE_TESTE = ("unit", "integration")


def pytest_collection_modifyitems(items):
    # Cada teste recebe o marcador da pasta onde está (unit ou integration),
    # o que permite rodar só um dos grupos com "pytest -m unit", por exemplo.
    for item in items:
        tipo = Path(item.fspath).relative_to(TESTS_DIR).parts[0]
        if tipo not in TIPOS_DE_TESTE:
            raise pytest.UsageError(
                f"{item.nodeid}: coloque o teste em tests/unit ou tests/integration"
            )
        item.add_marker(getattr(pytest.mark, tipo))
