import zlib
import zmq
import simplejson
import sys
import time

"""
 "  Configuration
"""
__relayEDDN             = 'tcp://eddn.edcd.io:9500'
#__timeoutEDDN           = 600000 # 10 minuts
__timeoutEDDN           = 60000 # 1 minut



"""
 "  Start
"""    
def main():
    context     = zmq.Context()
    subscriber  = context.socket(zmq.SUB)
    
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    while True:
        try:
            subscriber.connect(__relayEDDN)
            print 'Connect to EDDN'
            sys.stdout.flush()
            
            poller = zmq.Poller()
            poller.register(subscriber, zmq.POLLIN)
 
            while True:
                socks = dict(poller.poll(__timeoutEDDN))
                if socks:
                    if socks.get(subscriber) == zmq.POLLIN:
                        __message   = subscriber.recv(zmq.NOBLOCK)
                        __message   = zlib.decompress(__message)
                        __json      = simplejson.loads(__message)

                        # call dumps() to ensure double quotes in output
                        print simplejson.dumps(__json)
                        sys.stdout.flush()
                else:
                    print 'Disconnect from EDDN (After timeout)'
                    sys.stdout.flush()
                    
                    subscriber.disconnect(__relayEDDN)
                    break
                
        except zmq.ZMQError, e:
            print 'Disconnect from EDDN (After receiving ZMQError)'
            print 'ZMQSocketException: ' + str(e)
            sys.stdout.flush()
            
            subscriber.disconnect(__relayEDDN)
            time.sleep(10)
            
        

if __name__ == '__main__':
    main()
