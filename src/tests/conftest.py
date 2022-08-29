"""General pytest configuration, including fixtures."""
import os
import sys
from typing import Callable, Optional

import pytest

"""A dictionary of test messages, all in string form."""
test_messages = {
    'invalid_json': '{not real json',

    'plain_outdated_schema': '''{
        "$schemaRef": "http://schemas.elite-markets.net/eddn/journal/1",
        "header": {
            "uploaderID": "outdated schema",
            "softwareName": "pytest:Gateway.parse_and_error_handle",
            "softwareVersion": "v0.0.1"
        },
        "message": {
        }
    }''',

    'plain_no_softwarename': '''{
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1",
        "header": {
            "uploaderID": "no softwareName",
            "softwareVersion": "v0.0.1"
        },
        "message": {
        }
    }''',

    'plain_journal_scan_valid': '''{
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1",
        "header": {
            "uploaderID": "valid journal message",
            "softwareName": "pytest:Gateway.parse_and_error_handle",
            "softwareVersion": "v0.0.1"
        },
        "message": {
            "timestamp":"2021-11-05T15:46:28Z",
            "event":"Scan",
            "StarSystem":"Elphin",
            "StarPos":[-30.12500,8.18750,-17.00000],
            "SystemAddress":3932076118738
        }
    }''',
}


@pytest.fixture
def eddn_message() -> Callable:
    """Supply the requested test message."""
    def _method(msg_type: str) -> Optional[str]:
        return test_messages.get(msg_type)

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
