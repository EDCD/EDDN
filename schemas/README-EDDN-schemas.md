# EDDN Schemas Documentation

EDDN message Schemas are [JSON](https://www.json.org/json-en.html) files
conforming to 'draft 04' of the [JSON Schema](https://json-schema.org/)
specification.

## Canonical location of Schema files

For the EDDN Live service you should always be checking
[the live version of the schemas, and their READMEs](https://github.com/EDCD/EDDN/tree/live/schemas).
Any other version of the Schemas is not guaranteed to be synchronized with
those actually running on the Live service.

## Documentation of Schema files

The Schema files themselves are considered to be the canonical definition of
the required, and allowed, contents of the relevant EDDN message.  There
**SHOULD** be an accompanying README file, e.g. for `commodity-v3.0.json` there
is also a `commodity-README.md` file in the project root `schemas/` directory.

For more general documentation that all developers wanting to either Upload
messages or Listen to the stream of messages from the Relay, please consult
[the Developer documentation](../docs/Developers.md).
