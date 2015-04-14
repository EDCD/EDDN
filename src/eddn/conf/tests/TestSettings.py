import os
import unittest


class TestSettings(unittest.TestCase):

    def testLoadSettings(self):
        from eddn.conf.Settings import Settings
        self.assertEqual(Settings.RELAY_DECOMPRESS_MESSAGES, False)
        Settings.loadFrom(os.path.join(os.path.dirname(__file__), "testLoadSettings.json"))
        self.assertEqual(Settings.RELAY_DECOMPRESS_MESSAGES, True)
