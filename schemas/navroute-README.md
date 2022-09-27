# EDDN NavRoute Schema

## Introduction
Here we document how to take data from an ED `NavRoute` Journal
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
The primary data source for this schema is the `NavRoute.json` file.  That 
it has been freshly written is signalled by the ED Journal event `NavRoute`.

So, monitor the Journal as normal, and when you see a `NavRoute` event open 
the `NavRoute.json` file for reading, read it, and close it again.  Use the 
data you got from reading this file, not merely the Journal event.

The primary data to be sent is the `Route` array from the contents of the 
separate file.

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
