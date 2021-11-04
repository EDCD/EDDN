# coding: utf8
"""Handle various stats about uploads."""

from collections import deque
from datetime import datetime
from itertools import islice
from threading import Lock, Thread
from time import sleep
from typing import Any, Dict


class StatsCollector(Thread):
    """Collect simple statistics and aggregate them."""

    def __init__(self):
        super(StatsCollector, self).__init__()
        self.daemon = True
        self.max_minutes = 60

        self.current = {}
        self.history = {}

        self.lock = Lock()

        self.start_time = 0

    def run(self) -> None:
        """Update statistics once a minute."""
        self.start_time = datetime.utcnow()
        while True:
            sleep(60)
            with self.lock:
                for key in self.current.keys():
                    if key not in self.history:
                        self.history[key] = deque(maxlen=self.max_minutes)

                    self.history[key].appendleft(self.current[key])
                    self.current[key] = 0

    def tally(self, key: str) -> None:
        """
        Add one to the count of the given key.

        :param key: Key for affected data.
        """
        with self.lock:
            if key not in self.current:
                self.current[key] = 1
            else:
                self.current[key] += 1

    def get_count(self, key: str, minutes: int) -> int:
        """
        Get current count for given key over requested time period.

        :param key: Key for requested data.
        :param minutes: How many minutes back in time we want the count for.
        :returns: Count for the requested data.
        """
        if key in self.history:
            return sum(islice(self.history[key], 0, min(minutes, self.max_minutes)))
        return 0

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all current data.

        :returns: A Dict of the summary data.
        """
        summary: Dict[str, Any] = {}

        for key in self.current.keys():
            summary[key] = {
                "1min": self.get_count(key, 1),
                "5min": self.get_count(key, 5),
                "60min": self.get_count(key, 60)
            }

        summary['uptime'] = int((datetime.utcnow() - self.start_time).total_seconds())

        return summary
