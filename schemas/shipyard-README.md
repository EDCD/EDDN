# EDDN Shipyard Schema

## Introduction
Here we document how to take data from an ED `Shipyard` Journal
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event
`Shipyard`.

You MAY also source this data from the CAPI `/shipyard` endpoint.  See
[commodity-README.md#using-capi-data](commodity-README.md#using-capi-data)
for guidance on this.

 You only need the `name` key's value for each member of the `PriceList` 
array (if using Journal, it will be from the `ships` array if using CAPI 
data).

When using CAPI data *include* ships listed in the `"unavailable_list"` 
property (i.e. available at this station, but not to this Cmdr).

This list of ship names will go in the `ships` array in the EDDN message.

### Key Renames
Many of the key names have a different case defined in this schema, make
sure you are renaming them as appropriate.

### Elisions
There are no elisions in this schema.

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.
