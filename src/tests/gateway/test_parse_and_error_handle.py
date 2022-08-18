import os
import sys

# Tests don't include the directory that `pytest` is run from on sys.path
sys.path.append(os.getcwd())

import eddn.Gateway

###########################################################################
# Mock up a cl_args enough to get the configuration loaded
###########################################################################
class CLArgs:
    config = False

cl_args = CLArgs()
eddn.Gateway.load_config(cl_args)
eddn.Gateway.configure()
###########################################################################

def test_bad_json():
    msg = "{not real json"
    res = eddn.Gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith("FAIL: JSON parsing: ")

def test_outdated_schema():
    msg = """
{
    "$schemaRef": "http://schemas.elite-markets.net/eddn/journal/1",
    "header": {
        "uploaderID": "outdated schema",
        "softwareName": "pytest:Gateway.parse_and_error_handle",
        "softwareVersion": "v0.0.1"
    },
    "message": {
	}
}
    """
    res = eddn.Gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith("FAIL: Outdated Schema: The schema you have used is no longer supported. Please check for an updated version of your application.")

def test_fail_validation_no_softwarename():
    msg = """
{
    "$schemaRef": "https://eddn.edcd.io/schemas/journal/1",
    "header": {
        "uploaderID": "no softwareName",
        "softwareVersion": "v0.0.1"
    },
    "message": {
	}
}
    """
    res = eddn.Gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res.startswith("FAIL: Schema Validation: [<ValidationError: \"'softwareName' is a required property\">]")

def test_valid_journal_scan():
    msg = """
{
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
}
    """
    res = eddn.Gateway.parse_and_error_handle(msg.encode(encoding="utf-8"))
    assert res == "OK"

