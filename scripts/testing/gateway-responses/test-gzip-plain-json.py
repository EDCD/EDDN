#!/usr/bin/env python3

import json
import requests
import sys
import urllib3
import zlib

if len(sys.argv) != 2:
  print('test-sender.py <filename>')
  sys.exit(-1)

with open(sys.argv[1], 'r') as f:
  # Read from provided file
  msg = f.read()

  # Compress it
  msg_gzip = zlib.compress(msg.encode('utf-8'))

  http = urllib3.PoolManager()

  # Send that compressed data as a POST body
  r = http.request(
    'POST',
    'https://dev.eddn.edcd.io:4432/upload/',
    headers={
      'Content-Encoding': 'gzip'
    },
    body=msg_gzip
  )

  print(f'Response: {r.status!r}')
  print(f'Body:\n{r.data.decode()}\n')

