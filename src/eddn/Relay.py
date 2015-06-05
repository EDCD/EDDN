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

import gevent
import simplejson
import zmq.green as zmq
from bottle import get, response, run as bottle_run
from eddn.conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()

from eddn.core.StatsCollector import StatsCollector

statsCollector = StatsCollector()
statsCollector.start()

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

            if Settings.RELAY_DUPLICATE_MAX_MINUTES:
                if duplicateMessages.isDuplicated(message):
                    # We've already seen this message recently. Discard it.
                    statsCollector.tally("duplicate")
                    return

            if Settings.RELAY_DECOMPRESS_MESSAGES:
                message = zlib.decompress(message)

            sender.send(message)
            statsCollector.tally("outbound")

        logger.info("Relay is now listening for order data.")

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
    bottle_run(host='0.0.0.0', port=9090, server='gevent')


if __name__ == '__main__':
    main()
