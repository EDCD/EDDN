# coding: utf8

"""
Monitor sit below gateways, or another relay, and simply parse what it receives over SUB.
"""
from threading import Thread
import zlib
import gevent
import simplejson
import mysql.connector as mariadb
import datetime
import collections
import zmq.green as zmq
import re

from bottle import get, request, response, run as bottle_run
from eddn.conf.Settings import Settings, loadConfig
from eddn.core.Analytics import Analytics

from gevent import monkey
monkey.patch_all()

# This import must be done post-monkey-patching!
if Settings.RELAY_DUPLICATE_MAX_MINUTES:
    from eddn.core.DuplicateMessages import DuplicateMessages
    duplicateMessages = DuplicateMessages()
    duplicateMessages.start()


def date(__format):
    d = datetime.datetime.utcnow()
    return d.strftime(__format)


@get('/ping')
def ping():
    return 'pong'


@get('/getTotalSoftwares/')
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


@get('/getSoftwares/')
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


'''
@get('/getTotalUploaders/')
def getTotalUploaders():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
    uploaders = collections.OrderedDict()

    limit = request.GET.get('limit', '20').strip()

    query = """SELECT `name`, SUM(`hits`) AS `total`
               FROM `uploaders`
               GROUP BY `name`
               ORDER BY `total` DESC
               LIMIT %s"""

    results = db.cursor()
    results.execute(query, (int(limit), ))

    for row in results:
        uploaders[row[0].encode('utf8')] = row[1]

    db.close()

    return simplejson.dumps(uploaders)


@get('/getUploaders/')
def getUploaders():
    response.set_header("Access-Control-Allow-Origin", "*")
    db = mariadb.connect(user=Settings.MONITOR_DB['user'], password=Settings.MONITOR_DB['password'], database=Settings.MONITOR_DB['database'])
    uploaders = collections.OrderedDict()

    dateStart = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()

    query = """SELECT *
               FROM `uploaders`
               WHERE `dateStats` BETWEEN %s AND %s
               ORDER BY `hits` DESC, `dateStats` ASC"""

    results = db.cursor()
    results.execute(query, (dateStart, dateEnd))

    for row in results:
        currentDate = row[2].strftime('%Y-%m-%d')
        if not currentDate in uploaders.keys():
            uploaders[currentDate] = collections.OrderedDict()

        uploaders[currentDate][row[0].encode('utf8')] = row[1]

    db.close()

    return simplejson.dumps(uploaders)
'''


@get('/getTotalSchemas/')
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


@get('/getSchemas/')
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

        analytics = Analytics()

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
                    analytics.hit('DUPLICATE', uploaderID, uploaderIP)

                    return

            # Update software count
            c = db.cursor()
            c.execute('UPDATE `softwares` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (softwareID, ))
            c.execute('INSERT IGNORE INTO `softwares` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (softwareID, ))
            db.commit()

            # Update uploader count
            if uploaderID:  # Don't get empty uploaderID
                c = db.cursor()
                c.execute('UPDATE `uploaders` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (uploaderID, ))
                c.execute('INSERT IGNORE INTO `uploaders` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (uploaderID, ))
                db.commit()

            # Update schemas count
            c = db.cursor()
            c.execute('UPDATE `schemas` SET `hits` = `hits` + 1 WHERE `name` = %s AND `dateStats` = UTC_DATE()', (schemaID, ))
            c.execute('INSERT IGNORE INTO `schemas` (`name`, `dateStats`) VALUES (%s, UTC_DATE())', (schemaID, ))
            db.commit()

            db.close()

            if re.search('test', schemaID, re.I):
                analytics.hit(Settings.GATEWAY_JSON_SCHEMAS[schemaID] + '#test', uploaderID, uploaderIP)
            else:
                analytics.hit(Settings.GATEWAY_JSON_SCHEMAS[schemaID], uploaderID, uploaderIP)

        while True:
            inboundMessage = receiver.recv()
            gevent.spawn(monitor_worker, inboundMessage)


def main():
    loadConfig()
    m = Monitor()
    m.start()
    bottle_run(
        host=Settings.MONITOR_HTTP_BIND_ADDRESS,
        port=Settings.MONITOR_HTTP_PORT,
        server='gevent',
        certfile=Settings.CERT_FILE,
        keyfile=Settings.KEY_FILE
    )


if __name__ == '__main__':
    main()
