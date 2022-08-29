"""Test Gateway.handle_upload()."""
from typing import Callable


def test_plain_message(fix_sys_path, eddn_gateway, eddn_message: Callable) -> None:
    """Test eddn.Gateway with a plain message."""
    ####################################################################
    # Mock a bottle 'response' enough to accept setting status
    ####################################################################
    class BottleResponseMock:
        status: int = 200
    ####################################################################

    msg = eddn_message("plain_journal_scan_valid")
    resp_str = eddn_gateway.handle_upload(
        headers={
            "Content-Type": "application/json"
        },
        body=msg.encode(encoding="utf-8"),
        response=BottleResponseMock()
    )

    print(f"{resp_str=}")
    assert resp_str.startswith("OK")
