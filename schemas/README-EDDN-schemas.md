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

## General EDDN message outline

Each `message` object must have, at bare minimum:

1. `timestamp` - string date and time in ISO8601 format. Whilst this
   technically allows for any timezone to be cited you SHOULD provide this in
   UTC, aka 'Zulu Time' as in the example above. You MUST ensure that you are
   doing this properly. Do not claim 'Z' whilst actually using a local time
   that is offset from UTC.

   If you are only utilising Journal-sourced data then simply using the
   value from there should be sufficient as the PC game client is meant to
   always be correctly citing UTC for this.  Indeed it has been observed,
   in the Odyssey 4.0.0.1002 client, that with the Windows clock behind UTC
   by 21 seconds both the in-game UI clock *and* the Journal event
   timestamps are still properly UTC to the nearest second.

   Listeners MAY make decisions on accepting data based on this time stamp,
   i.e. "too old".
2. Where the data is sourced from a Journal event please do preserve the
   `event` key and value.  Yes, where we use an event-specific Schema this
   might seem redundant, but it might aid an EDDN listener in streamlining
   their code, and it does no harm.

   Any new Schema based on Journal data **MUST** make `event` a required
   property of the `message` dictionary.
3. At least one other key/value pair representing the data. In general there
   will be much more than this. Consult the
   [Schemas and their documentation](./).

4. Please consult the advice pertaining to
   [horizons and odyssey flags](../docs/Developers.md#horizons-and-odyssey-flags) and include them
   whenever possible.

Because the first versions of some Schemas were defined when only the CAPI
data was available, before Journal files existed, many of the key names chosen
in the Schemas are based on the equivalent in CAPI data, not Journal events.
This means you MUST rename many of the keys from Journal events to match the
Schemas.  Consult the relevant Schema, and its README, for details.

