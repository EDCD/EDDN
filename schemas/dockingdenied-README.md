# EDDN DockingDenied Schema

## Introduction
Here we document how to take data from an ED `` Journal 
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
`DockingDenied`.

Examples:

```json
{
    "timestamp":"2022-06-10T10:09:41Z",
    "event":"DockingDenied",
    "Reason":"RestrictedAccess",
    "MarketID":3706117376,
    "StationName":"V7G-T1G",
    "StationType":"FleetCarrier"
}
```

### Augmentations
#### horizons and odyssey flags
Please read [horizons and odyssey flags](../docs/Developers.md#horizons-and-odyssey-flags)
in the Developers' documentation.

#### gameversion and gamebuild
You **MUST** always set these as per [the relevant section](../docs/Developers.md#gameversions-and-gamebuild)
of the Developers' documentation.
