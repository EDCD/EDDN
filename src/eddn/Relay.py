# coding: utf8

"""
Relays sit below an announcer, or another relay, and simply repeat what
they receive over PUB/SUB.
"""
import argparse
import gevent
import hashlib
import logging
import simplejson
import time
import uuid
import zlib
from threading import Thread

import zmq.green as zmq


# Logging has to be configured first before we do anything.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
__logger_channel = logging.StreamHandler()
__logger_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d: %(message)s'
    )
__logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
__logger_formatter.default_msec_format = '%s.%03d'
__logger_channel.setFormatter(__logger_formatter)
logger.addHandler(__logger_channel)
logger.info('Made logger')

from eddn.conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()
from bottle import Bottle, get, request, response, run
app = Bottle()


# This import must be done post-monkey-patching!
from eddn.core.StatsCollector import StatsCollector
statsCollector = StatsCollector()
statsCollector.start()

# This import must be done post-monkey-patching!
if Settings.RELAY_DUPLICATE_MAX_MINUTES:
    from eddn.core.DuplicateMessages import DuplicateMessages
    duplicateMessages = DuplicateMessages()
    duplicateMessages.start()


def parse_cl_args():
    parser = argparse.ArgumentParser(
        prog='Gateway',
        description='EDDN Gateway server',
    )

    parser.add_argument(
        '--loglevel',
        help='Logging level to output at',
    )

    parser.add_argument(
        '-c', '--config',
        metavar='config filename',
        nargs='?',
        default=None,
    )

    return parser.parse_args()

@app.route('/stats/', method=['OPTIONS', 'GET'])
def stats():
    stats = statsCollector.getSummary()
    stats["version"] = Settings.EDDN_VERSION
    return simplejson.dumps(stats)


class Relay(Thread):

    REGENERATE_UPLOADER_NONCE_INTERVAL = 3 * 60  # 3 minutes, was 12 hrs

    def __init__(self, **kwargs):
        super(Relay, self).__init__(**kwargs)
        self.uploader_nonce = None
        self.uploader_nonce_timestamp = 0
        self.generate_uploader_nonce()

    def generate_uploader_nonce(self):
        self.uploader_nonce = str(uuid.uuid4())
        self.uploader_nonce_timestamp = time.time()

    def scramble_uploader(self, uploader):
        now = time.time()
        if now - self.uploader_nonce_timestamp > self.REGENERATE_UPLOADER_NONCE_INTERVAL:
            self.generate_uploader_nonce()
        return hashlib.sha1("{}-{}".format(self.uploader_nonce, uploader.encode('utf8'))).hexdigest()

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
        sender.setsockopt(zmq.SNDHWM, 500)

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

            # Mask the uploader with a randomised nonce but still make it unique
            # for each uploader
            if 'uploaderID' in json['header']:
                json['header']['uploaderID'] = self.scramble_uploader(json['header']['uploaderID'])

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


class EnableCors(object):
    """Enable CORS responses."""

    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        """
        Apply a CORS handler.

        Ref: <https://stackoverflow.com/a/17262900>
        """
        def _enable_cors(*args, **kwargs):
            """Set CORS Headers."""
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


def main():
    cl_args = parse_cl_args()
    if cl_args.loglevel:
        logger.setLevel(cl_args.loglevel)

    loadConfig(cl_args)

    r = Relay()
    r.start()

    app.install(EnableCors())
    app.run(
        host=Settings.RELAY_HTTP_BIND_ADDRESS,
        port=Settings.RELAY_HTTP_PORT,
        server='gevent',
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE
    )


if __name__ == '__main__':
    main()
