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
from bottle import get, run as bottle_run
from eddn.conf import Settings

from gevent import monkey
monkey.patch_all()

from eddn.StatsCollector import StatsCollector

statsCollector = StatsCollector()
statsCollector.start()


@get('/stats/')
def stats():
    return simplejson.dumps(statsCollector.getSummary())


class Relay(Thread):

    def run(self):
        """
        Fires up the relay process.
        """
        # These form the connection to the Gateway daemon(s) upstream.
        context = zmq.Context()

        receiver = context.socket(zmq.SUB)
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
            # if is_message_duped(message):
        # We've already seen this message recently. Discard it.
            #    return

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
    r = Relay()
    r.start()
    bottle_run(host='0.0.0.0', port=9090, server='gevent')


if __name__ == '__main__':
    main()
