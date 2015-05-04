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
from eddn._Conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()

class Monitor(Thread):

    def run(self):
        context  = zmq.Context()
        
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        
        for binding in Settings.RELAY_RECEIVER_BINDINGS:
            receiver.connect(binding)

        def monitor_worker(message):
            if Settings.RELAY_DECOMPRESS_MESSAGES:
                message = zlib.decompress(message)

            # Here we monitor different types of messages
            

        while True:
            inboundMessage = receiver.recv()
            gevent.spawn(relay_monitor, inboundMessage)


def main():
    loadConfig()
    m = Monitor()
    m.start()
    bottle_run(host='0.0.0.0', port=9091, server='gevent')


if __name__ == '__main__':
    main()
