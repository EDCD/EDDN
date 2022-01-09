#!/usr/bin/env python3

import json
import requests
import sys

if len(sys.argv) != 2:
  print('test-sender.py <filename>')
  sys.exit(-1)

with open(sys.argv[1], 'r') as f:
  msg = f.read()

  s = requests.Session()

  r = s.post('https://beta.eddn.edcd.io:4431/upload/', data=msg)

  print(f'Response: {r!r}')
  print(f'Body: {r.content.decode()}')

