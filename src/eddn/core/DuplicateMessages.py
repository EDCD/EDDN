# coding: utf8
"""Detect duplicate messages from senders."""

import hashlib
import re
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep
from typing import Dict

import simplejson

from eddn.conf.Settings import Settings


class DuplicateMessages(Thread):
    """Class holding all code for duplicate message detection."""

    max_minutes = Settings.RELAY_DUPLICATE_MAX_MINUTES

    caches: Dict = {}

    lock = Lock()

    def __init__(self) -> None:
        super(DuplicateMessages, self).__init__()
        self.daemon = True

    def run(self) -> None:
        """Expire duplicate messages."""
        while True:
            sleep(60)
            with self.lock:
                max_time = datetime.utcnow()

                for key in self.caches.keys():
                    if self.caches[key] + timedelta(minutes=self.max_minutes) < max_time:
                        del self.caches[key]

    def is_duplicated(self, json: Dict) -> bool:
        """Detect if the given message is in the duplicates cache."""
        with self.lock:
            # Test messages are never duplicate, would be a pain to wait for another test :D
            if re.search('test', json['$schemaRef'], re.I):
                return False

            # Shallow copy, minus headers
            json_test = {
                '$schemaRef': json['$schemaRef'],
                'message': dict(json['message']),
            }

            # Remove timestamp (Mainly to avoid multiple scan messages and faction influences)
            json_test['message'].pop('timestamp')

            # Convert journal starPos to avoid software modification in dupe messages
            if 'StarPos' in json_test['message']:
                json_test['message']['StarPos'] = [int(round(x * 32)) for x in json_test['message']['StarPos']]

            # Prevent journal Docked event with small difference in distance from start
            if 'DistFromStarLS' in json_test['message']:
                json_test['message']['DistFromStarLS'] = int(json_test['message']['DistFromStarLS'] + 0.5)

            # Remove journal ScanType and DistanceFromArrivalLS (Avoid duplicate scan messages after SAAScanComplete)
            json_test['message'].pop('ScanType', None)
            json_test['message'].pop('DistanceFromArrivalLS', None)

            message = simplejson.dumps(json_test, sort_keys=True)  # Ensure most duplicate messages will get the same
            # key
            key = hashlib.sha256(message.encode('utf8')).hexdigest()

            if key not in self.caches:
                self.caches[key] = datetime.utcnow()
                return False
            else:
                self.caches[key] = datetime.utcnow()
                return True
