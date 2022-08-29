"""General pytest configuration, including fixtures."""
import os
import pathlib
import sys
from typing import Callable, Optional

import pytest


@pytest.fixture()
def eddn_message() -> Callable:
    """Load and supply a test message from the on-disk collection."""
    def _method(msg_type: str) -> Optional[str]:
        path = pathlib.Path('tests/eddn_message/' + msg_type + '.json')
        with open(path, 'r') as eddn_message:
            return eddn_message.read()

    return _method


@pytest.fixture
def fix_sys_path() -> None:
    """Set up an eddn.Gateway import."""
    # Tests don't include the directory that `pytest` is run from on sys.path
    sys.path.append(os.getcwd())


@pytest.fixture(scope="session")
def eddn_gateway():
    """Set up an eddn.Gateway import."""
    import eddn.Gateway

    class CLArgs:
        config = False

    cl_args = CLArgs()
    eddn.Gateway.load_config(cl_args)
    eddn.Gateway.configure()

    return eddn.Gateway


@pytest.fixture
def bottle_response() -> object:
    """Mock a `bottle.response` enough for tests."""
    class BottleResponseMock:
        status: int = 200

    return BottleResponseMock()
