# coding: utf8
import hashlib
import re
import simplejson
import copy

from datetime import datetime, timedelta
from eddn.conf.Settings import Settings
from threading import Lock, Thread
from time import sleep


class DuplicateMessages(Thread):
    max_minutes = Settings.RELAY_DUPLICATE_MAX_MINUTES

    caches = {}

    lock = Lock()

    def __init__(self):
        super(DuplicateMessages, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            sleep(60)
            with self.lock:
                maxTime = datetime.utcnow()

                for key in self.caches.keys():
                    if self.caches[key] + timedelta(minutes=self.max_minutes) < maxTime:
                        del self.caches[key]

    def isDuplicated(self, json):
        with self.lock:
            jsonTest = copy.deepcopy(json)
        
            # Test messages are not duplicate
            if re.search('test', jsonTest['$schemaRef'], re.I):
                return False
            
            # Remove headers
            if 'gatewayTimestamp' in jsonTest['header']:
                del jsonTest['header']['gatewayTimestamp']  # Prevent dupe with new timestamp
            if 'timestamp' in jsonTest['message']:
                del jsonTest['message']['timestamp']  # Prevent dupe with new timestamp
            if 'softwareName' in jsonTest['header']:
                del jsonTest['header']['softwareName']  # Prevent dupe with different software
            if 'softwareVersion' in jsonTest['header']:
                del jsonTest['header']['softwareVersion']  # Prevent dupe with different software version
            if 'uploaderID' in jsonTest['header']:
                del jsonTest['header']['uploaderID']  # Prevent dupe with different uploaderID
            
            # Convert starPos to avoid software modification in dupe messages
            if 'StarPos' in jsonTest['message']:
                if jsonTest['message']['StarPos'][0]:
                    jsonTest['message']['StarPos'][0] = round(jsonTest['message']['StarPos'][0] *32)
                if jsonTest['message']['StarPos'][1]:
                    jsonTest['message']['StarPos'][1] = round(jsonTest['message']['StarPos'][1] *32)
                if jsonTest['message']['StarPos'][2]:
                    jsonTest['message']['StarPos'][2] = round(jsonTest['message']['StarPos'][2] *32)
            
            # Prevent Docked event with small difference in distance from start
            if 'DistFromStarLS' in jsonTest['message']:
                jsonTest['message']['DistFromStarLS'] = round(jsonTest['message']['DistFromStarLS'])

            message = simplejson.dumps(jsonTest, sort_keys=True) # Ensure most duplicate messages will get the same key
            key     = hashlib.sha256(message).hexdigest()

            if key not in self.caches:
                self.caches[key] = datetime.utcnow()
                return False
            else:
                self.caches[key] = datetime.utcnow()
                return True
