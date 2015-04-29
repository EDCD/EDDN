<?php
/**
 *  Configuration
 */
$relayEDDN              = 'tcp://eddn-relay.elite-markets.net:9500';
$timeoutEDDN            = 600000;

// Set false to listen to production stream
$debugEDDN              = true;

// Set to false if you do not want verbose logging
$logVerboseFile         = dirname(__FILE__) . '/Logs_Verbose_EDDN_%DATE%.htm';
//$logVerboseFile         = false;

// Set to false if you do not want JSON logging
$logJSONFile            = dirname(__FILE__) . '/Logs_JSON_EDDN_%DATE%.log';
//$logJSONFile            = false;

// A sample list of authorised softwares
$authorisedSoftwares    = array(
    "EDCE",
    "ED-TD.SPACE",
    "EliteOCR",
    "Maddavo's Market Share",
    "RegulatedNoise",
    "RegulatedNoise__DJ"
);

// Used this to excludes yourself for example has you don't want to handle your own messages ^^
$excludedSoftwares      = array(
    'My Awesome Market Uploader'
);



/**
 * START
 */
$oldTime = false;
function echoLog($str)
{
    global $oldTime, $logVerboseFile;
    
    if($logVerboseFile !== false)
        $logVerboseFileParsed = str_replace('%DATE%', date('Y-m-d'), $logVerboseFile);
    
    if($logVerboseFile !== false && !file_exists($logVerboseFileParsed))
    {
        file_put_contents(
            $logVerboseFileParsed, 
            '<style type="text/css">html { white-space: pre; font-family: Courier New,Courier,Lucida Sans Typewriter,Lucida Typewriter,monospace; }</style>'
        );
    }
        
    if($oldTime != date('H:i:s') || $oldTime === false)
    {
        $oldTime = date('H:i:s');
        $str     = $oldTime . ' | ' . $str;
    }
    else
        $str = '        '  . ' | ' . $str;
    
    fwrite(STDOUT, $str . PHP_EOL);
    
    if($logVerboseFile !== false)
        file_put_contents(
            $logVerboseFileParsed,
            $str . PHP_EOL,
            FILE_APPEND
        );
}

function echoLogJSON($json)
{
    global $logJSONFile;
    
    if($logJSONFile !== false)
    {
        $logJSONFileParsed = str_replace('%DATE%', date('Y-m-d'), $logJSONFile);
        
        file_put_contents(
            $logJSONFileParsed,
            $json . PHP_EOL,
            FILE_APPEND
        );
    }
}

// UTC
date_default_timezone_set('UTC');

echoLog('Starting EDDN Subscriber');
echoLog('');

$context    = new ZMQContext();
$subscriber = $context->getSocket(ZMQ::SOCKET_SUB);

$subscriber->setSockOpt(ZMQ::SOCKOPT_SUBSCRIBE, "");
$subscriber->setSockOpt(ZMQ::SOCKOPT_RCVTIMEO, $timeoutEDDN);

while (true)
{
    try
    {
        $subscriber->connect($relayEDDN);
        
        while (true)
        {
            $message = $subscriber->recv();
            
            if ($message === false)
            {
                $subscriber->disconnect($relayEDDN);
                break;
            }
            
            $message    = zlib_decode($message);
            $json      = json_decode($message, true);
            $converted  = false;
            
            // Handle commodity v1
            if($json['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/1' . (($debugEDDN === true) ? '/test' : ''))
            {
                echoLogJSON($message);
                echoLog('Receiving commodity-v1 message...');
                echoLog('    - Converting to v2...');
                
                $temp                           = array();
                $temp['$schemaRef']             = 'http://schemas.elite-markets.net/eddn/commodity/2' . (($debugEDDN === true) ? '/test' : '');
                $temp['header']                 = $json['header'];
                
                $temp['message']                = array();
                $temp['message']['systemName']  = $json['message']['systemName'];
                $temp['message']['stationName'] = $json['message']['stationName'];
                $temp['message']['timestamp']   = $json['message']['timestamp'];
                
                $temp['message']['commodities'] = array();
                
                $commodity                      = array();
                
                if(array_key_exists('itemName', $json['message']))
                    $commodity['name'] = $json['message']['itemName'];
                    
                if(array_key_exists('buyPrice', $json['message']))
                    $commodity['buyPrice'] = $json['message']['buyPrice'];
                if(array_key_exists('stationStock', $json['message']))
                    $commodity['supply'] = $json['message']['stationStock'];
                if(array_key_exists('supplyLevel', $json['message']))
                    $commodity['supplyLevel'] = $json['message']['supplyLevel'];
                
                if(array_key_exists('sellPrice', $json['message']))
                    $commodity['sellPrice'] = $json['message']['sellPrice'];
                if(array_key_exists('demand', $json['message']))
                    $commodity['demand'] = $json['message']['demand'];
                if(array_key_exists('demandLevel', $json['message']))
                    $commodity['demandLevel'] = $json['message']['demandLevel'];
                
                $temp['message']['commodities'][]   = $commodity;
                $json                               = $temp;
                unset($temp, $commodity);
                
                $converted = true;
            }
            
            
            // Handle commodity v2
            if($json['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/2' . (($debugEDDN === true) ? '/test' : ''))
            {
                if($converted === false)
                {
                    echoLogJSON($message);
                    echoLog('Receiving commodity-v2 message...');
                }
                
                $authorised = false;
                $excluded   = false;
                
                if(in_array($json['header']['softwareName'], $authorisedSoftwares))
                    $authorised = true;
                if(in_array($json['header']['softwareName'], $excludedSoftwares))
                    $excluded = true;
                
                echoLog('    - Software: ' . $json['header']['softwareName'] . ' / ' . $json['header']['softwareVersion']);
                echoLog('        - ' . (($authorised === true) 
                                            ? 'AUTHORISED' 
                                            : (( $excluded === true) ? 'EXCLUDED' : 'UNAUTHORISED')
                                        ));
                
                if($authorised === true && $excluded === false)
                {
                    // Do what you want with the data...
                    // Have fun !
                    
                    // For example
                    echoLog('    - Timestamp: ' . $json['message']['timestamp']);
                    echoLog('    - Uploader ID: ' . $json['header']['uploaderID']);
                    echoLog('        - System Name: ' . $json['message']['systemName']);
                    echoLog('        - Station Name: ' . $json['message']['stationName']);
                    
                    foreach($json['message']['commodities'] AS $commodity)
                    {
                        echoLog('            - Name: ' . $commodity['name']);
                        echoLog('                - Buy Price: ' . $commodity['buyPrice']);
                        echoLog('                - Supply: ' . $commodity['supply']
                            . ((array_key_exists('supplyLevel', $commodity)) ? ' (' . $commodity['supplyLevel'] . ')' : '')
                        );
                        echoLog('                - Sell Price: ' . $commodity['sellPrice']);
                        echoLog('                - Demand: ' . $commodity['demand']
                            . ((array_key_exists('demandLevel', $commodity)) ? ' (' . $commodity['demandLevel'] . ')' : '')
                        );
                    }
                    // End example
                }
                
                unset($authorised, $excluded);
                
                echoLog('');
                echoLog('');
            }
            
            unset($converted);
        }
    }
    catch (ZMQSocketException $e)
    {
        echoLog('');
        echoLog('ZMQSocketException: ' . $e);
        echoLog('');
        sleep(10);
    }
}

// Exit correctly
exit(0);