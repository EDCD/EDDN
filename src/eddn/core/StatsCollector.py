# coding: utf8

from collections import deque
from datetime import datetime
from itertools import islice
from threading import Lock, Thread
from time import sleep


class StatsCollector(Thread):
    '''
    Collects simple statistics and aggregates them over the number of minutes
    you choose, up to one hour.
    '''

    def __init__(self):
        super(StatsCollector, self).__init__()
        self.daemon = True
        self.max_minutes = 60

        self.current = {}
        self.history = {}

        self.lock = Lock()

        self.starttime = 0

    def run(self):
        self.starttime = datetime.utcnow()
        while True:
            sleep(60)
            with self.lock:
                for key in self.current.keys():
                    if key not in self.history:
                        self.history[key] = deque(maxlen=self.max_minutes)
                    self.history[key].appendleft(self.current[key])
                    self.current[key] = 0

    def tally(self, key):
        with self.lock:
            if key not in self.current:
                self.current[key] = 1
            else:
                self.current[key] += 1

    def getInboundCount(self, minutes):
        return sum(islice(self.inboundHistory, 0, min(minutes, self.max_minutes)))

    def getOutboundCount(self, minutes):
        return sum(islice(self.outboundHistory, 0, min(minutes, self.max_minutes)))

    def getCount(self, key, minutes):
        if key in self.history:
            return sum(islice(self.history[key], 0, min(minutes, self.max_minutes)))
        return 0

    def getSummary(self):
        summary = {}

        for key in self.current.keys():
            summary[key] = {
                "1min": self.getCount(key, 1),
                "5min": self.getCount(key, 5),
                "60min": self.getCount(key, 60)
            }

        summary['uptime'] = int((datetime.utcnow() - self.starttime).total_seconds())

        return summary
