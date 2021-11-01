# EDDN Schemas Documentation

## Introduction

EDDN is a
[zermoq](https://zeromq.org/) service to allow players of the game
[Elite Dangerous](https://www.elitedangerous.com/), published
by [Frontier Developments](https://www.frontier.co.uk/), to upload game data so
that interested listeners can receive a copy.

EDDN accepts HTTP POST uploads in a defined format representing this game data
and then passes it on to any interested listeners.

---
## Sources

There are two sources of game data, both provided by the publisher of the game,
Frontier Developerments.  They are both explicitly approved for use by 
third-party software.

### Journal Files

On the PC version of the game, "Journal files" are written during any game
session. These are in newline-delimited JSON format, with each line
representing a single JSON object. Frontier Developments publishes
documentation for the various events in their
[Player Tools & API Discussions](https://forums.frontier.co.uk/forums/elite-api-and-tools/)
forum.

In general the documentation is made available in a file named something like:

    Journal_Manual-v<version>

as both a MicroSoft word `.doc` file, or a `.pdf` file.  Historically the 
use of `_` versus `-` in those filenames has varied.

Consult the latest of these for documentation on individual events.  
However, be aware that sometimes the documentation is in error, possibly due to
not having been updated after a game client change.

### Companion API (CAPI) data

Frontier Developments provides an API to retrieve certain game data, even 
without the game running.  Historically this was for use by its short-lived
iOS "Companion" app, and was only intended to be used by that app. There was no
public documentation, or even admission of its existence.

Eventually, after some enterprising players had snooped the connections and
figured out the login method and endpoints, Frontier Developments
[allowed general use of this](https://forums.frontier.co.uk/threads/open-letter-to-frontier-developments.218658/page-19#post-3371472)
.

Originally the API authentication required being supplied with the email and
password as used to login to the game (but at least this was over HTTPS).

In late 2018 Frontier switched the authentication to using an oAuth2 flow,
meaning players no longer need to supply their email and password to
third-party sites and clients.

As of October 2021 there has still never been any official documentation about
the available endpoints and how they work. There is some
[third-party documentation](https://github.com/Athanasius/fd-api/blob/main/docs/README.md)
by Athanasius.

When using the Companion API please be aware that the server that supplies this
data sometimes lags behind the game - usually by a few seconds, sometimes by
minutes. You MUST check in the data from the CAPI that the Cmdr is
docked (`["commander"]["docked"]` is `True`) and that the station and
system (`["lastStarport"]["name"]` and `["lastSystem"]["name"]`) match those
reported from the Journal before using the data for the commodity, outfitting
and shipyard schemas.

---

## Uploading messages

### Send only live data to the live schemas
You MUST **NOT** send information from any non-live (e.g. alpha or beta)
version of the game to the main schemas on this URL.

You MAY send such to this URL so long as you append `/test` to the `$schemaRef`
value, e.g.

    "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2/test",

You MUST also utilise these test forms of the schemas when first testing your
code. There might also be a beta.eddn.edcd.io, or dev.eddn.edcd.io, service
available from time to time as necessary, e.g. for testing new schemas or
changes to existing ones.

### Sending data
To upload market data to EDDN, you'll need to make a POST request to the URL:

* https://eddn.edcd.io:4430/upload/

The body of this is a JSON object, so you SHOULD set a `Content-Type` header of
`applicaton/json`, and NOT any of:

* `application/x-www-form-urlencoded`
* `multipart/form-data`
* `text/plain`

### Format of uploaded messages
Each message is a JSON object in utf-8 encoding containing the following
key+value pairs:

1. `$schemaRef` - Which schema (including version) this message is for.
2. `header` - Object containing mandatory information about the upload;
    1. `uploaderID` - a unique ID for the player uploading this data.  
       Don't worry about privacy, the EDDN service will hash this with a key
       that is regularly changed so no-one knows who an uploader is in-game.
    2. `softwareName` - an identifier for the software performing the upload.
    3. `softwareVersion` - The version of that software being used.

   Listeners MAY make decisions about whether to utilise the data in any
   message based on the combination of `softwareName` and `softwareVersion`.
   
   **DO not** add `gatewaytimestamp` yourself. The EDDN Gateway will add
   this and will overwrite any that you provide, so don't bother.
4. `message` - Object containing the data for this message. Consult the
   relevant README file within this documentation, e.g.
   [codexentry-README.md](./codexentry-README.md). There are some general
   guidelines [below](#contents-of-message).

For example, a shipyard message, version 2, might look like:

```JSON
{
  "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2",
  "header": {
    "uploaderID": "Bill",
    "softwareName": "My excellent app",
    "softwareVersion": "0.0.1"
  },
  "message": {
    "systemName": "Munfayl",
    "stationName": "Samson",
    "marketId": 128023552,
    "horizons": true,
    "timestamp": "2019-01-08T06:39:43Z",
    "ships": [
      "anaconda",
      "dolphin",
      "eagle",
      "ferdelance",
      "hauler",
      "krait_light",
      "krait_mkii",
      "mamba",
      "python",
      "sidewinder"
    ]
  }
}
```

### Contents of `message`

Each `message` object must have, at bare minimum:

1. `timestamp` - string date and time in ISO8601 format. Whilst that
   technically allows for any timezone to be cited you SHOULD provide this in
   UTC, aka 'Zulu Time' as in the example above. You MUST ensure that you are
   doing this properly. Do not claim 'Z' whilst actually using a local time
   that is offset from UTC.
   
   Listeners MAY make decisions on accepting data based on this time stamp,
   i.e. "too old".
2. One other key/value pair representing the data. In general there will be
   much more than this. Again, consult the
   [schemas and their documentation](./).

Note that many of the key names chosen in the schemas are based on the CAPI 
data, not Journal events, because the CAPI came first.  This means renaming 
many of the keys from Journal events to match the schema.

EDDN is intended to transport generic data not specific to any particular Cmdr
and to reflect the data that a player would see in-game in station services or
the local map. To that end, uploading applications MUST ensure that messages do
not contain any Cmdr-specific data (other than "uploaderID" and the "horizons"
flag). In practice as of E:D 3.3 this means:

* outfitting: Skip items whose availability depends on the Cmdr's status rather
  than on the station. Namely:
    - Items that aren't weapons/utilities (`Hpt_*`), standard/internal
      modules (`Int_*`) or armour (`*_Armour_*`) (i.e. bobbleheads, decals,
      paintjobs and shipkits).
    - Items that have a non-null `"sku"` property, unless
      it's `"ELITE_HORIZONS_V_PLANETARY_LANDINGS"` (i.e. PowerPlay and tech
      broker items).
    - The `"Int_PlanetApproachSuite"` module (for historical reasons).
* shipyard: *Include* ships listed in the `"unavailable_list"` property (i.e.
  available at this station, but not to this Cmdr).
* journal: Strip out `"..._Localised"` properties throughout the data
  structure.
* journal/Docked: Strip out `"Wanted"`, `"ActiveFine"`, `"CockpitBreach"`
  properties
* journal/FSDJump: Strip out `"Wanted"`, `"BoostUsed"`, `"FuelLevel"`
  , `"FuelUsed"` and `"JumpDist"` properties.
* journal/Location: Strip out `"Wanted"`, `"Latitude"` and `"Longitude"`
  properties.
* journal/Location and journal/FSDJump: strip out `"HappiestSystem"`
  , `"HomeSystem"`, `"MyReputation"` and `"SquadronFaction"` properties within
  the list of `"Factions"`.

Some of these requirements are also enforced by the schemas, and some things
the schemas enforce might not be explicitly called out here, so **do**
check what you're sending against the schema when implementing sending new
events.
