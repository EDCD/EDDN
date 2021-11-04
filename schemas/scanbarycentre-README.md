# EDDN ScanBaryCentre Schema

## Introduction
Here we document how to take data from an ED `ScanBaryCentre` Journal
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event
`ScanBaryCentre`.

### Elisions
There are no elisions in this schema.

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the
last `FSDJump`, `CarrierJump`, or `Location` event.
