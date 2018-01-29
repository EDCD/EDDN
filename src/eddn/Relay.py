# coding: utf8

"""
Relays sit below an announcer, or another relay, and simply repeat what
they receive over PUB/SUB.
"""
# Logging has to be configured first before we do anything.
import logging
from threading import Thread

logger = logging.getLogger(__name__)
import zlib

import random
import string
import hashlib

import gevent
import simplejson
import zmq.green as zmq
from bottle import get, response, run as bottle_run
from eddn.conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()

# This import must be done post-monkey-patching!
from eddn.core.StatsCollector import StatsCollector
statsCollector = StatsCollector()
statsCollector.start()

# This import must be done post-monkey-patching!
if Settings.RELAY_DUPLICATE_MAX_MINUTES:
    from eddn.core.DuplicateMessages import DuplicateMessages
    duplicateMessages = DuplicateMessages()
    duplicateMessages.start()


@get('/stats/')
def stats():
    response.set_header("Access-Control-Allow-Origin", "*")
    stats = statsCollector.getSummary()
    stats["version"] = Settings.EDDN_VERSION
    return simplejson.dumps(stats)


def onetime_prefix():
    """
    Return random string 8 character string
    :return:
    """
    prefix = ""
    while len(prefix) < 8:
        prefix += random.choice(string.lowercase + string.digits + string.uppercase)
    return prefix


# used by scramble_uploader to give a unique "key" each time the relay process is started
_onetime_prefix_value = onetime_prefix()


def scramble_uploader(uploaderId):
    """
    Make a one-way hash of the uploader that can't be undone from.

    This is kind of like an HMac with _onetime_prefix_value as an ephemeral key.
    the public data
    :param uploaderId:
    :return:
    """
    hasher = hashlib.sha1()
    hasher.update(_onetime_prefix_value + uploaderId)
    return hasher.hexdigest()[:20]


class Relay(Thread):

    def run(self):
        """
        Fires up the relay process.
        """
        # These form the connection to the Gateway daemon(s) upstream.
        context = zmq.Context()

        receiver = context.socket(zmq.SUB)

        # Filters on topics or not...
        if Settings.RELAY_RECEIVE_ONLY_GATEWAY_EXTRA_JSON is True:
            for schemaRef, schemaFile in Settings.GATEWAY_JSON_SCHEMAS.iteritems():
                receiver.setsockopt(zmq.SUBSCRIBE, schemaRef)
            for schemaRef, schemaFile in Settings.RELAY_EXTRA_JSON_SCHEMAS.iteritems():
                receiver.setsockopt(zmq.SUBSCRIBE, schemaRef)
        else:
            receiver.setsockopt(zmq.SUBSCRIBE, '')

        for binding in Settings.RELAY_RECEIVER_BINDINGS:
            # Relays bind upstream to an Announcer, or another Relay.
            receiver.connect(binding)

        sender = context.socket(zmq.PUB)

        for binding in Settings.RELAY_SENDER_BINDINGS:
            # End users, or other relays, may attach here.
            sender.bind(binding)

        def relay_worker(message):
            """
                This is the worker function that re-sends the incoming messages out
                to any subscribers.
                :param str message: A JSON string to re-broadcast.
            """
            # Separate topic from message
            message = message.split(' |-| ')

            # Handle gateway not sending topic
            if len(message) > 1:
                message = message[1]
            else:
                message = message[0]

            message = zlib.decompress(message)
            json    = simplejson.loads(message)
            
            # Handle duplicate message
            if Settings.RELAY_DUPLICATE_MAX_MINUTES:
                if duplicateMessages.isDuplicated(json):
                    # We've already seen this message recently. Discard it.
                    statsCollector.tally("duplicate")
                    return
            
            # Scramble ID to end consumer (Avoid realtime user tracking without their consent)
            if 'uploaderID' in json['header']:
                json['header']['uploaderID'] = scramble_uploader(json['header']['uploaderID'])
            
            # Remove IP to end consumer
            if 'uploaderIP' in json['header']:
                del json['header']['uploaderIP']
            
            # Convert message back to JSON
            message = simplejson.dumps(json, sort_keys=True)
            
            # Recompress message
            message = zlib.compress(message)
            
            # Send message
            sender.send(message)
            statsCollector.tally("outbound")

        while True:
            # For each incoming message, spawn a greenlet using the relay_worker
            # function.
            inboundMessage = receiver.recv()
            statsCollector.tally("inbound")
            gevent.spawn(relay_worker, inboundMessage)


def main():
    loadConfig()
    r = Relay()
    r.start()
    bottle_run(
        host=Settings.RELAY_HTTP_BIND_ADDRESS, 
        port=Settings.RELAY_HTTP_PORT, 
        server='gevent', 
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE
    )


if __name__ == '__main__':
    main()
