# EDDN NavRoute Schema

## Introduction
Here we document how to take data from an ED `NavRoute` Journal
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the `NavRoute.json` file.  That 
it has been freshly written is signalled by the ED Journal event `NavRoute`.

So, monitor the Journal as normal, and when you see a `NavRoute` event open 
the `NavRoute.json` file for reading, read it, and close it again.  Use the 
data you got from reading this file, not merely the Journal event.

The primary data to be sent is the `Route` array from the contents of the 
separate file.

### Elisions
There are no elisions in this schema.

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.