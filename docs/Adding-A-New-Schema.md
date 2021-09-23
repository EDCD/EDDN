# Adding A New Schema

## Introduction
As of September 2021 it was decided that all new Journal events will be
added to their own, new, schemas.  This better facilitates defining any
values that should be elided, or augmentations added, without twisting
schema definitions into knots.

In the future we will likely migrate all of the events currently
supported in the journal schema into their own schemas, and later still
deprecate the journal schema.

### Code changes
The only code change required is to
[src/conf/Settings.py](../src/conf/Settings.py) in the
`GATEWAY_JSON_SCHEMAS` dictionary.  This defines the schemas the Gateway
will accept, and the local schema file to check each against.

### Deployment changes
As of 2021-09-23 all of the setup.py deployment code operates on file
globs or directories, so no changes are necessary in order to get new
schema files deployed.
