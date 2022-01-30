## Introduction

EDDN is a
[zermoq](https://zeromq.org/) service which allows players of the game
[Elite Dangerous](https://www.elitedangerous.com/), published
by [Frontier Developments](https://www.frontier.co.uk/), to upload game data so
that interested listeners can receive a copy.

EDDN accepts HTTP POST uploads in
[a defined format](#sending-data)
representing this game data and then passes it on to any interested listeners.

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

It is *not* recommended to use CAPI data as the source as it's fraught with
additional issues.  EDMarketConnector does so in order to facilitate
obtaining data without the player needing to open the commodities screen.

#### Detecting CAPI data lag

When using the Companion API please be aware that the server that supplies this
data sometimes lags behind the game - usually by a few seconds, sometimes by
minutes. You MUST check in the data from the CAPI that the Cmdr is
docked, and that the station and system names match those
reported from the Journal before using the data for the commodity, outfitting
and shipyard Schemas:

1. Retrieve the commander data from the `/profile` CAPI endpoint.
2. Check that `commander['docked']` is true.  If not, abort.
3. Retrieve the data from the `/market` and `/shipyard` CAPI endpoints.
4. Compare the system and station name from the CAPI market data,
   `["lastStarport"]["name"]` and `["lastSystem"]["name"]`,
   to that from the last `Docked` or `Location` journal event.  If either does
   not match then you MUST **abort**.  This likely indicates that the CAPI
   data is lagging behind the game client state and thus should not be used.

---

## Uploading messages

### Send only live data to the live Schemas
You MUST **NOT** send information from any non-live (e.g. alpha or beta)
version of the game to the main Schemas on this URL.

You MAY send such to this URL so long as you append `/test` to the `$schemaRef`
value, e.g.

    "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2/test",

You MUST also utilise these test forms of the Schemas whenever you are
testing your EDDN-handling code, be that new code or changes to existing code.

As well as the Live service there are also `beta` and `dev`
[endpoints](../README.md#eddn-endpoints) which might be available from time
to time as necessary, e.g. for testing new Schemas or changes to existing
ones.  Ask on the `#eddn` channel of the
[EDCD Discord](https://edcd.github.io/) (check at the bottom for the invite
link).

Alternatively you could attempt
[running your own test instance of EDDN](../docs/Running-this-software.md).

