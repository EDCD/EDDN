# coding: utf8

"""
Bouncer script to forward received messages to a Gateway.

This is intended to be used if performing a server migration of the live
service.

DNS updates can be slow, especially with multiple layers of caching
involved, some of which might not respect declared TTLs.  So use this to
listen for new messages from EDDN client/senders and forward them on to
where the new Gateway is running.

Architecture:

  1. The /upload/ bottle route, `upload()`,  receives messages, as if this
    was a Gateway.

  2. The payload is extracted using `get_decompressed_message()`, as the
    message *may* be compressed, but might not be.

  3. The result of that is passed on to forward_message()
    which spawns a greenlet to actually send the message on using
    `push_message()`.

  4. `push_message()` then sends the message to the configured live/real
    Gateway.
"""
import argparse
import logging
import zlib
from datetime import datetime
from typing import Callable

import gevent
import requests
import simplejson
import urlparse
from bottle import Bottle, request, response
from gevent import monkey

from eddn.conf.Settings import Settings, load_config

monkey.patch_all()

app = Bottle()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
__logger_channel = logging.StreamHandler()
__logger_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d: %(message)s"
    )
__logger_formatter.default_time_format = "%Y-%m-%d %H:%M:%S"
__logger_formatter.default_msec_format = "%s.%03d"
__logger_channel.setFormatter(__logger_formatter)
logger.addHandler(__logger_channel)
logger.info("Made logger")


# This import must be done post-monkey-patching!
from eddn.core.StatsCollector import StatsCollector  # noqa: E402

stats_collector = StatsCollector()
stats_collector.start()


def parse_cl_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="Gateway",
        description="EDDN Gateway server",
    )

    parser.add_argument(
        "--loglevel",
        help="Logging level to output at",
    )

    parser.add_argument(
        "-c", "--config",
        metavar="config filename",
        nargs="?",
        default=None,
    )

    return parser.parse_args()


def push_message(message_body: str) -> None:
    """
    Push a message our to subscribed listeners.

    Spawned as a greenlet to push messages (strings) through ZeroMQ.
    This is a dumb method that just pushes strings; it assumes you've already
    validated and serialised as you want to.
    """
    try:
        r = requests.post(
            Settings.BOUNCER_LIVE_GATEWAY_URL,
            data=message_body,
        )

    except Exception as e:
        logger.error("Failed sending message on", exc_info=e)

    else:
        if r.status_code != requests.codes.ok:
            logger.error(f"Response from {Settings.BOUNCER_LIVE_GATEWAY_URL}:\n{r.text}\n")

        else:
            stats_collector.tally("outbound")


def get_remote_address() -> str:
    """
    Determine the address of the uploading client.

    First checks the for proxy-forwarded headers, then falls back to
    request.remote_addr.
    :returns: Best attempt at remote address.
    """
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def get_decompressed_message() -> bytes:
    """
    Detect gzip Content-Encoding headers and de-compress on the fly.

    For upload formats that support it.
    :returns: The de-compressed request body.
    """
    content_encoding = request.headers.get("Content-Encoding", "")

    if content_encoding in ["gzip", "deflate"]:
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
                message_body = form_enc_parsed["data"][0]
            except (KeyError, IndexError):
                raise MalformedUploadError(
                    "No 'data' POST key/value found. Check your POST key "
                    "name for spelling, and make sure you're passing a value."
                )
    else:
        # Uncompressed request. Bottle handles all of the parsing of the
        # POST key/vals, or un-encoded body.
        data_key = request.forms.get("data")
        if data_key:
            # This is a form-encoded POST. Support the silly people.
            message_body = data_key
        else:
            # This is a non form-encoded POST body.
            message_body = request.body.read()

    return message_body


def forward_message(message_body: bytes) -> str:
    """
    Send the parsed message to the Relay/Monitor as compressed JSON.

    :param message_body: Incoming message.
    :returns: "OK" assuming it is.
    """
    # TODO: This instead needs to send the message to remote Gateway
    gevent.spawn(push_message, message_body)
    logger.info(f"Accepted upload from {get_remote_address()}")

    return "OK"


@app.route("/upload/", method=["OPTIONS", "POST"])
def upload() -> str:
    """
    Handle an /upload/ request.

    :returns: The processed message, else error string.
    """
    try:
        # Body may or may not be compressed.
        message_body = get_decompressed_message()

    except zlib.error as exc:
        # Some languages and libs do a crap job zlib compressing stuff. Provide
        # at least some kind of feedback for them to try to get pointed in
        # the correct direction.
        response.status = 400
        logger.error(f"gzip error with {get_remote_address()}: {exc}")

        return f"{exc}"

    except MalformedUploadError as exc:
        # They probably sent an encoded POST, but got the key/val wrong.
        response.status = 400
        logger.error(f"Error to {get_remote_address()}: {exc}")

        return f"{exc}"

    stats_collector.tally("inbound")
    return forward_message(message_body)


@app.route("/health_check/", method=["OPTIONS", "GET"])
def health_check() -> str:
    """
    Return our version string in as an "am I awake" signal.

    This should only be used by the gateway monitoring script. It is used
    to detect whether the gateway is still alive, and whether it should remain
    in the DNS rotation.

    :returns: Version of this software.
    """
    return Settings.EDDN_VERSION


@app.route("/stats/", method=["OPTIONS", "GET"])
def stats() -> str:
    """
    Return some stats about the Gateway's operation so far.

    :return: JSON stats data
    """
    stats_current = stats_collector.get_summary()
    stats_current["version"] = Settings.EDDN_VERSION

    return simplejson.dumps(stats_current)


class MalformedUploadError(Exception):
    """
    Exception for malformed upload.

    Raise this when an upload is structurally incorrect. This isn't so much
    to do with something like a bogus region ID, this is more like "You are
    missing a POST key/val, or a body".
    """

    pass


class EnableCors(object):
    """Handle enabling CORS headers in all responses."""

    name = "enable_cors"
    api = 2

    def apply(self, fn: Callable):
        """
        Apply CORS headers to the calling bottle app.

        :param fn:
        :param context:
        :return:
        """
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = \
                "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"

            if request.method != "OPTIONS":
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


class CustomLogging(object):
    """Wrap a Bottle request so that a log line is emitted after it's handled."""

    name = "custom_logging"
    api = 2

    def apply(self, fn: Callable):
        """
        Apply custom logging to bottle request.

        :param fn:
        :param context:
        :return:
        """
        def _log_to_logger(*args, **kwargs):
            request_time = datetime.utcnow()
            actual_response = fn(*args, **kwargs)

            # logger.info("Request:\n%s\n", request)
            if len(request.remote_route) > 1:
                remote_addr = request.remote_route[1]

            else:
                remote_addr = request.remote_addr

            logger.info(f"{remote_addr} {request_time} {request.method} {request.url} {response.status}")

            return actual_response

        return _log_to_logger


def main() -> None:
    """Handle setting up and running the bottle app."""
    cl_args = parse_cl_args()
    if cl_args.loglevel:
        logger.setLevel(cl_args.loglevel)

    logger.info("Loading config...")
    load_config(cl_args)

    logger.info("Installing EnableCors ...")
    app.install(EnableCors())
    logger.info("Installing CustomLogging ...")
    app.install(CustomLogging())
    logger.info("Running bottle app ...")
    app.run(
        host=Settings.BOUNCER_HTTP_BIND_ADDRESS,
        port=Settings.BOUNCER_HTTP_PORT,
        server="gevent",
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE,
        quiet=True,
    )


if __name__ == "__main__":
    main()
