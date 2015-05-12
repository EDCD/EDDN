import zlib
import zmq
import simplejson
import sys

"""
 "  Configuration
"""
__relayEDDN             = 'tcp://eddn-relay.elite-markets.net:9500'
__timeoutEDDN           = 600000



"""
 "  Start
"""    
def main():
    context     = zmq.Context()
    subscriber  = context.socket(zmq.SUB)
    
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    subscriber.setsockopt(zmq.RCVTIMEO, __timeoutEDDN)

    while True:
        try:
            subscriber.connect(__relayEDDN)
            
            while True:
                __message   = subscriber.recv()
                
                if __message == False:
                    subscriber.disconnect(__relayEDDN)
                    break
                
                __message   = zlib.decompress(__message)
                __json      = simplejson.loads(__message)
                
                
                print __json
                sys.stdout.flush()
                
        except zmq.ZMQError, e:
            print 'ZMQSocketException: ' + str(e)
            sys.stdout.flush()
            time.sleep(10)
            
        

if __name__ == '__main__':
    main()
