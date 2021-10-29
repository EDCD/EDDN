# EDDN BlackMarket Schema

## Introduction
Here we document how to take data from an ED `Market` Journal Event and
properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event `Market`, 
and the additional file, `Market.json`, that it signals the writing of.

So, look for the `Market` event, and when it occurs open and read the 
`Market.json` file which contains the actual data.  Treat *that* data as 
the event.

It *is* also possible to construct this data from a CAPI `/market` query.

### Key Renames
Many of the key names have a different case defined in this schema, make 
sure you are renaming them as appropriate.

#### StarSystem to systemName
Rename the `StarSystem` key name to `systemName`.

### Elisions
#### Remove _Localised key/values
You MUST remove the following key/value pairs from the data:

  - `StationType` key/value.
  - All keys whose name ends with `_Localised`, i.e. the `Name_Localised` 
    key/values in Items.
  - `Producer` key/value pair in Items.
  - `Rare` key/value pair in Items.
  - `id` key/value pair in Items.

#### Item Category
Remove not only the `Category_Localised` key/value, as above, but also the
`Category` key/value pair from each Item.

### Augmentations
#### horizons flag
Use the value from the `LoadGame` event.
#### odyssey flag
Use the value from the `LoadGame` event.
