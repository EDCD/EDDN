# EDDN FSSSignalDiscovered Schema

## Introduction
Here we document how to take data from an ED `FSSSignalDiscovered` Journal 
Event and properly structure it for sending to EDDN.

Please consult [EDDN Schemas README](./README-EDDN-schemas.md) for general
documentation for a schema such as this.

## Senders
The primary data source for this schema is the ED Journal event 
`FSSSignalDiscovered`.

### Batching
You MUST put several `FSSSignalDiscovered` events to an array `signals` which is key of `message`. Minimum size of 
`signals` is 1 item.

Do not make a request for every single event.

Possible algorithm of batching:
1. If the event is FSSSignalDiscovered, store it to the temporal list and proceed to next event.
2. If the next event is also FSSSignalDiscovered, repeat 1.
3. If the next event is any other or there is no other event for more than 10 seconds, send the 
   temporal list in a single message to EDDN.

### Elisions
You MUST remove the following key/value pairs from the data:

  - `TimeRemaining` key/value pair.

You MUST refuse to send the whole `FSSSignalDiscovered` event if `USSType` key has `$USS_Type_MissionTarget;` value.

### Augmentations
#### horizons flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### odyssey flag
You SHOULD add this key/value pair, using the value from the `LoadGame` event.

#### systemName
You SHOULD add a `systemName` string containing the system name from the last `FSDJump`, `CarrierJump`, or `Location` 
event There exists problem when you gets `FSSSignalDiscovered` before
`FSDJump`, `CarrierJump`, or `Location` event, so you MUST cross-check it with `SystemAddress` or don't include at all. 

#### StarPos
You SHOULD add a `StarPos` array containing the system co-ordinates from the 
last `FSDJump`, `CarrierJump`, or `Location` event. There exists problem when you gets `FSSSignalDiscovered` before
`FSDJump`, `CarrierJump`, or `Location` event, so you MUST cross-check it with `SystemAddress` or don't include at all. 

## Receivers
Receivers should remember: `horizons`, `odyssey`, `systemName`, `StarPos` are optional key/value pairs, it means you
should not rely on it will appear in every EDDN event.

## Examples
This is a few example of messages that passes current `FSSSignalDiscovered` schema.
1. A message without `horizons`, `odyssey`, `systemName`, `StarPos` fields.
```json
{
   "$schemaRef":"https://eddn.edcd.io/schemas/fsssignaldiscovered/1",
   "header":{
      "gatewayTimestamp":"2021-11-06T22:48:43.483147Z",
      "softwareName":"an software",
      "softwareVersion":"a version",
      "uploaderID":"an uploader"
   },
   "message":{
      "event":"FSSSignalDiscovered",
      "signals":[
         {
            "timestamp":"2021-07-30T19:03:08Z",
            "event":"FSSSignalDiscovered",
            "SystemAddress":1774711381,
            "SignalName":"EXPLORER-CLASS X2X-74M",
            "IsStation":true
         }
      ]
   }
}
```

2. A message with `horizons`, `odyssey`, `systemName`, `StarPos` fields which says it sent from Odyssey.
```json
{
   "$schemaRef":"https://eddn.edcd.io/schemas/fsssignaldiscovered/1",
   "header":{
      "gatewayTimestamp":"2021-11-06T22:48:43.483147Z",
      "softwareName":"an software",
      "softwareVersion":"a version",
      "uploaderID":"an uploader"
   },
   "message":{
      "event":"FSSSignalDiscovered",
      "signals":[
         {
            "timestamp":"2021-07-30T19:03:08Z",
            "event":"FSSSignalDiscovered",
            "SystemAddress":1774711381,
            "SignalName":"EXPLORER-CLASS X2X-74M",
            "IsStation":true
         },
         { 
            "timestamp":"2020-12-31T14:14:01Z", 
            "event":"FSSSignalDiscovered", 
            "SystemAddress":216054883492, 
            "SignalName":"$USS_NonHumanSignalSource;", 
            "USSType":"$USS_Type_NonHuman;",
            "SpawningState":"$FactionState_None;", 
            "SpawningFaction":"$faction_none;",
            "ThreatLevel":5
            }
      ],
        "StarPos": [
          8.1875,
          124.21875,
          -38.5
        ],
        "StarSystem": "HIP 56186",
        "horizons": true,
        "odyssey": true
   }
}
```
