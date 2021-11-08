"""Verify that all the current schema files actually load."""

import pathlib
import sys

import simplejson

# From parent of where this script is
script_path = pathlib.Path(sys.argv[0])
root_dir = script_path.parent.parent

# Take every file in the schemas directory
schemas_dir = root_dir / 'schemas'
failures = 0
for schema_file in schemas_dir.glob('*-v*.*.json'):
    # print(f'Schema: {schema_file}')
    with open(schema_file, 'r') as sf:
        try:
            json = simplejson.load(sf)

        except simplejson.JSONDecodeError as e:
            print(f'Failed to load {schema_file}:\n{e!r}')
            failures += 1

if failures > 0:
    exit(-1)
