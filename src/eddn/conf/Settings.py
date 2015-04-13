'''
Created on 15 Nov 2014

@author: james
'''

import simplejson
import argparse
from eddn import __version__ as version


class _Settings(object):

    EDDN_VERSION = version

    ###############################################################################
    # Relay settings
    ###############################################################################

    RELAY_RECEIVER_BINDINGS = ["tcp://localhost:8500"]

    RELAY_SENDER_BINDINGS = ["tcp://*:9500"]

    RELAY_DECOMPRESS_MESSAGES = False

    ###############################################################################
    #  Gateway settings
    ###############################################################################

    GATEWAY_SENDER_BINDINGS = ["tcp://*:8500"]

    GATEWAY_IP_KEY_SALT = None

    GATEWAY_JSON_SCHEMAS = {
        "http://schemas.elite-markets.net/eddn/commodity/1": "../schemas/commodity-v0.1.json",
        "http://schemas.elite-markets.net/eddn/commodity/1/test": "../schemas/commodity-v0.1.json"
    }

    def loadFrom(self, fileName):
        f = open(fileName, 'r')
        conf = simplejson.load(f)
        for key, value in conf.iteritems():
            if key in self.__dict__:
                self.__dict__[key] = value
            else:
                print "Ignoring unknown setting {0}".format(key)

Settings = _Settings()

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", nargs="?", default=None)
args = parser.parse_args()

if args.config:
    Settings.loadFrom(args.config)
