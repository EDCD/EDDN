import sys

import simplejson
import jsonschema

schema_filename = sys.argv[1]
message_filename = sys.argv[2]

schema_file = open(schema_filename, 'r')
schema_data = schema_file.read()
schema = simplejson.loads(schema_data)

message_file = open(message_filename, 'r')
message_data = message_file.read()
message = simplejson.loads(message_data)

jsonschema.validate(message, schema, format_checker=jsonschema.FormatChecker())
