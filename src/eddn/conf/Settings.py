'''
Created on 15 Nov 2014

@author: james
'''

import logging.config

###############################################################################
# Relay settings
###############################################################################

RELAY_RECEIVER_BINDINGS = ["tcp://127.0.0.1:8500"]

RELAY_SENDER_BINDINGS = ["tcp://127.0.0.1:9500"]

RELAY_DECOMPRESS_MESSAGES = False

###############################################################################
#  Gateway settings
###############################################################################

GATEWAY_SENDER_BINDINGS = ["tcp://127.0.0.1:8500"]

###############################################################################
# Logging Settings
###############################################################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(name)s -- %(levelname)s -- %(asctime)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

logging.config.dictConfig(LOGGING)
