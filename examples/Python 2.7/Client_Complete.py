import zlib
import zmq
import simplejson
import sys, os, datetime, time

"""
 "  Configuration
"""
__relayEDDN             = 'tcp://eddn.edcd.io:9500'
#__timeoutEDDN           = 600000 # 10 minuts
__timeoutEDDN           = 60000 # 1 minut

# Set False to listen to production stream; True to listen to debug stream
__debugEDDN             = False;

# Set to False if you do not want verbose logging
__logVerboseFile        = os.path.dirname(__file__) + '/Logs_Verbose_EDDN_%DATE%.htm'
#__logVerboseFile        = False

# Set to False if you do not want JSON logging
__logJSONFile           = os.path.dirname(__file__) + '/Logs_JSON_EDDN_%DATE%.log'
#__logJSONFile           = False

# A sample list of authorised softwares
__authorisedSoftwares   = [
    "EDCE",
    "ED-TD.SPACE",
    "EliteOCR",
    "Maddavo's Market Share",
    "RegulatedNoise",
    "RegulatedNoise__DJ",
    "E:D Market Connector [Windows]"
]

# Used this to excludes yourself for example has you don't want to handle your own messages ^^
__excludedSoftwares     = [
    'My Awesome Market Uploader'
]



"""
 "  Start
"""
def date(__format):
    d = datetime.datetime.utcnow()
    return d.strftime(__format)


__oldTime = False
def echoLog(__str):
    global __oldTime, __logVerboseFile
    
    if __logVerboseFile != False:
        __logVerboseFileParsed = __logVerboseFile.replace('%DATE%', str(date('%Y-%m-%d')))
    
    if __logVerboseFile != False and not os.path.exists(__logVerboseFileParsed):
        f = open(__logVerboseFileParsed, 'w')
        f.write('<style type="text/css">html { white-space: pre; font-family: Courier New,Courier,Lucida Sans Typewriter,Lucida Typewriter,monospace; }</style>')
        f.close()

    if (__oldTime == False) or (__oldTime != date('%H:%M:%S')):
        __oldTime = date('%H:%M:%S')
        __str = str(__oldTime)  + ' | ' + str(__str)
    else:
        __str = '        '  + ' | ' + str(__str)
        
    print __str
    sys.stdout.flush()

    if __logVerboseFile != False:
        f = open(__logVerboseFileParsed, 'a')
        f.write(__str + '\n')
        f.close()
    

def echoLogJSON(__json):
    global __logJSONFile
    
    if __logJSONFile != False:
        __logJSONFileParsed = __logJSONFile.replace('%DATE%', str(date('%Y-%m-%d')))
        
        f = open(__logJSONFileParsed, 'a')
        f.write(str(__json) + '\n')
        f.close()
        

