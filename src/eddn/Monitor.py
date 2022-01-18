# coding: utf8

"""
Monitor sit below gateways, or another relay, and simply parse what it receives over SUB.
"""
from threading import Thread
import argparse
import zlib
import gevent
import simplejson
import mysql.connector as mariadb
import datetime
import collections
import zmq.green as zmq
import re

from eddn.conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()
from bottle import Bottle, get, request, response, run
app = Bottle()

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
        help='CURRENTLY NO EFFECT - Logging level to output at',
    )

    parser.add_argument(
        '-c', '--config',
        metavar='config filename',
        nargs='?',
        default=None,
    )

    return parser.parse_args()

def date(__format):
    d = datetime.datetime.utcnow()
    return d.strftime(__format)


@app.route('/ping', method=['OPTIONS', 'GET'])
def ping():
    return 'pong'


@app.route('/getTotalSoftwares/', method=['OPTIONS', 'GET'])
def getTotalSoftwares():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
    softwares = collections.OrderedDict()

    maxDays = request.GET.get('maxDays', '31').strip()
    maxDays = int(maxDays) - 1

    query = """SELECT name, SUM(hits) AS total, MAX(dateStats) AS maxDate
               FROM softwares
               GROUP BY name
               HAVING maxDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
               ORDER BY total DESC"""

    results = db.cursor()
    results.execute(query, (maxDays, ))

    for row in results:
        softwares[row[0].encode('utf8')] = str(row[1])

    db.close()

    return simplejson.dumps(softwares)


@app.route('/getSoftwares/', method=['OPTIONS', 'GET'])
def getSoftwares():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
    softwares = collections.OrderedDict()

    dateStart = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()

    query = """SELECT *
               FROM `softwares`
               WHERE `dateStats` BETWEEN %s AND %s
               ORDER BY `hits` DESC, `dateStats` ASC"""

    results = db.cursor()
    results.execute(query, (dateStart, dateEnd))

    for row in results:
        currentDate = row[2].strftime('%Y-%m-%d')
        if not currentDate in softwares.keys():
            softwares[currentDate] = collections.OrderedDict()

        softwares[currentDate][str(row[0])] = str(row[1])

    db.close()

    return simplejson.dumps(softwares)


@app.route('/getTotalSchemas/', method=['OPTIONS', 'GET'])
def getTotalSchemas():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
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


@app.route('/getSchemas/', method=['OPTIONS', 'GET'])
def getSchemas():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
    #db.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    schemas = collections.OrderedDict()

    dateStart = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()

    query = """SELECT *
               FROM `schemas`
               WHERE `dateStats` BETWEEN %s AND %s
               ORDER BY `hits` DESC, `dateStats` ASC"""

    results = db.cursor()
    results.execute(query, (dateStart, dateEnd))

    for row in results:
        currentDate = row[2].strftime('%Y-%m-%d')
        if not currentDate in schemas.keys():
            schemas[currentDate] = collections.OrderedDict()

        schemas[currentDate][str(row[0])] = str(row[1])

    db.close()

    return simplejson.dumps(schemas)


class Monitor(Thread):

    def run(self):
        context = zmq.Context()

        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')

        for binding in Settings.MONITOR_RECEIVER_BINDINGS:
            receiver.connect(binding)

        def monitor_worker(message):
            db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])

            # Separate topic from message
            message = message.split(' |-| ')

            # Handle gateway not sending topic
            if len(message) > 1:
                message = message[1]
            else:
                message = message[0]

            message = zlib.decompress(message)
            json    = simplejson.loads(message)

            # Default variables
            schemaID    = json['$schemaRef']
            softwareID  = json['header']['softwareName'].encode('utf8') + ' | ' + json['header']['softwareVersion'].encode('utf8')

            uploaderID  = json['header']['uploaderID'].encode('utf8')
            uploaderIP  = None
            if 'uploaderIP' in json['header']:
                uploaderIP = json['header']['uploaderIP'].encode('utf8')

            # Duplicates?
            if Settings.RELAY_DUPLICATE_MAX_MINUTES:
                if duplicateMessages.isDuplicated(json):
                    schemaID = 'DUPLICATE MESSAGE'

                    c = db.cursor()
                    c.execute('UPDATE `schemas` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (schemaID, ))
                    c.execute('INSERT IGNORE INTO `schemas` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (schemaID, ))
                    db.commit()

                    db.close()

                    return

            # Update software count
            c = db.cursor()
            c.execute('UPDATE `softwares` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (softwareID, ))
            c.execute('INSERT IGNORE INTO `softwares` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (softwareID, ))
            db.commit()

            # Update schemas count
            c = db.cursor()
            c.execute('UPDATE `schemas` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (schemaID, ))
            c.execute('INSERT IGNORE INTO `schemas` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (schemaID, ))
            db.commit()

            db.close()

        while True:
            inboundMessage = receiver.recv()
            gevent.spawn(monitor_worker, inboundMessage)


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
    loadConfig(cl_args)

    m = Monitor()
    m.start()
    app.install(EnableCors())
    app.run(
        host=Settings.MONITOR_HTTP_BIND_ADDRESS,
        port=Settings.MONITOR_HTTP_PORT,
        server='gevent',
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE
    )


if __name__ == '__main__':
    main()
