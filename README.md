# EDDN - Elite Dangerous Data Network

## About EDDN
Elite Dangerous Data Network is a tool that facilitates players of the game
[Elite Dangerous](https://www.elitedangerous.com/), including its 
expansions, sharing data about the game galaxy with others.
By pooling data in a common format, tools and analyses can be produced that add
an even greater depth and vibrancy to the in-game universe.

EDDN is not run by or affiliated with the developer of the game - [Frontier 
Developments](http://www.frontier.co.uk/).

The live EDDN service itself does not store any data, and thus makes no 
archive or "current state" available to anyone.  What it provides is a
stream of live data to any interested parties.  Some of those then make 
aggregated data available for general use.

---
---

## Using EDDN
### Game players
It might be useful to consult the [EDCD Cmdr's Guide](https://edcd.github.io/cmdrs-guide.html)
for a general overview of how players can contribute and use game data.

---

#### Contributing data
There are a variety of tools available to players in order for them to help 
out by contributing data, and to then utilise that data to enhance their 
gameplay experience.

For the most part any player who wishes to share data
will need to be playing the game on a PC, as that gives direct access to 
"Journal" files written by the game client.  These are the best source of 
game data.
There are, however, some tools that utilise an API provided by the game
developer that can supply some data if you are playing on a console.

So, on PC, look into installing one of the following tools:

- [E:D Market Connector](https://github.com/EDCD/EDMarketConnector/wiki)
- [EDDI](https://github.com/EDCD/EDDI)
- [EDDiscovery](https://github.com/EDDiscovery/EDDiscovery)
- [Elite Log Agent](https://github.com/DarkWanderer/Elite-Log-Agent)

This list is not exhaustive, or intended to particular endorse any of these 
projects over another, listed here or not.

If you are playing on console some options are:

- The 'console updater', available in a user's 'dashboard' on
  [EDSM](https://www.edsm.net).
- [Journal Limpet](https://journal-limpet.com/).

---

#### Utilising data
If you're looking for tools that utilise EDDN data to enhance your experience
then you're probably looking for one of the sites listed below.  NB: These are
listed in name-alphabetical order and no particular ranking or endorsement is
intended.

- [EDDB](https://eddb.io/) - a website which tries to act as a database of all
 the data available in the game. In general EDDB tries to help finding 
 stuff which players are looking for.
- [EDSM](https://www.edsm.net/) - originally focused on being a 'Star Map', 
  but has since expanded its functionality.  Of particular interest to 
  in-game explorers.
- [Inara](https://inara.cz/) - a popular alternative to EDDB, with a lot of 
  its own unique functionality.
- [Spansh](https://www.spansh.co.uk/plotter) - originally this had one tool,
  a 'Neutron Star' route plotter, but has since expanded into offering many 
  other route plotting tools and general data searching.

---

There are many other third-party tools for Elite Dangerous, both for 
contributing data and utilising it, listed on
[Elite: Dangerous Codex](https://edcodex.info/).  Some of them
interact with EDDN - check the [EDDN tag](https://edcodex.info/?m=tools&cat=9).

---

### Developers
If you are a developer of a third-party tool that could be enhanced by 
uploading data to EDDN then please consult
[the live branch documentation](https://github.com/EDCD/EDDN/blob/live/schemas/README-EDDN-schemas.md)
.
**DO NOT** assume that any code or documentation in the `master` (or 
any other) branch on GitHub truly reflects the current live service!

Anyone planning to send data too EDDN **MUST** comply with all the advice in
that document, and the individual schema README files as applicable.  It's
also the best resource for those listening to the EDDN data stream.

#### EDDN endpoints

There are up to three separate services which might be running.

| Service | Upload |           Listeners           | Notes                                                                                                                                                                                 |
| ------: | :-----: |:-----------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Live | `https://eddn.edcd.io:4430/upload/` |   `tcp://eddn.edcd.io:9500/`    | The actual live service, which should always be running. It is automatically restarted every Thursday at 07:06:00 UTC                                                                 |
| Beta | `https://beta.eddn.edcd.io:4431/upload/` | `tcp://beta.eddn.edcd.io:9510/` | The beta service, which should be running the current state of the `beta` branch.  Usually only active when either new schemas or forthcoming code changes are being actively tested. |
| Dev | `https://dev.eddn.edcd.io:4432/upload/` | `tcp://dev.eddn.edcd.io:9520/`  | The dev service, which could be running any public branch of the code *or* a private branch.                                                                                          | 

In general the Beta and Dev services will only be running so as to aid the core
development team in testing changes.  Don't expect them to be generally
available.

You **MUST** use the correct hostname in the Upload URLs as these are
TLS/HTTPS connections terminated on a Reverse Proxy.

You can get away with using alternate hostnames on the Listener URLs, as
they're purely a ZeroMQ endpoint, no TLS.  But don't be surprised if either
the Beta or Dev service is actually running on a different IP, so don't
chance it.

If you need to test some of your own changes then please read
[Running this software](docs/Running-this-software.md) for how to instantiate
your own test service.  It is hoped that in the future the code will allow for
easily running in a "local only" mode, not requiring any reverse proxy or
internet-valid TLS certificates.

---
---

## Misc

### Service Status
Consult [EDDN Status](https://eddn.edcd.io/) for some information about, 
and statistics for, the live service.

### Hosting of the live service

Hosting is currently provided by the
[Elite: Dangerous Community Developers](https://edcd.github.io/).

### Contacting the EDDN team

* [EDCD Discord](https://discord.gg/XBsdCq9) - **Use the `#eddn` channel**.
* [E:D forum thread](https://forums.frontier.co.uk/threads/elite-dangerous-data-network-eddn.585701/#post-9400060)
