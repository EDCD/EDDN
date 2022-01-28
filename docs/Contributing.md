# Contributing to the EDDN Project

## Introduction

This document is intended to solidly and usefully define necessary information
pertaining to either improving the EDDN software, or add a new Schema to the
supported set.

## File formatting and editor configuration

The project contains an `.editorconfig` file at its root.  Please either ensure
your editor is taking note of those settings, or cross-check its contents
with the
[editorconfig documentation](https://github.com/editorconfig/editorconfig/wiki/EditorConfig-Properties)
, and ensure your editor/IDE's settings match.

## Branches and other project miscellanea

This project utilises a number of Git branches:

- `live` - The Live service should, outside of brief periods during deployment,
   always be running using the software and supporting files from this branch.
   This is where you should be looking if checking current behaviour of the
   service.

- `master` - This is in effect the staging area for any changes considered
   ready for deployment to the Live service.

- `beta` - Changes under consideration for Live deployment that are currently
   undergoing further testing.  If the Beta service is running it should be
   using this branch, but there might be exceptions.
   There MAY be changes in `develop` *and* `master` that were not merged here.

- `develop` - Usually any Pull Requests will be merged here first.  This is the
   default branch against which any new work should be undertaken.  Urgent
   bug fixes should be the only exception to this, and even then it would only
   happen if `develop` already contains non-Live changes that are not yet
   considered ready for deployment.

You might also see 'work in progress' branches with a `fix/` or `enhancement/`
prefix.

## Code Changes

All code changes should start with
[an open Issue on GitHub](https://github.com/EDCD/EDDN/issues?q=is%3Aissue+is%3Aopen).
If no pertinent issue already exists then please create one.

All Pull Requests should be made against the `develop` branch unless you are
directed to do otherwise.  A Pull Request that is opened without prior
discussion in a relevant Issue is liable to be closed without further
consideration, but exceptions may be made for 'obvious' changes.

## Testing

As of 2022-01-28 the project still does not contain any automated tests,
neither unit or functional.  But you should make every effort to test any
changes, including new Schemas, or changes to existing ones, before opening
a Pull Request for those changes.

`scripts/testing/` exists and might contain some scripts and supporting files
that will be useful in this.

### Bug Fixes

An urgent Bug Fix may be fast-tracked through to the `master` branch, but will
by default go through the `develop` branch.

Where changes pertain to fixing a bug they should be in a branch named as per
the convention `fix/<issue number>/<brief descrption>`, e.g.
`fix/123/avoid-decompress-crash`.

### Enhancements

Any changes to existing code or supporting files that does not address a bug
is considered an enhancement.  Examples would be:

- Changes to an existing Schema to better support actual game data and
   potential uses by Listeners.  If you're not sure whether the change is an
   Enhancement or Fix, use your best assessment, we won't bite your head off.
- Adding a wholly new Schema.
- Improving the Monitor web page, be that adding extra output or a new way to
  view or manipulate the data presented.

Where changes pertain to adding wholly new functionality, including adding a
new schema, or improving an existing feature, then they should be in a branch
named as per the convention `enhancement/<issue number>/<brief descrption>`
, e.g. `enhancement/234/add-schema-somenewevent`.

## Adding a New Schema

If you think you have a good case for an additional EDDN Schema then there are
several things you should consider:

1. Ensure you read
   [the general Schemas README](https://github.com/EDCD/EDDN/blob/live/schemas/README-EDDN-schemas.md)
   so as to be aware of general requirements that your new Schema will need to
   adhere to.

   You might also find useful information in the other Schema-specific README
   files.  Certainly check those if you encounter trouble documenting a new
   Schema.

2. What is the source of the data?  In almost all circumstances the only 
   acceptable sources are the game Journal files and the Frontier CAPI service.
   We do *NOT* accept any manually entered data being sent over EDDN, it's too
   prone to error.

   - Do **NOT** blindly trust that the Frontier-provided Journal documentation
      is correct with respect to the current game version.  Gather actual
      examples of Journal output under as varied circumstances as are relevant,
      and base your new Schema on what you learn.
   
   - Remember that there might be differences between data from a player using
      a Horizons version of the game versus an Odyssey version.  This is why
      all Schemas should mandate augmentation with `horizons` and `odyssey`
      flags, but there might be other considerations when defining a Schema.

3. Is the new Schema going to be practically useful ?
   1. What use cases are there for the new data?
   2. Given that nowhere near all players will be running an EDDN
      sender, and even where they do we might still miss some relevant data,
      is this data still useful ?
   
      e.g. the owner of a Fleet Carrier sending data about their buy and sell
      orders is useful, but if they then don't log in again for a while
      there'll be no update to the FC state.  Likewise for an FC jumping
      between systems.
   
      At the very least you should consider, and document, caveats about the
      data for the benefit of Listeners.
   3. Who benefits ?  If the only interested Listener would be a very niche
      project, with no benefit to others, then perhaps you should instead
      consider e.g. an EDMarket Connector plugin that sends to your own
      server ?
   4. What's the likely volume of messages compared to existing Schemas?  If
      there would often be many messages in a short space of time consider
      requiring senders to batch them.  2022-01-28: There's no live example of
      this yet, but see
      [discussion of adding support for FSSSignalDiscovered](https://github.com/EDCD/EDDN/issues/152)
      .
   5. What's the likely size range of the new messages?  The Gateway has a
      limit on the size of the *body* of `/upload/` requests.  Check
      [live branch src/eddn/Gateway.py](https://github.com/EDCD/EDDN/blob/live/src/eddn/Gateway.py)
      `bottle.BaseRequest.MEMFILE_MAX = ...` for the current limit.

4. For CAPI-sourced data you need to keep in mind possible synchronization
   issues between it and any necessary data augmentations from Journal data.
   This might mean needing to make such augmentations optional.

5. For Journal-sourced data if the source is an event not yet allowed by any
   existing Schema then you MUST define a wholly new Schema for the data.  This
   allows you to fully specify both required and forbidden information.

   The Journal events that are handled in the generic `journal` Schema are only
   there for historical reasons and due to the difficulties in ensuring all
   listeners and senders migrate to separate Schemas in a synchronized manner.

6. You **MUST**
   [open an issue on GitHub](https://github.com/EDCD/EDDN/issues/new)
   in order to propose the new Schema.  If a consensus appears to have been
   reached in comments therein then start work on a Pull Request.

7. There must be at least one working Sender implementation before the Pull
   Request for a new Schema will be merged into the Live service.  Experience
   has demonstrated that there are often caveats and gotchas discovered during
   the development of a Sender for a new Schema.

   Often this will end up being a Pull Request against either
   [Elite Dangerous Market Connector](https://github.com/EDCD/EDMarketConnector) 's
   EDDN plugin, or [ED Discovery](https://github.com/EDDiscovery/EDDiscovery).

The Schema files are placed in the `schemas/` directory, located in the root
of the project structure.  See [Schema file requirements](#schema-file-requirements)
for more information.

### Always start a new Schema at version 1

The first time a new Schema goes live it should be as version 1.
 - What should policy be on incrementing the version ?  I'm not confident
   anything other than an integer is supported - Ath

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

1. Obviously you need to create the new file in the `schemas/` directory.
  This should be named as per the data source, i.e. Journal `event` value, and
  include the Schema version, and `.json` extension.  You **MUST** fold the
  the `event` value to lower case for this.
  An example is `fssdiscoveryscan-v1.0.json` for adding support for the Journal
  `FSSDiscoveryScan` event.

2. You **MUST** also create the README file for the new Schema.  This is also
  placed in the `schemas/` directory.  The name should match that of the
  Schema file itself, without the version, and with a `.md` extention instead
  of `.json`.
  An example is `fssdiscoveryscan-README.md` documenting the
  `fssdiscoveryscan-v1.0.json` Schema file.

3. You will need to add two lines to `src/eddn/conf/Settings.py` in order to
  have the Gateway recognise the new Schema.  You are adding to the
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

4. You MUST add a file containing an example **valid** full EDDN message in the
   `scripts/testing/gateway-responses/` directory.
   1. Name the file as per the Schema name.  In the case of only adding a
      single valid message you can use e.g. `newschema.json`.
       1. If adding variants of valid messages then please annotate the
          filename appropriately, e.g. `newschema-valid-inspace.json` and
          `newschema-valid-onbody.json`.
       2. If adding variants that are *invalid* in some manner them name
          the files as e.g. `newschema-invalid-no-starpos.json`.
   2. The file MUST contain the full plain-text of an EDDN upload, as would be
      sent in the body of a request to the `/upload/` endpoint.  Test it with
      the `scripts/testing/gateway-response/test-sender.py` script.
   3. Please have the `$schemaRef` key:value first, followed by the `header`
      dictionary, and only then the `message` dictionary.
   4. Base the `message` part of this on actual source data, e.g. a line
      from a relevant Journal file.
   5. Ensure the message `timestamp` value is sane, i.e. from a time period
      in which the game was providing this data.
   6. Ensure any data added as an augmentation is correct, i.e.
      the proper co-ordinates of the named StarSystem in StarPos.

   This will aid in confirming that the new schema actually works for a valid
   message.  You MAY add additional examples that are invalid in various ways
   that the schema will detect, but this is not required.

#### Schema file requirements


1. The file **MUST** be valid [JSON](https://www.json.org/json-en.html),
   without any special extensions (so no comments).  Remember that JSON does
   **not** allow for a trailing comma on the last entry of an array or
   dictionary.
2. The file **MUST** comply with the relevant
   [JSON Schema](https://json-schema.org/) definition.

   As of 2022-01-28 we still use 'draft 04' of this specification.
   We are looking into updating to the latest in
   [#139 - Update to latest JSON schema version(s) ](https://github.com/EDCD/EDDN/issues/139).
3. The file **MUST** load using Python's `simplejson` module, as this
   is what the Gateway code uses.  The script `contrib/test-schema.py` will
   check both this and that the validation code doesn't choke on it.
4. All new Schemas **MUST** comply with all requirements outlined in the
   [general Schemas documentation](https://github.com/EDCD/EDDN/blob/live/schemas/README-EDDN-schemas.md).
   If you have a good reason why your new Schema can't and shouldn't comply
   with these requirements, then consensus will need to be achieved on changing
   those requirements and/or allowing the exception.
5. If the data source is a game Journal event then you **MUST** include the
   `event` key and its value as in the source data.  This might seem redundant
   when we mandate a separate Schema for any newly handled Journal event, but
   it does no harm and might make data handling for Listeners easier, i.e.
   they can just pass all "oh, that's from Journal data" messages through the
   same initial handling.
6. All Schema files MUST be accompanied by a MarkDown formatted
   [README file](#schema-readme-requirements).

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
