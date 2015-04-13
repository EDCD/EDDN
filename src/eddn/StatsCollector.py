from collections import deque
from itertools import islice
from threading import Lock, Thread
from time import sleep


class StatsCollector(Thread):
    '''
    Collects simple statistics - number of inbound vs. outbound messages - and
    aggregates them over the number of minutes you choose, up to one hour.
    '''

    max_minutes = 60

    inboundMessages = 0
    outboundMessages = 0

    current = {}

    history = {}

    inboundHistory = deque(maxlen=max_minutes)
    outboundHistory = deque(maxlen=max_minutes)

    lock = Lock()

    def __init__(self):
        super(StatsCollector, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            sleep(60)
            with self.lock:
                self.inboundHistory.appendleft(self.inboundMessages)
                self.outboundHistory.appendleft(self.outboundMessages)
                self.inboundMessages = 0
                self.outboundMessages = 0
                for key in self.current.keys():
                    if key not in self.history:
                        self.history[key] = deque(maxlen=self.max_minutes)
                    self.history[key].appendleft(self.current[key])
                    self.current[key] = 0

    def tallyInbound(self):
        with self.lock:
            self.inboundMessages += 1

    def tallyOutbound(self):
        with self.lock:
            self.outboundMessages += 1

    def tally(self, key):
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
        summary = {
            "inbound": {
                "1min": self.getInboundCount(1),
                "5min": self.getInboundCount(5),
                "60min": self.getInboundCount(60),
            },
            "outbound": {
                "1min": self.getOutboundCount(1),
                "5min": self.getOutboundCount(5),
                "60min": self.getOutboundCount(60)
            }
        }

        for key in self.current.keys():
            summary[key] = {
                "1min": self.getCount(key, 1),
                "5min": self.getCount(key, 5),
                "60min": self.getCount(key, 60)
            }

        return summary
