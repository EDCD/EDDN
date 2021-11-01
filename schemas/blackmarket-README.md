# EDDN BlackMarket Schema

## Introduction

**This schema is deprecated.  The same data has been made available via the
`prohibited` array in the [commodity schema](./commodity-v3.0.json) since 
September 2017.**

What follows below is only for historical curiosity.

---

Here we document how to take data from an ED `BlackMArket` Journal Event and
properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event `MarketSell`.

### Key Renames
#### name
Due to how the EDDN schema is defined the `Type` key/value should
have the key renamed to `name`.

#### prohibited
Due to how the EDDN schema is defined the `IllegalGoods` key/value should
have the key renamed to `prohibited`.

#### marketID
The Journal documentation says this is `MarketID`, but in the schema the 
`m` is lower case.

### Elisions
You MUST remove the following key/value pairs from the data:

  - `Count`
  - `TotalSale`
  - `AvgPricePaid`
  - `StolenGoods`
  - `BlackMarket` - Because we're using this schema, so this is un-necessary. 

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### systemName
The star system name for where this market is.   Use the `StarSystem` value
from the prior `Docked` or `Location` event.

#### stationName
From the `StationName` value on the prior `Docked` or `Location` event.