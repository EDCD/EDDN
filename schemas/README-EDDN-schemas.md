# EDDN Schemas Documentation

## Introduction
EDDN is a zermoq service to allow players of the game 
[Elite Dangerous](https://www.elitedangerous.com/), 
published by [Frontier Developments](https://www.frontier.co.uk/), to 
upload game data so that interested listeners can receive a copy.

EDDN accepts HTTP POST uploads in a defined format representing this game 
data and then passes it on to any interested listeners.

## Sources
There are two sources of game data, both provided, and approved for use, by
Frontier Developments, the publisher of the game.

## Journal Files
On the PC version of the game "Journal files" are written during any game 
session.  These are in newline-delimited JSON format, with each line 
representing a single JSON object.  Frontier Developments publishes 
documentation for the various events in their
[Player Tools & API Discussions](https://forums.frontier.co.uk/forums/elite-api-and-tools/)
forum.

In general the documentation is made available in a file named something like:

    Journal_Manual-v<version>

as both a MicroSoft word `.doc` file, or a `.pdf` file.

Consult the latest of these for documentation on individual events.  
However, be aware that sometimes the documentation is in error, possibly 
due to not having been updated after a game client change.

## Companion API (CAPI) data
Historically Frontier Developments provided an API for use by its 
short-lived iOS "Companion" app.  Initially this was only meant to be used 
by that app, with no public documentation, or even admission of its existence.

Initially it required being supplied with the email and password as used to 
login to the game (but at least over HTTPS).  Eventually they
[allowed general use of this](https://forums.frontier.co.uk/threads/open-letter-to-frontier-developments.218658/page-19#post-3371472).

In late 2018 Frontier switched the authentication to using an oAuth2 flow, 
meaning players no longer need to supply their email and password to 
third-party sites and clients.

As of October 2021 there has still never been any official documentation 
about the available endpoints and how they work.  There is some
[third-party documentation](https://github.com/Athanasius/fd-api/blob/main/docs/README.md)
by Athanasius.
