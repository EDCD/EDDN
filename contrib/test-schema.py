"""Check if a file's JSON message passes the given schema."""
import simplejson
import sys
from jsonschema import FormatChecker, ValidationError
from jsonschema import validate as json_validate

if len(sys.argv) < 2:
    print(
f"""
Usage: {sys.argv[0]} <schema file name> [<test data file name>]

Note that the entire file will be loaded by simpljson.load() and should
only contain one JSON object.
"""
    )
    sys.exit(-1)

schema_file_name = sys.argv[1]
test_file_name = None
if len(sys.argv) == 3:
    test_file_name = sys.argv[2]

with open(schema_file_name, 'r') as schema_file:
    schema = simplejson.load(schema_file)
    print('Schema file loaded OK...')

    if test_file_name is not None:
        with open(test_file_name, 'r') as test_file:
            test_event = simplejson.load(test_file)

        json_validate(test_event, schema, format_checker=FormatChecker())

        print('Input file validated against schema OK.')
