# EDDN FSSAllBodiesFound Schema

## Introduction
Here we document how to take data from an ED `FSSAllBodiesFound` Journal 
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event 
`FSSAllBodiesFound`.

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../../docs/Developers.md#horizons-and-odyssey-flags)
over in the Developers' documentation.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event.
