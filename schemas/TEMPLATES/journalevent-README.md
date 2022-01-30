!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!! STOP !!!

!! These are not valid MarkDown comments.

!! You MUST read, comply with, and then remove all of these lines to have a

!! valid Schema README file.

1. Be careful if using any existing Schema, or its README, as reference for a
   new Schema.  Some of them will have some departures from best practices for
   historical reasons.  It's usually not easy to co-ordinate all Listeners and
   Senders smoothly updating to a new version of a Schema, so less than ideal
   requires/optional/disallowed definitions might be present in older Schemas.

   [The main Schema documentation](../README-EDDN-schemas.md) is the canonical
   authority.
2. Replace all instances of `NewJournalEvent` with the name of the actual
   Journal event's Schema you are documenting.  This should have the case
   preserved as per how it appears in actual game Journal files.
3. Replace all instances of `newjournalevent` with the lower-case folded
   version of this Schema's Journal event name.
4. For new Journal-based schemas no key renames should be necessary.

   If there are no renames of key names for this Schema, then remove the
   `Key Renames` section.

   Where such renames *are* required do **NOT** attempt to list them all here.
   That would just require updating them both here and in the actual Schema.

   If there are any, then the affected property object should contain a key
   named `renamed` with its value being the original key name in the source
   data, e.g. in the commodity/3 schema a Journal `StarSystem` is renamed
   to `systemName` so we have:

      ```json
        "message": {
            "type"                  : "object",
            "additionalProperties"  : false,
            "required"              : [ "systemName", "stationName", "marketId", "timestamp", "commodities" ],
            "properties"            : {
                "systemName": {
                    "type"      : "string",
                    "renamed"   : "StarSystem",
                    "minLength" : 1
                },

      ```

5. Do **NOT** remove the `horizons and odyssey flags` section.  It is
   mandatory that they are allowed (but are optional) in any Journal-based
   EDDN Schema.

6. If both:
   1. either the source Journal event contains information that includes the
      System name (possibly as `StarSystem` or `SystemName`), **OR** the source
      data contains a `SystemAddress` value,
   2. and a `StarPos` array is *not already present* in the source data.
   
   then you MUST include the `StarPos` section in `Augmentations` and add
   `StarPos` to the `required` message properties in the Schema file.

   If neither key is in the source data then remove the `StarPos` section from
   this document and the Schema file.

7. Do **NOT** add an 'Elisions'/'Removals' section.  Leave the Schema as the
   sole reference for any data that is in the source but should not be in the
   final EDDN message.

The line:

    # EDDN NewJournalEvent Schema

below should ultimately be the first line in this file, after required edits.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# EDDN NewJournalEvent Schema

## Introduction
Here we document how to take data from an ED `NewJournalEvent` Journal 
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

If you find any discrepancies between what this document says and what is
defined in the relevant Schema file, then you should, in the first instance,
assume that it is the Schema file that is correct.
**PLEASE open
[an issue on GitHub](https://github.com/EDCD/EDDN/issues/new/choose)
to report any such anomalies you find so that we can check and resolve the
discrepancy.**

## Senders
The data source for this schema is the ED Journal event `NewJournalEvent`.

### Key Renames
Some key names in this Schema are different from how they appear in the source
Journal data.  Look for keys where the object contains a `renamed` key - the
value is what the name would have been in the source Journal data.

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../../docs/Developers.md#horizons-and-odyssey-flags)
over in the Developers' documentation.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event.

## Listeners
The advice above for [Senders](#senders), combined with the actual Schema file
*should* provide all the information you need to process these events.
