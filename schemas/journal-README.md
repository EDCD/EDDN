# EDDN Journal Schema

## Introduction
Here we document how to take data from miscellaneous ED Journal
events and properly structure it for sending to EDDN.

This is the historical "all Journal events" schema that will be deprecated 
in the future.  Please check for a schema specific to the journal event 
under consideration to see if data should be sent on that event specific 
schema instead.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal events:

  - `Docked`
  - `FSDJump`
  - `Scan`
  - `Location`
  - `SAASignalsFound`
  - `CarrierJump`
  - `CodexEntry` - But see the separate
    [codexentry schema](./codexentry-README.md) documentation.

### Key Renames
Many of the key names have a different case defined in this schema, make
sure you are renaming them as appropriate.

### Elisions
#### Remove _Localised key/values
All keys whose name ends with `_Localised`, i.e. the `Name_Localised`
key/values in Items.

#### Personal data in `Docked` events
The following keys+values should be removed from `Docked` event data:

  - `Wanted`
  - `ActiveFine`
  - `CockpitBreach`

#### Personal data in `FSDJump` events
The following keys+values should be removed from `FSDJump` event data:

- `Wanted`
- `BoostUsed`
- `FuelLevel`
- `FuelUsed`
- `JumpDist`
- `HappiestSystem` from within the list of `Factions`.
- `HomeSystem` from within the list of `Factions`.
- `MyReputation` from within the list of `Factions`.
- `SquadronFaction` from within the list of `Factions`.

####  Personal data in `Location` events
The following keys+values should be removed from `Location` event data:

- `Wanted`
- `Latitude`
- `Longitude`
- `HappiestSystem` from within the list of `Factions`.
- `HomeSystem` from within the list of `Factions`.
- `MyReputation` from within the list of `Factions`.
- `SquadronFaction` from within the list of `Factions`.

### Augmentations
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

#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### StarSystem
If not already present, you MUST add a `StarSystem` string containing the
name of the system from the last `FSDJump`, `CarrierJump`, or `Location` event.

**You MUST apply a location cross-check, as per
[Other data augmentations](../docs/Developers.md#other-data-augmentations).**

This should only apply to `SAASignalsFound` events.

#### StarPos
If not already present, you  MUST add a `StarPos` array containing the
system co-ordinates from the last `FSDJump`, `CarrierJump`, or `Location`
event.

**You MUST apply a location cross-check, as per
[Other data augmentations](../docs/Developers.md#other-data-augmentations).**

This should only apply to `Docked`, `Scan` and `SAASignalsFound` events.
