"""
Monitor sit below gateways, or another relay, and simply parse what it receives over SUB.
"""
from threading import Thread
import zlib
import gevent
import simplejson
import sqlite3
import datetime
import collections
import zmq.green as zmq
from bottle import get, request, response, run as bottle_run
from eddn._Conf.Settings import Settings, loadConfig

from gevent import monkey
monkey.patch_all()

def date(__format):
    d = datetime.datetime.utcnow()
    return d.strftime(__format)


@get('/getGateways/')
def getGateways():
    response.set_header("Access-Control-Allow-Origin", "*")
    gateways            = []
    
    for gateway in Settings.RELAY_RECEIVER_BINDINGS:
        gateways.append(gateway) 
    
    return simplejson.dumps(gateways)
    
@get('/getTotalSoftwares/')
def getTotalSoftwares():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    softwares   = collections.OrderedDict()
    
    maxDays     = request.GET.get('maxDays', '31').strip()
    maxDays     = int(maxDays) -1;
    
    query       = """SELECT name, SUM(hits) AS total, MAX(dateStats) AS maxDate 
                     FROM softwares 
                     GROUP BY name 
                     HAVING maxDate >= DATE('now', '""" + '-' + str(maxDays) + """ day')
                     ORDER BY total DESC"""
    results     = db.execute(query)
    
    for row in results:
        softwares[str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(softwares)
    
@get('/getSoftwares/')
def getSoftwares():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    softwares   = collections.OrderedDict()
    
    dateStart   = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd     = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()
    
    query       = """SELECT * 
                     FROM softwares 
                     WHERE dateStats BETWEEN ? AND ? 
                     ORDER BY hits DESC, dateStats ASC"""
    results     = db.execute(query, (dateStart, dateEnd))
    
    for row in results:
        if not str(row[2]) in softwares.keys():
            softwares[str(row[2])] = collections.OrderedDict()
         
        softwares[str(row[2])][str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(softwares)
    
@get('/getTotalUploaders/')
def getTotalUploaders():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    uploaders   = collections.OrderedDict()
    
    limit       = request.GET.get('limit', '20').strip()
    
    query       = """SELECT name, SUM(hits) AS total
                     FROM uploaders 
                     GROUP BY name 
                     ORDER BY total DESC
                     LIMIT """ + limit
    results     = db.execute(query)
    
    for row in results:
        uploaders[str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(uploaders)
    
@get('/getUploaders/')
def getUploaders():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    uploaders   = collections.OrderedDict()
    
    dateStart   = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd     = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()
    
    query       = """SELECT * 
                     FROM uploaders 
                     WHERE dateStats BETWEEN ? AND ? 
                     ORDER BY hits DESC, dateStats ASC"""
    results     = db.execute(query, (dateStart, dateEnd))
    
    for row in results:
        if not str(row[2]) in uploaders.keys():
            uploaders[str(row[2])] = collections.OrderedDict()
         
        uploaders[str(row[2])][str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(uploaders)
    
@get('/getTotalSchemas/')
def getTotalSchemas():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    schemas     = collections.OrderedDict()
    
    query       = """SELECT name, SUM(hits) AS total 
                     FROM schemas 
                     GROUP BY name 
                     ORDER BY total DESC"""
    results     = db.execute(query)
    
    for row in results:
        schemas[str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(schemas)
    
@get('/getSchemas/')
def getSchemas():
    response.set_header("Access-Control-Allow-Origin", "*")
    db          = sqlite3.connect(Settings.MONITOR_DB)
    schemas     = collections.OrderedDict()
    
    dateStart   = request.GET.get('dateStart', str(date('%Y-%m-%d'))).strip()
    dateEnd     = request.GET.get('dateEnd', str(date('%Y-%m-%d'))).strip()
    
    query       = """SELECT * 
                     FROM schemas 
                     WHERE dateStats BETWEEN ? AND ? 
                     ORDER BY hits DESC, dateStats ASC"""
    results     = db.execute(query, (dateStart, dateEnd))
    
    for row in results:
        if not str(row[2]) in schemas.keys():
            schemas[str(row[2])] = collections.OrderedDict()
         
        schemas[str(row[2])][str(row[0])] = str(row[1])
    
    db.close()
    
    return simplejson.dumps(schemas)



class Monitor(Thread):

    def run(self):
        context  = zmq.Context()
        
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        
        for binding in Settings.MONITOR_RECEIVER_BINDINGS:
            receiver.connect(binding)

        def monitor_worker(message):
            db          = sqlite3.connect(Settings.MONITOR_DB)
            
            if Settings.MONITOR_DECOMPRESS_MESSAGES:
                message = zlib.decompress(message)
            
            json    = simplejson.loads(message)
            
            # Update software count
            softwareID = json['header']['softwareName'] + ' | ' + json['header']['softwareVersion']
            
            c = db.cursor()
            c.execute('UPDATE softwares SET hits = hits + 1 WHERE `name` = ? AND `dateStats` = DATE("now", "utc")', (softwareID, ))
            c.execute('INSERT OR IGNORE INTO softwares (name, dateStats) VALUES (?, DATE("now", "utc"))', (softwareID, ))
            db.commit()
            
            
            # Update uploader count
            uploaderID = json['header']['uploaderID']
            
            c = db.cursor()
            c.execute('UPDATE uploaders SET hits = hits + 1 WHERE `name` = ? AND `dateStats` = DATE("now", "utc")', (uploaderID, ))
            c.execute('INSERT OR IGNORE INTO uploaders (name, dateStats) VALUES (?, DATE("now", "utc"))', (uploaderID, ))
            db.commit()
            
            
            # Update schemas count 
            schemaID = json['$schemaRef']
            
            c = db.cursor()
            c.execute('UPDATE schemas SET hits = hits + 1 WHERE `name` = ? AND `dateStats` = DATE("now", "utc")', (schemaID, ))
            c.execute('INSERT OR IGNORE INTO schemas (name, dateStats) VALUES (?, DATE("now", "utc"))', (schemaID, ))
            db.commit()
            
            db.close()

        while True:
            inboundMessage = receiver.recv()
            gevent.spawn(monitor_worker, inboundMessage)


def main():
    loadConfig()
    m = Monitor()
    m.start()
    bottle_run(host='0.0.0.0', port=9091, server='gevent')


if __name__ == '__main__':
    main()
