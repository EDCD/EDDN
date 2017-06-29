# coding: utf8

"""
Contains the necessary ZeroMQ socket and a helper function to publish
market data to the Announcer daemons.
"""
import gevent
import hashlib
import logging
import simplejson
import urlparse
import zlib
import zmq.green as zmq
from datetime import datetime

from pkg_resources import resource_string
# import os

from eddn.conf.Settings import Settings, loadConfig
from eddn.core.Validator import Validator, ValidationSeverity

from gevent import monkey
monkey.patch_all()
from bottle import run, request, response, get, post

logger = logging.getLogger(__name__)

# This socket is used to push market data out to the Announcers over ZeroMQ.
context = zmq.Context()
sender = context.socket(zmq.PUB)

validator = Validator()

# This import must be done post-monkey-patching!
from eddn.core.StatsCollector import StatsCollector
statsCollector = StatsCollector()
statsCollector.start()


def configure():
    # Get the list of transports to bind from settings. This allows us to PUB
    # messages to multiple announcers over a variety of socket types
    # (UNIX sockets and/or TCP sockets).
    for binding in Settings.GATEWAY_SENDER_BINDINGS:
        sender.bind(binding)

    for schemaRef, schemaFile in Settings.GATEWAY_JSON_SCHEMAS.iteritems():
        validator.addSchemaResource(schemaRef, resource_string('eddn.Gateway', schemaFile))


def push_message(parsed_message, topic):
    """
    Spawned as a greenlet to push messages (strings) through ZeroMQ.
    This is a dumb method that just pushes strings; it assumes you've already validated
    and serialised as you want to.
    """
    string_message = simplejson.dumps(parsed_message, ensure_ascii=False).encode('utf-8')

    # Push a zlib compressed JSON representation of the message to
    # announcers with schema as topic
    compressed_msg = zlib.compress(string_message)
    
    send_message = "%s |-| %s" % (str(topic), compressed_msg)
    
    sender.send(send_message)
    statsCollector.tally("outbound")


def get_remote_address():
    """
    Determines the address of the uploading client. First checks the for
    proxy-forwarded headers, then falls back to request.remote_addr.
    :rtype: str
    """
    return request.headers.get('X-Forwarded-For', request.remote_addr)


def get_decompressed_message():
    """
    For upload formats that support it, detect gzip Content-Encoding headers
    and de-compress on the fly.
    :rtype: str
    :returns: The de-compressed request body.
    """
    content_encoding = request.headers.get('Content-Encoding', '')

    if content_encoding in ['gzip', 'deflate']:
        # Compressed request. We have to decompress the body, then figure out
        # if it's form-encoded.
        try:
            # Auto header checking.
            message_body = zlib.decompress(request.body.read(), 15 + 32)
        except zlib.error:
            # Negative wbits suppresses adler32 checksumming.
            message_body = zlib.decompress(request.body.read(), -15)

        # At this point, we're not sure whether we're dealing with a straight
        # un-encoded POST body, or a form-encoded POST. Attempt to parse the
        # body. If it's not form-encoded, this will return an empty dict.
        form_enc_parsed = urlparse.parse_qs(message_body)
        if form_enc_parsed:
            # This is a form-encoded POST. The value of the data attrib will
            # be the body we're looking for.
            try:
                message_body = form_enc_parsed['data'][0]
            except (KeyError, IndexError):
                raise MalformedUploadError(
                    "No 'data' POST key/value found. Check your POST key "
                    "name for spelling, and make sure you're passing a value."
                )
    else:
        # Uncompressed request. Bottle handles all of the parsing of the
        # POST key/vals, or un-encoded body.
        data_key = request.forms.get('data')
        if data_key:
            # This is a form-encoded POST. Support the silly people.
            message_body = data_key
        else:
            # This is a non form-encoded POST body.
            message_body = request.body.read()

    return message_body


def parse_and_error_handle(data):
    try:
        parsed_message = simplejson.loads(data)
    except (
        MalformedUploadError, TypeError, ValueError
    ) as exc:
        # Something bad happened. We know this will return at least a
        # semi-useful error message, so do so.
        response.status = 400
        logger.error("Error to %s: %s" % (get_remote_address(), exc.message))
        return str(exc)

    # Here we check if an outdated schema has been passed
    if parsed_message["$schemaRef"] in Settings.GATEWAY_OUTDATED_SCHEMAS:
        response.status = '426 Upgrade Required'  # Bottle (and underlying httplib) don't know this one
        statsCollector.tally("outdated")
        return "FAIL: The schema you have used is no longer supported. Please check for an updated version of your application."

    validationResults = validator.validate(parsed_message)

    if validationResults.severity <= ValidationSeverity.WARN:
        parsed_message['header']['gatewayTimestamp'] = datetime.utcnow().isoformat() + 'Z'

        ip_hash_salt = Settings.GATEWAY_IP_KEY_SALT
        if ip_hash_salt:
            # If an IP hash is set, salt+hash the uploader's IP address and set
            # it as the EDDN upload key value.
            ip_hash = hashlib.sha1(ip_hash_salt + get_remote_address()).hexdigest()
            parsed_message['header']['uploaderKey'] = ip_hash

        # Sends the parsed MarketOrderList or MarketHistoryList to the Announcers
        # as compressed JSON.
        gevent.spawn(push_message, parsed_message, parsed_message['$schemaRef'])
        logger.info("Accepted %s upload from %s" % (
            parsed_message, get_remote_address()
        ))
        return 'OK'
    else:
        response.status = 400
        statsCollector.tally("invalid")
        return "FAIL: " + str(validationResults.messages)


@post('/upload/')
def upload():
    try:
        # Body may or may not be compressed.
        message_body = get_decompressed_message()
    except zlib.error as exc:
        # Some languages and libs do a crap job zlib compressing stuff. Provide
        # at least some kind of feedback for them to try to get pointed in
        # the correct direction.
        response.status = 400
        logger.error("gzip error with %s: %s" % (get_remote_address(), exc.message))
        return exc.message
    except MalformedUploadError as exc:
        # They probably sent an encoded POST, but got the key/val wrong.
        response.status = 400
        logger.error("Error to %s: %s" % (get_remote_address(), exc.message))
        return exc.message

    statsCollector.tally("inbound")
    return parse_and_error_handle(message_body)


@get('/health_check/')
def health_check():
    """
    This should only be used by the gateway monitoring script. It is used
    to detect whether the gateway is still alive, and whether it should remain
    in the DNS rotation.
    """
    return Settings.EDDN_VERSION


@get('/stats/')
def stats():
    response.set_header("Access-Control-Allow-Origin", "*")
    stats = statsCollector.getSummary()
    stats["version"] = Settings.EDDN_VERSION
    return simplejson.dumps(stats)


class MalformedUploadError(Exception):
    """
    Raise this when an upload is structurally incorrect. This isn't so much
    to do with something like a bogus region ID, this is more like "You are
    missing a POST key/val, or a body".
    """
    pass


def main():
    loadConfig()
    configure()
    run(
        host=Settings.GATEWAY_HTTP_BIND_ADDRESS, 
        port=Settings.GATEWAY_HTTP_PORT, 
        server='gevent', 
        certfile='/etc/letsencrypt/live/eddn.edcd.io/fullchain.pem', 
        keyfile='/etc/letsencrypt/live/eddn.edcd.io/privkey.pem'
    )

if __name__ == '__main__':
    main()
