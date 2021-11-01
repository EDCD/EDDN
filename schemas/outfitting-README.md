# EDDN Outfitting Schema

## Introduction
Here we document how to take data from an ED `Outfitting` Journal
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event
`Outfitting`.

You MAY also source this data from the CAPI `/shipyard` endpoint.  See
[commodity-README.md#using-capi-data](commodity-README.md#using-capi-data)
for guidance on this.

You only need the `name` key's value for each member of the `modules` array.

### Key Renames
Many of the key names have a different case defined in this schema, make
sure you are renaming them as appropriate.

### Elisions
Remove items whose availability depends on the Cmdr's status rather than on the
station. Namely:

- Items that aren't weapons/utilities (`Hpt_*`), standard/internal
  modules (`Int_*`) or armour (`*_Armour_*`) (i.e. bobbleheads, decals,
  paintjobs and shipkits).  This is enforced by the schema.
- Items that have a non-null `"sku"` property, unless
  it's `"ELITE_HORIZONS_V_PLANETARY_LANDINGS"` (i.e. PowerPlay and tech
  broker items).
- The `"Int_PlanetApproachSuite"` module (for historical reasons).

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.