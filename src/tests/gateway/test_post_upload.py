"""Tests via `bottle` endpoints."""
import os
import sys
from typing import Callable

from webtest import TestApp

# Tests don't include the directory that `pytest` is run from on sys.path
sys.path.append(os.getcwd())

import eddn.Gateway  # noqa: E402 # Has to be after that sys.path fixup


def test_plain_message(eddn_message: Callable) -> None:
    """Test eddn.Gateway /upload/ with a plain message."""
    eddn.Gateway.setup_bottle_app()

    # Wrap the real app in a TestApp object
    test_app = TestApp(eddn.Gateway.app)
    assert test_app is not None

    dc_msg = test_app.post(
        '/upload/',
        params=eddn_message('plain_journal_scan_valid'),
        headers={
            'Content-Type': 'application/json'
        },
    )

    assert dc_msg == 'OK'
