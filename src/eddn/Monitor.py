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

import sqlite3
import sys
import datetime

def date(__format):
    d = datetime.datetime.utcnow()
    return d.strftime(__format)

class Monitor(Thread):

    def run(self):
        context  = zmq.Context()
        
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        
        for binding in Settings.MONITOR_RECEIVER_BINDINGS:
            receiver.connect(binding)

        def monitor_worker(message):
            db          = sqlite3.connect(Settings.MONITOR_DB)
            currentDate = str(date('%Y-%m-%d'))
            
        
            if Settings.MONITOR_DECOMPRESS_MESSAGES:
                message = zlib.decompress(message)
            
            json    = simplejson.loads(message)
            
            # Update software count
            softwareID = json['header']['softwareName'] + ' | ' + json['header']['softwareVersion']
            
            c = db.cursor()
            c.execute('UPDATE uploaders SET hits = hits + 1 WHERE `name` = ? AND `dateStats` = ?', (softwareID, currentDate))
            c.execute('INSERT OR IGNORE INTO uploaders (name, dateStats) VALUES (?, ?)', (softwareID, currentDate))
            db.commit()
            
            
            # Update schemas count 
            schemaID = json['$schemaRef']
            
            c = db.cursor()
            c.execute('UPDATE schemas SET hits = hits + 1 WHERE `name` = ? AND `dateStats` = ?', (schemaID, currentDate))
            c.execute('INSERT OR IGNORE INTO schemas (name, dateStats) VALUES (?, ?)', (schemaID, currentDate))
            db.commit()
            
            
            print softwareID
            print schemaID
            print currentDate
            sys.stdout.flush()
            
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
