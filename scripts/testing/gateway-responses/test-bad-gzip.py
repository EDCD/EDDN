#!/usr/bin/env python3
#
# 2022-01-10:   THIS SCRIPT DOES NOT PERFORM THE INTENDED PURPOSE
# BECAUSE IT SEEMS THAT `requests` (or underlying modules) IS TOO CLEVER
# AND APPLIES COMPRESSION WHEN WE SET THE `Content-Encoding: gzip`
# HEADER

import json
import requests
import sys

print('''
DO NOT USE THIS SCRIPT, IT DOES NOT PERFORM THE INTENDED PURPOSE.

USE THE `test-bad-gzip.sh` SCRIPT INSTEAD.

''')
sys.exit(-1)

if len(sys.argv) != 2:
  print('test-sender.py <filename>')
  sys.exit(-1)

with open(sys.argv[1], 'r') as f:
  msg = f.read()

  s = requests.Session()

  # This apparently causes compression to actually happen
  s.headers['Content-Encoding'] = 'gzip'
  r = s.post(
    'https://beta.eddn.edcd.io:4431/upload/',
    data=msg,
  )

  print(f'Response: {r!r}')
  print(f'Body: {r.content.decode()}')

