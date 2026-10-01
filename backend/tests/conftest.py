from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


def pytest_collection_modifyitems(items):
    # Marca cada teste de acordo com a pasta em que está (tests/unit ou tests/integration).
    # Testes fora dessas pastas não seriam executados pelo CI, então são rejeitados.
    for item in items:
        test_type = Path(item.fspath).relative_to(TESTS_DIR).parts[0]
        if test_type not in ("unit", "integration"):
            raise pytest.UsageError(
                f"{item.nodeid}: testes devem ficar em tests/unit ou tests/integration"
            )
        item.add_marker(getattr(pytest.mark, test_type))
