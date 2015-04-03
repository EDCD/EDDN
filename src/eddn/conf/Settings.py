'''
Created on 15 Nov 2014

@author: james
'''

from eddn import __version__ as version

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
