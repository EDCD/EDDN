# coding: utf8

import argparse
import simplejson
from eddn.conf.Version import __version__ as version


class _Settings(object):

    EDDN_VERSION = version

    ###############################################################################
    # Local installation settings
    ###############################################################################

    CERT_FILE                               = '/etc/letsencrypt/live/eddn.edcd.io/fullchain.pem'
    KEY_FILE                                = '/etc/letsencrypt/live/eddn.edcd.io/privkey.pem'

    ###############################################################################
    # Relay settings
    ###############################################################################

    RELAY_HTTP_BIND_ADDRESS                 = "0.0.0.0"
    RELAY_HTTP_PORT                         = 9090

    RELAY_RECEIVER_BINDINGS                 = ["tcp://127.0.0.1:8500"]

    RELAY_SENDER_BINDINGS                   = ["tcp://*:9500"]

    # If set to False, no deduplicate is made
    RELAY_DUPLICATE_MAX_MINUTES             = 15

    # If set to false, don't listen to topic and accept all incoming messages
    RELAY_RECEIVE_ONLY_GATEWAY_EXTRA_JSON   = True

    RELAY_EXTRA_JSON_SCHEMAS                = {}

    ###############################################################################
    #  Gateway settings
    ###############################################################################

    GATEWAY_HTTP_BIND_ADDRESS               = "127.0.0.1"
    GATEWAY_HTTP_PORT                       = 8081

    GATEWAY_SENDER_BINDINGS                 = ["tcp://127.0.0.1:8500"]

    GATEWAY_JSON_SCHEMAS                    = {
        "https://eddn.edcd.io/schemas/commodity/3"                  : "schemas/commodity-v3.0.json",
        "https://eddn.edcd.io/schemas/commodity/3/test"             : "schemas/commodity-v3.0.json",

        "https://eddn.edcd.io/schemas/shipyard/2"                   : "schemas/shipyard-v2.0.json",
        "https://eddn.edcd.io/schemas/shipyard/2/test"              : "schemas/shipyard-v2.0.json",

        "https://eddn.edcd.io/schemas/outfitting/2"                 : "schemas/outfitting-v2.1.json",
        "https://eddn.edcd.io/schemas/outfitting/2/test"            : "schemas/outfitting-v2.1.json",

        "https://eddn.edcd.io/schemas/blackmarket/1"                : "schemas/blackmarket-v1.0.json",
        "https://eddn.edcd.io/schemas/blackmarket/1/test"           : "schemas/blackmarket-v1.0.json",

        "https://eddn.edcd.io/schemas/journal/1"                    : "schemas/journal-v1.0.json",
        "https://eddn.edcd.io/schemas/journal/1/test"               : "schemas/journal-v1.0.json",
    }

    GATEWAY_OUTDATED_SCHEMAS                = [
        "http://schemas.elite-markets.net/eddn/commodity/1",
        "http://schemas.elite-markets.net/eddn/commodity/1/test",
        "http://schemas.elite-markets.net/eddn/commodity/2",
        "http://schemas.elite-markets.net/eddn/commodity/2/test",
        "http://schemas.elite-markets.net/eddn/commodity/3",
        "http://schemas.elite-markets.net/eddn/commodity/3/test",
        "http://schemas.elite-markets.net/eddn/outfitting/1",
        "http://schemas.elite-markets.net/eddn/outfitting/1/test",
        "http://schemas.elite-markets.net/eddn/outfitting/2",
        "http://schemas.elite-markets.net/eddn/outfitting/2/test",
        "http://schemas.elite-markets.net/eddn/shipyard/1",
        "http://schemas.elite-markets.net/eddn/shipyard/1/test",
        "http://schemas.elite-markets.net/eddn/shipyard/2",
        "http://schemas.elite-markets.net/eddn/shipyard/2/test",
        "http://schemas.elite-markets.net/eddn/blackmarket/1",
        "http://schemas.elite-markets.net/eddn/blackmarket/1/test",
        "http://schemas.elite-markets.net/eddn/journal/1",
        "http://schemas.elite-markets.net/eddn/journal/1/test",
    ]

    ###############################################################################
    #  Monitor settings
    ###############################################################################

    MONITOR_RECEIVER_BINDINGS               = ["tcp://127.0.0.1:8500"]

    MONITOR_DB                              = "/home/EDDN_Monitor.s3db"
    #MONITOR_DB                              = "D:/EDDN_Monitor.s3db" #DEBUG

    MONITOR_UA                              = "UA-496332-23"




    def loadFrom(self, fileName):
        f = open(fileName, 'r')
        conf = simplejson.load(f)
        for key, value in conf.iteritems():
            if key in dir(self):
                self.__setattr__(key, value)
            else:
                print "Ignoring unknown setting {0}".format(key)

Settings = _Settings()


def loadConfig():
    '''
    Loads in a settings file specified on the commandline if one has been specified.
    A convenience method if you don't need other things specified as commandline
    options. Otherwise, point the filename to Settings.loadFrom().
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", nargs="?", default=None)
    args = parser.parse_args()

    if args.config:
        Settings.loadFrom(args.config)