def main():
    echoLog('Starting EDDN Subscriber')
    echoLog('')
    
    context     = zmq.Context()
    subscriber  = context.socket(zmq.SUB)
    
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    subscriber.setsockopt(zmq.RCVTIMEO, __timeoutEDDN)

    while True:
        try:
            subscriber.connect(__relayEDDN)
            echoLog('Connect to ' + __relayEDDN)
            echoLog('')
            echoLog('')
            
            poller = zmq.Poller()
            poller.register(subscriber, zmq.POLLIN)
 
            while True:
                socks = dict(poller.poll(__timeoutEDDN))
                if socks:
                    if socks.get(subscriber) == zmq.POLLIN:
                        __message   = subscriber.recv(zmq.NOBLOCK)
                        __message   = zlib.decompress(__message)
                        __json      = simplejson.loads(__message)
                        __converted = False
                        
                        
                        # Handle commodity v1
                        if __json['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/1' + ('/test' if (__debugEDDN == True) else ''):
                            echoLogJSON(__message)
                            echoLog('Receiving commodity-v1 message...')
                            echoLog('    - Converting to v2...')
                            
                            __temp                              = {}
                            __temp['$schemaRef']                = 'http://schemas.elite-markets.net/eddn/commodity/2' + ('/test' if (__debugEDDN == True) else '')
                            __temp['header']                    = __json['header']
                            
                            __temp['message']                   = {}
                            __temp['message']['systemName']     = __json['message']['systemName']
                            __temp['message']['stationName']    = __json['message']['stationName']
                            __temp['message']['timestamp']      = __json['message']['timestamp']
                            
                            __temp['message']['commodities']    = []
                            
                            __commodity                         = {}
                            
                            if 'itemName' in __json['message']:
                                __commodity['name'] = __json['message']['itemName']
                            
                            if 'buyPrice' in __json['message']:
                                __commodity['buyPrice'] = __json['message']['buyPrice']
                            if 'stationStock' in __json['message']:
                                __commodity['supply'] = __json['message']['stationStock']
                            if 'supplyLevel' in __json['message']:
                                __commodity['supplyLevel'] = __json['message']['supplyLevel']
                            
                            if 'sellPrice' in __json['message']:
                                __commodity['sellPrice'] = __json['message']['sellPrice']
                            if 'demand' in __json['message']:
                                __commodity['demand'] = __json['message']['demand']
                            if'demandLevel' in __json['message']:
                                __commodity['demandLevel'] = __json['message']['demandLevel']
                            
                            __temp['message']['commodities'].append(__commodity)
                            __json                              = __temp
                            del __temp, __commodity
                            
                            __converted = True
                        
                        # Handle commodity v2
                        if __json['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/2' + ('/test' if (__debugEDDN == True) else ''):
                            if __converted == False:
                                echoLogJSON(__message)
                                echoLog('Receiving commodity-v2 message...')
                            
                            __authorised = False
                            __excluded   = False
                            
                            if __json['header']['softwareName'] in __authorisedSoftwares:
                                __authorised = True
                            if __json['header']['softwareName'] in __excludedSoftwares:
                                __excluded = True
                        
                            echoLog('    - Software: ' + __json['header']['softwareName'] + ' / ' + __json['header']['softwareVersion'])
                            echoLog('        - ' + 'AUTHORISED' if (__authorised == True) else
                                                        ('EXCLUDED' if (__excluded == True) else 'UNAUTHORISED')
                            )
                            
                            if __authorised == True and __excluded == False:
                                # Do what you want with the data...
                                # Have fun !
                                
                                # For example
                                echoLog('    - Timestamp: ' + __json['message']['timestamp'])
                                echoLog('    - Uploader ID: ' + __json['header']['uploaderID'])
                                echoLog('        - System Name: ' + __json['message']['systemName'])
                                echoLog('        - Station Name: ' + __json['message']['stationName'])
                                
                                for __commodity in __json['message']['commodities']:
                                    echoLog('            - Name: ' + __commodity['name'])
                                    echoLog('                - Buy Price: ' + str(__commodity['buyPrice']))
                                    echoLog('                - Supply: ' + str(__commodity['supply']) 
                                        + ((' (' + __commodity['supplyLevel'] + ')') if 'supplyLevel' in __commodity else '')
                                    )
                                    echoLog('                - Sell Price: ' + str(__commodity['sellPrice']))
                                    echoLog('                - Demand: ' + str(__commodity['demand'])
                                        + ((' (' + __commodity['demandLevel'] + ')') if 'demandLevel' in __commodity else '')
                                    )
                                # End example
                                
                            del __authorised, __excluded
                            
                            echoLog('')
                            echoLog('')
                        
                        del __converted
                else:
                    print 'Disconnect from ' + __relayEDDN + ' (After timeout)'
                    echoLog('')
                    echoLog('')
                    sys.stdout.flush()
                    
                    subscriber.disconnect(__relayEDDN)
                    break
                
        except zmq.ZMQError, e:
            subscriber.disconnect(__relayEDDN)
            
            echoLog('')
            echoLog('Disconnect from ' + __relayEDDN + ' (After receiving ZMQError)')
            echoLog('ZMQSocketException: ' + str(e))
            echoLog('')
            
            time.sleep(10)
            
        

if __name__ == '__main__':
    main()
