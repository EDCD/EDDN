import unittest

from eddn.core.StatsCollector import StatsCollector
from time import sleep


class Test(unittest.TestCase):

    def testStatsCollectorTally(self):
        print "This test will take about 60 seconds to run!"
        statsCollector = StatsCollector()
        statsCollector.start()

        self.assertEqual(0, statsCollector.getCount("test", 1))
        statsCollector.tally("test")
        sleep(60)
        self.assertEqual(1, statsCollector.getCount("test", 1))
