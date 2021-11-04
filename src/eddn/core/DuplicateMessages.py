# coding: utf8
"""Detect duplicate messages from senders."""

import hashlib
import re
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep

import simplejson

from eddn.conf.Settings import Settings


class DuplicateMessages(Thread):
    """Class holding all code for duplicate message detection."""

    max_minutes = Settings.RELAY_DUPLICATE_MAX_MINUTES

    caches = {}

    lock = Lock()

    def __init__(self):
        super(DuplicateMessages, self).__init__()
        self.daemon = True

    def run(self):
        """Expire duplicate messages."""
        while True:
            sleep(60)
            with self.lock:
                max_time = datetime.utcnow()

                for key in self.caches.keys():
                    if self.caches[key] + timedelta(minutes=self.max_minutes) < max_time:
                        del self.caches[key]

    def isDuplicated(self, json):
        with self.lock:
            # Test messages are never duplicate, would be a pain to wait for another test :D
            if re.search('test', json['$schemaRef'], re.I):
                return False

            # Shallow copy, minus headers
            jsonTest = {
                '$schemaRef': json['$schemaRef'],
                'message': dict(json['message']),
            }

            # Remove timestamp (Mainly to avoid multiple scan messages and faction influences)
            jsonTest['message'].pop('timestamp')

            # Convert journal starPos to avoid software modification in dupe messages
            if 'StarPos' in jsonTest['message']:
                jsonTest['message']['StarPos'] = [int(round(x * 32)) for x in jsonTest['message']['StarPos']]

            # Prevent journal Docked event with small difference in distance from start
            if 'DistFromStarLS' in jsonTest['message']:
                jsonTest['message']['DistFromStarLS'] = int(jsonTest['message']['DistFromStarLS'] + 0.5)

            # Remove journal ScanType and DistanceFromArrivalLS (Avoid duplicate scan messages after SAAScanComplete)
            jsonTest['message'].pop('ScanType', None)
            jsonTest['message'].pop('DistanceFromArrivalLS', None)

            message = simplejson.dumps(jsonTest, sort_keys=True) # Ensure most duplicate messages will get the same key
            key     = hashlib.sha256(message).hexdigest()

            if key not in self.caches:
                self.caches[key] = datetime.utcnow()
                return False
            else:
                self.caches[key] = datetime.utcnow()
                return True
