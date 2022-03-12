"""Verify that all the current schema files actually load."""

import pathlib
import sys

import simplejson

# From parent of where this script is
script_path = pathlib.Path(sys.argv[0])
root_dir = script_path.parent.parent

# Take every file in the schemas directory
schemas_dir = root_dir / "schemas"
failures = 0
for schema_file in schemas_dir.glob("*-v*.*.json"):
    with open(schema_file, "r") as sf:
        try:
            json = simplejson.load(sf)

        except simplejson.JSONDecodeError as e:
            print(f"{schema_file}: Failed to load:\n{e!r}\n")
            failures += 1

        else:
            print(f"{schema_file}: OK")

if failures > 0:
    exit(-1)
