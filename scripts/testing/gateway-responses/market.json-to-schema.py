#!/usr/bin/env python3

import json
import re
import sys
from collections import OrderedDict

if len(sys.argv) != 2:
  print('<script> Market.json')
  sys.exit(-1)

CANONICALISE_RE = re.compile(r'\$(.+)_name;')

def canonicalise(item) -> str:
	match = CANONICALISE_RE.match(item)
	return match and match.group(1) or item

entry = json.load(open(sys.argv[1], 'r'))

items = entry.get('Items')

commodities = sorted((OrderedDict([
  ('name',          canonicalise(commodity['Name'])),
  ('meanPrice',     commodity['MeanPrice']),
  ('buyPrice',      commodity['BuyPrice']),
  ('stock',         commodity['Stock']),
  ('stockBracket',  commodity['StockBracket']),
  ('sellPrice',     commodity['SellPrice']),
  ('demand',        commodity['Demand']),
  ('demandBracket', commodity['DemandBracket']),
]) for commodity in items), key=lambda c: c['name'])

msg = {
  '$schemaRef': 'https://eddn.edcd.io/schemas/commodity/3',
  'message': OrderedDict([
    ('timestamp',   entry['timestamp']),
    ('systemName',  entry['StarSystem']),
    ('stationName', entry['StationName']),
    ('marketId',    entry['MarketID']),
    ('commodities', commodities),
  ]),

}

msg['header'] = {
	'uploaderID': 'Athanasius Testing',
	'softwareName': 'Athanasius Testing',
  'softwareVersion': 'v0.0.1',
}
print(json.dumps(msg, indent=2))
