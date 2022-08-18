import os
import sys

# Tests don't include the directory that `pytest` is run from on sys.path
sys.path.append(os.getcwd())

import eddn.Gateway

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
