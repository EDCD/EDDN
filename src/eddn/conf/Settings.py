# coding: utf8

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

        "https://eddn.edcd.io/schemas/outfitting/2"                 : "schemas/outfitting-v2.0.json",
        "https://eddn.edcd.io/schemas/outfitting/2/test"            : "schemas/outfitting-v2.0.json",

        "https://eddn.edcd.io/schemas/blackmarket/1"                : "schemas/blackmarket-v1.0.json",
        "https://eddn.edcd.io/schemas/blackmarket/1/test"           : "schemas/blackmarket-v1.0.json",

        "https://eddn.edcd.io/schemas/journal/1"                    : "schemas/journal-v1.0.json",
        "https://eddn.edcd.io/schemas/journal/1/test"               : "schemas/journal-v1.0.json",

        "https://eddn.edcd.io/schemas/scanbarycentre/1"             : "schemas/scanbarycentre-v1.0.json",
        "https://eddn.edcd.io/schemas/scanbarycentre/1/test"        : "schemas/scanbarycentre-v1.0.json",

        "https://eddn.edcd.io/schemas/fssdiscoveryscan/1"           : "schemas/fssdiscoveryscan-v1.0.json",
        "https://eddn.edcd.io/schemas/fssdiscoveryscan/1/test"      : "schemas/fssdiscoveryscan-v1.0.json",

        "https://eddn.edcd.io/schemas/codexentry/1"                 : "schemas/codexentry-v1.0.json",
        "https://eddn.edcd.io/schemas/codexentry/1/test"            : "schemas/codexentry-v1.0.json",

        "https://eddn.edcd.io/schemas/navbeaconscan/1"              : "schemas/navbeaconscan-v1.0.json",
        "https://eddn.edcd.io/schemas/navbeaconscan/1/test"         : "schemas/navbeaconscan-v1.0.json",

        "https://eddn.edcd.io/schemas/navroute/1"                   : "schemas/navroute-v1.0.json",
        "https://eddn.edcd.io/schemas/navroute/1/test"              : "schemas/navroute-v1.0.json",

        "https://eddn.edcd.io/schemas/approachsettlement/1"         : "schemas/approachsettlement-v1.0.json",
        "https://eddn.edcd.io/schemas/approachsettlement/1/test"    : "schemas/approachsettlement-v1.0.json",
        "https://eddn.edcd.io/schemas/fssallbodiesfound/1"          : "schemas/fssallbodiesfound-v1.0.json",
        "https://eddn.edcd.io/schemas/fssallbodiesfound/1/test"     : "schemas/fssallbodiesfound-v1.0.json",

        "https://eddn.edcd.io/schemas/fssbodysignals/1"             : "schemas/fssbodysignals-v1.0.json",
        "https://eddn.edcd.io/schemas/fssbodysignals/1/test"        : "schemas/fssbodysignals-v1.0.json",

        "https://eddn.edcd.io/schemas/fsssignaldiscovered/1"            : "schemas/fsssignaldiscovered-v1.0.json",
        "https://eddn.edcd.io/schemas/fsssignaldiscovered/1/test"       : "schemas/fsssignaldiscovered-v1.0.json",

        "https://eddn.edcd.io/schemas/fcmaterials_journal/1"                : "schemas/fcmaterials_journal-v1.0.json",
        "https://eddn.edcd.io/schemas/fcmaterials_journal/1/test"           : "schemas/fcmaterials_journal-v1.0.json",

        "https://eddn.edcd.io/schemas/fcmaterials_capi/1"                : "schemas/fcmaterials_capi-v1.0.json",
        "https://eddn.edcd.io/schemas/fcmaterials_capi/1/test"           : "schemas/fcmaterials_capi-v1.0.json",

        "https://eddn.edcd.io/schemas/dockinggranted/1"               : "schemas/dockinggranted-v1.0.json",
        "https://eddn.edcd.io/schemas/dockinggranted/1/test"          : "schemas/dockinggranted-v1.0.json",
        "https://eddn.edcd.io/schemas/dockingdenied/1"                : "schemas/dockingdenied-v1.0.json",        
        "https://eddn.edcd.io/schemas/dockingdenied/1/test"           : "schemas/dockingdenied-v1.0.json",        
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

    MONITOR_HTTP_BIND_ADDRESS               = "0.0.0.0"
    MONITOR_HTTP_PORT                       = 9091

    MONITOR_RECEIVER_BINDINGS               = ["tcp://127.0.0.1:8500"]

    MONITOR_DB                              = {
        "user":     "eddn",
        "password": "cvLYM8AEqg29YTatFMEcqph3YkDWUMvC",
        "database": "eddn"
    }

    MONITOR_UA                              = "UA-496332-23"

    ##########################################################################
    #  Bouncer settings
    ##########################################################################
    BOUNCER_HTTP_BIND_ADDRESS               = "127.0.0.1"
    BOUNCER_HTTP_PORT                       = 8081

    BOUNCER_LIVE_GATEWAY_URL = 'https://eddn.edcd.io:4430/upload/'

    def loadFrom(self, fileName):
        f = open(fileName, 'r')
        conf = simplejson.load(f)
        for key, value in conf.iteritems():
            if key in dir(self):
                self.__setattr__(key, value)
            else:
                print "Ignoring unknown setting {0}".format(key)

Settings = _Settings()


def loadConfig(cl_args):
    """
    Load in a commandline-specified settings file, if applicable.

    A convenience method if you don't need other things specified as commandline
    options. Otherwise, point the filename to Settings.loadFrom().

    :param cl_args: An `argparse.parse_args()` return.
    """
    if cl_args.config:
        Settings.loadFrom(cl_args.config)
