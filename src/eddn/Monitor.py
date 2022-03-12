"""EDDN Monitor, which records stats about incoming messages."""
# coding: utf8

import argparse
import collections
import datetime
import zlib
from threading import Thread
from typing import OrderedDict

import gevent
import mysql.connector as mariadb
import simplejson
import zmq.green as zmq
from bottle import Bottle, request, response
from gevent import monkey
from zmq import SUB as ZMQ_SUB
from zmq import SUBSCRIBE as ZMQ_SUBSCRIBE

from eddn.conf.Settings import Settings, load_config

monkey.patch_all()

app = Bottle()

# This import must be done post-monkey-patching!
if Settings.RELAY_DUPLICATE_MAX_MINUTES:
    from eddn.core.DuplicateMessages import DuplicateMessages

    duplicate_messages = DuplicateMessages()
    duplicate_messages.start()


def parse_cl_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="Gateway",
        description="EDDN Gateway server",
    )

    parser.add_argument(
        "--loglevel",
        help="CURRENTLY NO EFFECT - Logging level to output at",
    )

    parser.add_argument(
        "-c",
        "--config",
        metavar="config filename",
        nargs="?",
        default=None,
    )

    return parser.parse_args()


def date(__format) -> str:
    """
    Make a "now" datetime as per the supplied format.

    :param __format:
    :return: String representation of "now"
    """
    d = datetime.datetime.utcnow()
    return d.strftime(__format)


@app.route("/ping", method=["OPTIONS", "GET"])
def ping() -> str:
    """Respond to a ping request."""
    return "pong"


@app.route("/getTotalSoftwares/", method=["OPTIONS", "GET"])
def get_total_softwares() -> str:
    """Respond with data about total uploading software counts."""
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(
        user=Settings.MONITOR_DB["user"],
        password=Settings.MONITOR_DB["password"],
        database=Settings.MONITOR_DB["database"],
    )
    softwares = collections.OrderedDict()

    max_days = request.GET.get("maxDays", "31").strip()
    max_days = int(max_days) - 1

    query = """SELECT name, SUM(hits) AS total, MAX(dateStats) AS maxDate
               FROM softwares
               GROUP BY name
               HAVING maxDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
               ORDER BY total DESC"""

    results = db.cursor()
    results.execute(query, (max_days,))

    for row in results:
        softwares[row[0].encode("utf8")] = str(row[1])

    db.close()

    return simplejson.dumps(softwares)


@app.route("/getSoftwares/", method=["OPTIONS", "GET"])
def get_softwares() -> str:
    """Respond with hit stats for all uploading software."""
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(
        user=Settings.MONITOR_DB["user"],
        password=Settings.MONITOR_DB["password"],
        database=Settings.MONITOR_DB["database"],
    )
    softwares: OrderedDict = collections.OrderedDict()

    date_start = request.GET.get("dateStart", str(date("%Y-%m-%d"))).strip()
    date_end = request.GET.get("dateEnd", str(date("%Y-%m-%d"))).strip()

    query = """SELECT *
               FROM `softwares`
               WHERE `dateStats` BETWEEN %s AND %s
               ORDER BY `hits` DESC, `dateStats` ASC"""

    results = db.cursor()
    results.execute(query, (date_start, date_end))

    for row in results:
        current_date = row[2].strftime("%Y-%m-%d")
        if current_date not in softwares.keys():
            softwares[current_date] = collections.OrderedDict()

        softwares[current_date][str(row[0])] = str(row[1])

    db.close()

    return simplejson.dumps(softwares)


@app.route("/getTotalSchemas/", method=["OPTIONS", "GET"])
def get_total_schemas() -> str:
    """Respond with total hit stats for all schemas."""
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(
        user=Settings.MONITOR_DB["user"],
        password=Settings.MONITOR_DB["password"],
        database=Settings.MONITOR_DB["database"],
    )
    schemas = collections.OrderedDict()

    query = """SELECT `name`, SUM(`hits`) AS `total`
               FROM `schemas`
               GROUP BY `name`
               ORDER BY `total` DESC"""

    results = db.cursor()
    results.execute(query)

    for row in results:
        schemas[str(row[0])] = row[1]

    db.close()

    return simplejson.dumps(schemas)


