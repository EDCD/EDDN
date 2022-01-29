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

   If there are no renames of key names for this Schema, then edit the
   `Key Renames` section to contain only the text `None.`.

   Where such renames *are* required do **NOT** attempt to list them all here.
   That would just require updating them both here and in the actual Schema.

   If there are any, call them out in the `description` of the affected
   property in the Schema.

5. In the `Elisions` section clearly document any keys (and thus their values)
   that are in the source data, but that should not be in the resulting EDDN
   message.

   **You do not need to list keys with a `_Localised` suffix.**

6. Do **NOT** remove the `horizons and odyssey flags` section.  It is
   mandatory that they are allowed (but are optional) in any Journal-based
   EDDN Schema.

7. If:
   1. either the source Journal event contains information that includes the
      System name (possibly as `StarSystem` or `SystemName`), **OR** the source
      data contains a `SystemAddress` value,
   2. and a `StarPos` array is *not already present* in the source data.
   
   then you MUST include the `StarPos` section in `Augmentations`.

   If neither key is in the source data then remove the `StarPos` section from
   this document.

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
Many of the key names have a different case defined in this schema, make 
sure you are renaming them as appropriate.

### Elisions
None

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../README-EDDN-schemas.md#horizons-and-odyssey-flags)
over in the main Schema documentation.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event.

## Listeners
The advice above for [Senders](#senders), combined with the actual Schema file *should*
provide all the information you need to process these events.
