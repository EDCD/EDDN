# EDDN ScanOrganic Schema

## Introduction
Here we document how to take data from an ED `ScanOrganic` Journal Event and
properly structure it for sending to EDDN.

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
The primary data source for this schema is the ED Journal event `ScanOrganic`.

### ScanType
The 'Analyse' scan type only triggers when you have the scan tool out for a
long enough duration following your third scan. It's possible to put away the
tool before this completes and the event will then trigger the next time the
tool is used, which could be in another system entirely. For this reason,
it may report incorrect data and is thus excluded from submission.

### Variant
Variant should be reported if present. It was not included in older journal
versions and therefore is not required to facilitate older journal submissions.

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../docs/Developers.md#horizons-and-odyssey-flags)
in the Developers' documentation.

#### gameversion and gamebuild
You **MUST** always set these as per [the relevant section](../docs/Developers.md#gameversions-and-gamebuild)
of the Developers' documentation.

#### StarSystem
You MUST add a StarSystem key/value pair representing the name of the system
this event occurred in. Source this from either Location, FSDJump or
CarrierJump as appropriate.

**You MUST apply a location cross-check, as per
[Other data augmentations](../docs/Developers.md#other-data-augmentations).**

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the
last `FSDJump`, `CarrierJump`, or `Location` event.

**You MUST apply a location cross-check, as per
[Other data augmentations](../docs/Developers.md#other-data-augmentations).**

#### BodyID and BodyName
BodyID is already present in the form of the 'Body' key. This should be
renamed to BodyID to mirror many other events.

You MUST track `BodyName` both from Status.json *and* also from some
Journal events in order to cross-check it before using the `Body` from
Journal events.

The following is correct as of game version 4.0.0.801 (Odyssey initial
release, Update 7, plus one patch).

1. Record `journal_body_name` and `journal_body_id` from the
   `BodyName` and `BodyID` values in `ApproachBody` events.

   This will occur when the player flies below Orbital Cruise altitude
   around a body.
2. Also record these from `Location` events to cover logging in already there.
3. Unset both `journal_body_name` and `journal_body_id` on `LeaveBody` and
   `FSDJump` events.
   Do NOT do so for `SupercruiseEntry`, because a player can enter supercruise
   below max Orbital Cruise altitude and then come back down without a new
   `ApproachBody` event occurring.
4. If Status.json has `BodyName` present, record that as `status_body_name`.

   This key and its value will be present whenever the player comes close
   enough to a body for the Orbital Cruise/Glide HUD elements to appear.
   It will disappear again when they fly back above that altitude, or jump
   away.
5. If Status.json does **not** have `BodyName` then clear `status_body_name`.
