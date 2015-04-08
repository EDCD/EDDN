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
                self.inboundHistory.append(self.inboundMessages)
                self.outboundHistory.append(self.outboundMessages)
                self.inboundMessages = 0
                self.outboundMessages = 0

    def tallyInbound(self):
        with self.lock:
            self.inboundMessages += 1

    def tallyOutbound(self):
        with self.lock:
            self.outboundMessages += 1

    def getInboundCount(self, minutes):
        return sum(islice(self.inboundHistory, 0, max(minutes, self.max_minutes)))

    def getOutboundCount(self, minutes):
        return sum(islice(self.outboundHistory, 0, max(minutes, self.max_minutes)))
