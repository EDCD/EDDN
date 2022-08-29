"""Test Gateway.handle_upload()."""
from typing import Callable


def test_valid_plain_message(
    fix_sys_path,
    eddn_message: Callable,
    eddn_gateway,
    bottle_response
) -> None:
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
        response=bottle_response
    )

    print(f"{resp_str=}")
    assert resp_str.startswith("OK")


def test_invalid_message(
    fix_sys_path,
    eddn_message: Callable,
    eddn_gateway,
    bottle_response
) -> None:
    """Test eddn.Gateway with an invalid message."""
    ####################################################################
    # Mock a bottle 'response' enough to accept setting status
    ####################################################################
    class BottleResponseMock:
        status: int = 200
    ####################################################################

    msg = eddn_message("invalid_json")
    resp_str = eddn_gateway.handle_upload(
        headers={
            "Content-Type": "application/json"
        },
        body=msg.encode(encoding="utf-8"),
        response=bottle_response
    )

    print(f"{resp_str=}")
    assert resp_str.startswith("FAIL: JSON parsing: ")


def test_outdated_schema(
    fix_sys_path,
    eddn_message: Callable,
    eddn_gateway,
    bottle_response
) -> None:
    """Test eddn.Gateway with an invalid message."""
    ####################################################################
    # Mock a bottle 'response' enough to accept setting status
    ####################################################################
    class BottleResponseMock:
        status: int = 200
    ####################################################################

    msg = eddn_message("plain_outdated_schema")
    resp_str = eddn_gateway.handle_upload(
        headers={
            "Content-Type": "application/json"
        },
        body=msg.encode(encoding="utf-8"),
        response=bottle_response
    )

    print(f"{resp_str=}")
    assert resp_str.startswith("FAIL: Outdated Schema: ")
