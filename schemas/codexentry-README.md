# EDDN CodexEntry Schema

## Introduction
Here we document how to take data from an ED `CodexEntry` Journal Event and
properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general 
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event `CodexEntry`.

### Elisions
You MUST remove any key where the key name ends in 
`_Localised`.

You MUST remove the two keys `IsNewEntry` and `NewTraitsDiscovered`.

### Augmentations
#### StarPos
You MUST **add** a `StarPos` key with value of type `array` containing the 
galaxy co-ordinates of the system.  You will need to have obtained these 
from prior event(s) upon the player arriving, or logging into, the system.

e.g. if the system is `Alpha Centauri`:
```json
    "StarPos": [3.03125, -0.09375, 3.15625]
```

#### BodyID and BodyName
You SHOULD attempt to track the BodyName and BodyID where the player is 
and add keys/values for these.

For `BodyName` you MUST retrieve this from the latest `Status.json` data, 
using the `Body` value there-in.

You SHOULD obtain the `BodyID` from an `ApproachBody` or `Location` event.  
You MUST cross-check the `Body` value in this to ensure it has the same 
name as you got from `Status.json`.  One possible issue is binary bodies where
you might get an `ApproachBody` for one before descending towards the other, 
without an additional `ApproachBody` to correct things.

e.g. for `Bestia A 2 a`
```json
    "BodyName": "Bestia A 2 a",
    "BodyID": 15,
```

If you cannot properly obtain the values for `BodyName` or `BodyID` then 
you MUST NOT include them.

## Receivers

As per ['BodyID and BodyName'](#bodyid-and-bodyname) above be aware that 
you are not guaranteed to reveice these values for any given event.  Some 
codex entries will be in space and thus they aren't even relevant.  In 
other cases it may not have been possible to properly determine both of them.

Adjust your local processing accordingly.