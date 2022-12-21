"""Tests for eddn.Gateway.get_decompressed_message."""
import os
from typing import Callable


def test_plain_message(eddn_message: Callable, monkeypatch) -> None:
    """Test eddn.Gateway.get_decompressed_message() with a plain message."""
    # Tests don't include the directory that `pytest` is run from on sys.path
    print(type(monkeypatch))
    monkeypatch.syspath_prepend(os.getcwd())
    import eddn.Gateway

    eddn.Gateway.setup_bottle_app()
    print(f'{eddn.Gateway.app.__dict__=}')

    msg = eddn_message('journal/1/scan/valid')

    dc_msg = eddn.Gateway.get_decompressed_message(
        {
            'Content-Type': 'application/json',
        },
        msg.encode(encoding='utf-8'),
    )

    assert msg == dc_msg.decode()
