#!/usr/bin/env python3

import json
import sys
import urllib3

if len(sys.argv) != 2:
  print('test-sender.py <filename>')
  sys.exit(-1)

with open(sys.argv[1], 'r') as f:
  # Read from provided file
  msg = f.read()

  # Fake form-encode it
  msg = 'data=' + msg

  http = urllib3.PoolManager()

  # Send that data as a POST body
  r = http.request(
    'POST',
    'https://beta.eddn.edcd.io:4431/upload/',
    body=msg
  )

  print(f'Response: {r.status!r}')
  print(f'Body:\n{r.data.decode()}\n')

