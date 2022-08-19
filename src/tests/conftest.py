"""General pytest configuration, including fixtures."""
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