@app.route("/getSchemas/", method=["OPTIONS", "GET"])
def get_schemas() -> str:
    """Respond with schema hit stats between given datetimes."""
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(
        user=Settings.MONITOR_DB["user"],
        password=Settings.MONITOR_DB["password"],
        database=Settings.MONITOR_DB["database"],
    )
    schemas: OrderedDict = collections.OrderedDict()

    date_start = request.GET.get("dateStart", str(date("%Y-%m-%d"))).strip()
    date_end = request.GET.get("dateEnd", str(date("%Y-%m-%d"))).strip()

    query = """SELECT *
               FROM `schemas`
               WHERE `dateStats` BETWEEN %s AND %s
               ORDER BY `hits` DESC, `dateStats` ASC"""

    results = db.cursor()
    results.execute(query, (date_start, date_end))

    for row in results:
        current_date = row[2].strftime("%Y-%m-%d")
        if current_date not in schemas.keys():
            schemas[current_date] = collections.OrderedDict()

        schemas[current_date][str(row[0])] = str(row[1])

    db.close()

    return simplejson.dumps(schemas)


class Monitor(Thread):
    """Monitor thread class."""

    def run(self) -> None:
        """Handle receiving Gateway messages and recording stats."""
        context = zmq.Context()

        receiver = context.socket(ZMQ_SUB)
        receiver.setsockopt_string(ZMQ_SUBSCRIBE, "")

        for binding in Settings.MONITOR_RECEIVER_BINDINGS:
            receiver.connect(binding)

        def monitor_worker(message: bytes) -> None:
            db = mariadb.connect(
                user=Settings.MONITOR_DB["user"],
                password=Settings.MONITOR_DB["password"],
                database=Settings.MONITOR_DB["database"],
            )

            message_text = zlib.decompress(message)
            json = simplejson.loads(message_text)

            # Default variables
            schema_id = json["$schemaRef"]
            software_id = f"{json['header']['softwareName']} | {json['header']['softwareVersion']}"

            # Duplicates?
            if Settings.RELAY_DUPLICATE_MAX_MINUTES:
                if duplicate_messages.is_duplicated(json):
                    schema_id = "DUPLICATE MESSAGE"

                    c = db.cursor()
                    c.execute(
                        "UPDATE `schemas` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()",
                        (schema_id,),
                    )
                    c.execute(
                        "INSERT IGNORE INTO `schemas` (`name`, `dateStats`) VALUES (%s, UTC_DATE())", (schema_id,)
                    )
                    db.commit()

                    db.close()

                    return

            # Update software count
            c = db.cursor()
            c.execute(
                "UPDATE `softwares` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()",
                (software_id,),
            )
            c.execute("INSERT IGNORE INTO `softwares` (`name`, `dateStats`) VALUES (%s, UTC_DATE())", (software_id,))
            db.commit()

            # Update schemas count
            c = db.cursor()
            c.execute(
                "UPDATE `schemas` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()", (schema_id,)
            )
            c.execute("INSERT IGNORE INTO `schemas` (`name`, `dateStats`) VALUES (%s, UTC_DATE())", (schema_id,))
            db.commit()

            db.close()

        while True:
            inbound_message = receiver.recv()
            gevent.spawn(monitor_worker, inbound_message)


def apply_cors() -> None:
    """
    Apply a CORS handler.

    Ref: <https://stackoverflow.com/a/17262900>
    """
    response.set_header("Access-Control-Allow-Origin", "*")
    response.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    response.set_header("Access-Control-Allow-Headers", "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token")


def main() -> None:
    """Handle setting up and running the bottle app."""
    cl_args = parse_cl_args()
    load_config(cl_args)

    m = Monitor()
    m.start()
    app.add_hook("after_request", apply_cors)
    app.run(
        host=Settings.MONITOR_HTTP_BIND_ADDRESS,
        port=Settings.MONITOR_HTTP_PORT,
        server="gevent",
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE,
    )


if __name__ == "__main__":
    main()
