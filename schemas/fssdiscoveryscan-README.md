# EDDN FSSDiscoveryScan Schema

## Introduction
Here we document how to take data from an ED `FSSDiscoveryScan` Journal 
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event 
`FSSDiscoveryScan`.

### Key Renames
Many of the key names have a different case defined in this schema, make 
sure you are renaming them as appropriate.

### Elisions
#### Remove _Localised key/values
All keys whose name ends with `_Localised`, i.e. the `Name_Localised`
key/values in Items.

#### Other Elisions
You MUST remove the following key/value pairs from the data:

  - `Progress` key/value pair.

#### Item Category
Remove not only the `Category_Localised` key/value, as above, but also the
`Category` key/value pair from each Item.

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### StarPos
You MUST add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event.