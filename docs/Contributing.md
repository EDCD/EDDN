# Contributing to the EDDN Project

## Introduction

This file is still mostly a stub.

## Text format

The project contains an `.editorconfig` file at its root.  Please either ensure
your editor is taking note of those settings, or cross-check its contents
with the
[editorconfig documentation](https://github.com/editorconfig/editorconfig/wiki/EditorConfig-Properties)
, and ensure your editor/IDE's settings match.

## Code Changes

### Bug Fixes

### Enhancements

## Adding a New Schema

If you think you have a good case for an additional EDDN Schema then there are
several things you should consider:

1. What is the source of the data?  In almost all circumstances the only 
  acceptable sources are the game Journal files and the Frontier CAPI service.
  We do *NOT* want manually entered data being sent over EDDN, it's too prone
  to error.

2. Is the new Schema going to be practically useful ?
   1. What use cases are there for the new data?
   2. Who benefits ?  
   3. What's the likely volume of messages compared to existing Schemas?  If
      there would often be many messages in a short space of time consider
      requiring senders to batch them.  2022-01-28: There's no live example of
      this yet, but see
      [discussion of adding support for FSSSignalDiscovered](https://github.com/EDCD/EDDN/issues/152)
      .
   4. What's the likely size range of the new messages?  The Gateway has a
      limit on the size of the *body* of `/upload/` requests.  Check
      [live branch src/eddn/Gateway.py](https://github.com/EDCD/EDDN/blob/live/src/eddn/Gateway.py)
      `bottle.BaseRequest.MEMFILE_MAX = ...` for the current limit.

3. For CAPI-sourced data you need to keep in mind the possible synchronization
  issues between it and any necessary data augmentations from Journal data.
  This might mean needing to make such augmentations optional.

4. For Journal-sourced data if the source is an event not yet allowed by any
  existing Schema then you MUST define a wholly new Schema for the data.  This
  allows you to fully specify both required and forbidden information in the
  resulting messages.
  The Journal events that are handled in the generic `journal` Schema are only
  there for historical reasons and due to the difficulties in ensuring all
  listeners and senders migrate to separate Schemas in a synchronized manner.

5. Ensure you read
   [the general Schemas README](https://github.com/EDCD/EDDN/blob/live/schemas/README-EDDN-schemas.md)
   so as to be aware of general requirements that your new Schema will need to
   adhere to.

7. You **MUST**
  [open an issue on GitHub](https://github.com/EDCD/EDDN/issues/new)
  in order to propose the new Schema.  If a consensus appears to have been
  reached in comments therein then start work on a Pull Request.

8. There must be at least one working Sender implementation before the Pull
   Request for a new Schema will be merged into the live service.  Experience
   has demonstrated that there are often caveats and gotchas discovered during
   the development of a Sender for a new Schema.
   Often this will end up being a Pull Request against either
   [Elite Dangerous Market Connector](https://github.com/EDCD/EDMarketConnector) 's
   EDDN plugin, or [ED Discovery](https://github.com/EDDiscovery/EDDiscovery).

The Schema files are placed in the `schemas/` directory, located in the root
of the project structure.  They are
[JSON](https://www.json.org/json-en.html)
files, conforming to the
[JSON Schema](https://json-schema.org/)
specification.  As of 2022-01-28 we still use 'draft 04' of this specification.
We are looking into updating to the latest in
[#139 - Update to latest JSON schema version(s) ](https://github.com/EDCD/EDDN/issues/139).

All Schema files MUST be accompanied by a MarkDown formatted README file.

### Always start a new Schema at version 1

The first time a new Schema goes live it should be as version 1.
 - What should policy be on incrementing the version ?  I'm not confident
   anything other than an integer is actually supported - Ath

Any breaking changes **MUST** increment the version number.  Use a git file
rename to update the name of the file.  Examples of such breaking changes
include:

- If you add a new required property.  Senders will need to update.
- If you remove a required property *and making it optional doesn't make
  sense*.  Senders will need to update.  Listeners will need to cope with the
  data no longer being present.
- If you change a property from optional to required or disallowed.  Senders
  will need to update.  Listeners can no longer expect it, if disallowed.

### Necessary file edits

1. Obviously you need to create the new file, in the `schemas/` directory.
  This should be named as per the data source, i.e. Journal `event` value, and
  include the Schema version, and `.json` extension.  You **MUST** fold the
  the `event` value to lower case for this.
  An example is `fssdiscoveryscan-v1.0.json` for adding support for the Journal
  `FSSDiscoveryScan` event.

2. You **MUST** also create the README file for the new Schema.  This is also
  placed in the `schemas/` directory.  The name should match that of the
  Schema file itself, without the version, and with a `.md` extention instead
  of `.json`.
  An example is `fssdiscoveryscan-README.md` documents the
  `fssdiscoveryscan-v1.0.json` Schema file.

3. You will need to add two lines to `src/eddn/conf/Settings.py` in order to
  have the Gateway actually recognise the new Schema.  You are adding to the
  end of the `GATEWAY_JSON_SCHEMAS` dictionary.  Both the live Schema *and*
  the `/test` version **MUST** be added.
  For `fssdiscoveryscan-v1.0.json` you would add:
    ```python
   
        "https://eddn.edcd.io/schemas/fssdiscoveryscan/1"                    : "schemas/fssdiscoveryscan-v1.0.json",
        "https://eddn.edcd.io/schemas/fssdiscoveryscan/1/test"               : "schemas/fssdiscoveryscan-v1.0.json",
    ```
   Please ensure you use the current hostname as per the entries for already
   existing Schemas.  Keep the trailing comma on the final entry, Python
   allows it, and it will reduce the diff on adding any further Schemas.

#### Schema file requirements

1. The file **MUST** actually be valid JSON, without any special extensions
   (so no comments).  Remember that JSON does **not** allow for a trailing
   comma on the last entry of an array or dictionary.
2. The file **MUST** comply with the relevant JSON Schema definition.
3. The file **MUST** actually load using Python's `simplejson` module, as this
   is what the Gateway code uses.  The script `contrib/test-schema.py` will
   check both this and that the validation code doesn't choke on it.
4. All new Schemas **MUST** comply with all requirements outlined in the
   [general Schemas documentation](https://github.com/EDCD/EDDN/blob/live/schemas/README-EDDN-schemas.md).
   If you have a good reason why your new Schema can't and shouldn't comply
   with any such then consensus will need to be achieved on changing those
   requirements and/or allowing the exception.
5. If the data source is a game Journal event then you **MUST** include the
   `event` key and its value as in the source data.  This might seem redundant
   when we mandate a separate Schema for any newly handled Journal event, but
   it does no harm and might make data handling for Listeners easier, i.e.
   they can just pass all "oh, that's from Journal data" messages through the
   same initial handling.

#### Schema README requirements

The per-Schema README **MUST** give both Senders and Listeners sufficient
information to correctly handle the pertinent data.  You do not need to repeat
anything already specified in the general Schema README.  Referring to it via
MarkDown linking is helpful.

1. The reason(s) for any augmentations to a message must be clearly explained.
   1. **DO** outline where the additional data comes from.  e.g. `StarPos`
      added to many events should come from a prior `Location`, `FSDJump` or
      `CarrierJump` Journal event.

2. The reason(s) why any property is optional must be clearly explained.
   Perhaps it's not always present in the source data.

3. The reason(s) why any data in the source is not in the message, i.e. because
   it's personal to the player, or maybe it's just not useful (always the same
   in every instance of the source data).

4. If your Schema only works whilst not complying with any main Schema 
   requirements, and this has been approved, then you need to explicitly
   document which requirement(s) are waived and why.

5. If you use another Schema's README as the basis for yours then you MUST
   remove any text that isn't relevant to your Schema.
