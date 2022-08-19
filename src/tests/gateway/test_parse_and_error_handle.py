"""Tests for eddn.Gateway.parse_and_error_handle."""
import os
import sys
from typing import Callable

import pytest


@pytest.fixture
def fix_sys_path() -> None:
    """Set up an eddn.Gateway import."""
    # Tests don't include the directory that `pytest` is run from on sys.path
    sys.path.append(os.getcwd())


@pytest.fixture(scope='module')
def eddn_gateway():
    """Set up an eddn.Gateway import."""
    import eddn.Gateway

    class CLArgs:
        config = False

    cl_args = CLArgs()
    eddn.Gateway.load_config(cl_args)
    eddn.Gateway.configure()

    return eddn.Gateway


def test_invalid_json(fix_sys_path, eddn_gateway, eddn_message: Callable) -> None:
    """Test invalid JSON input."""
    msg = eddn_message('invalid_json')
    res = eddn_gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith("FAIL: JSON parsing: ")


def test_outdated_schema(fix_sys_path, eddn_gateway, eddn_message: Callable) -> None:
    """Test attempt to use an outdated schema."""
    msg = eddn_message('plain_outdated_schema')
    res = eddn_gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith(
        "FAIL: Outdated Schema: The schema you have used is no longer supported."
        " Please check for an updated version of your application."
    )


def test_fail_validation_no_softwarename(fix_sys_path, eddn_gateway, eddn_message: Callable) -> None:
    """Test detecting a message with no softwareName in the message."""
    msg = eddn_message('plain_no_softwarename')
    res = eddn_gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith("FAIL: Schema Validation: [<ValidationError: \"'softwareName' is a required property\">]")


def test_valid_journal_scan(fix_sys_path, eddn_gateway, eddn_message: Callable) -> None:
    """Test a valid journal/1, `event == 'Scan'` message."""
    msg = eddn_message('plain_journal_scan_valid')
    res = eddn_gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res == "OK"
