# EDDN FSSAllBodiesFound Schema

## Introduction
Here we document how to take data from an ED `FSSAllBodiesFound` Journal 
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
The primary data source for this schema is the ED Journal event 
`FSSAllBodiesFound`.

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../docs/Developers.md#horizons-and-odyssey-flags)
in the Developers' documentation.

#### gameversion
You **MUST** always add this field **to the header object**.

1. If you are using Journal files directly then you **MUST** use the value
  of the `gameversion` element from the`Fileheader` event.
2. If you are using the CAPI `/journal` endpoint to retrieve and process
  Journal events then:
   1. You will not have `Fileheader` available.
   2. If `gameversion` is present in the `LoadGame` event, as in 4.0 clients,
     use its value.
   3. If `LoadGame` does not have a `gameversion` element, as with 3.8 Horizons
     clients (up to at least `3.8.0.407`), you **MUST** set `gameversion`, but 
     with the value `"CAPI"`.

#### gamebuild
You **MUST** always add this field **to the header object**.

1. If you are using Journal files directly then you **MUST** use the value
   of the `build` value from the`Fileheader` event.
2. If you are using the CAPI `/journal` endpoint to retrieve and process
   Journal events then:
    1. You will not have `Fileheader` available.
    2. If `build` is present in the `LoadGame` event, as in 4.0 clients, use
      its value.
    3. If `LoadGame` does not have a `build` element, as with 3.8 Horizons
       clients (up to at least `3.8.0.407`), you **MUST** set `gamebuild`, but
       with the value `"CAPI"`.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event.

**You MUST apply a location cross-check, as per
[Other data augmentations](../docs/Developers.md#other-data-augmentations).**
