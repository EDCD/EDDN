<?php
/**
 *  Configuration
 */
$relayEDDN              = 'tcp://eddn-relay.elite-markets.net:9500';
$logFile                = dirname(__FILE__) . '/Logs_EDDN_' . date('Y-m-d') . '.htm';

// A sample list of authorised softwares
$authorisedSoftwares    = array(
    "ED-TD.SPACE",
    "EliteOCR",
    "RegulatedNoise",
    "RegulatedNoise__DJ",
    "Maddavo's Market Share"
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
    global $oldTime, $logFile;
    
    if(!file_exists($logFile))
    {
        file_put_contents(
            $logFile, 
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
    
    file_put_contents(
        $logFile,
        $str . PHP_EOL,
        FILE_APPEND
    );
}

// UTC
date_default_timezone_set('UTC');

echoLog('Starting EDDN Subscribe');
echoLog('');

$context = new ZMQContext();
$socket = $context->getSocket(ZMQ::SOCKET_SUB);
$socket->setSockOpt(ZMQ::SOCKOPT_SUBSCRIBE, "");
$socket->setSockOpt(ZMQ::SOCKOPT_RCVTIMEO, 600000);

while (true)
{
    try
    {
        $socket->connect($relayEDDN);
        while (true)
        {
            $message = $socket->recv();
            
            if ($message === false)
            {
                $socket->disconnect($relayEDDN);
                break;
            }
            
            $json       = zlib_decode($message);
            $array      = json_decode($json, true);
            $converted  = false;
            
            
            // Handle commodity v1
            if($array['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/1')
            {
                echoLog('Receiving commodity-v1 message...');
                echoLog('    - Converting to v2...');
                
                $temp                           = array();
                $temp['$schemaRef']             = 'http://schemas.elite-markets.net/eddn/commodity/2';
                $temp['header']                 = $array['header'];
                
                $temp['message']                = array();
                $temp['message']['systemName']  = $array['message']['systemName'];
                $temp['message']['stationName'] = $array['message']['stationName'];
                $temp['message']['timestamp']   = $array['message']['timestamp'];
                
                $temp['message']['commodities'] = array();
                
                $commodity                      = array();
                
                if(array_key_exists('itemName', $array['message']))
                    $commodity['name'] = $array['message']['itemName'];
                    
                if(array_key_exists('buyPrice', $array['message']))
                    $commodity['buyPrice'] = $array['message']['buyPrice'];
                if(array_key_exists('stationStock', $array['message']))
                    $commodity['supply'] = $array['message']['stationStock'];
                if(array_key_exists('supplyLevel', $array['message']))
                    $commodity['supplyLevel'] = $array['message']['supplyLevel'];
                
                if(array_key_exists('sellPrice', $array['message']))
                    $commodity['sellPrice'] = $array['message']['sellPrice'];
                if(array_key_exists('demand', $array['message']))
                    $commodity['demand'] = $array['message']['demand'];
                if(array_key_exists('demandLevel', $array['message']))
                    $commodity['demandLevel'] = $array['message']['demandLevel'];
                
                $temp['message']['commodities'][]   = $commodity;
                $array                              = $temp;
                unset($temp, $commodity);
                
                $converted = true;
            }
            
            
            // Handle commodity v2
            if($array['$schemaRef'] == 'http://schemas.elite-markets.net/eddn/commodity/2')
            {
                if($converted === false)
                    echoLog('Receiving commodity-v2 message...');
                unset($converted);
                
                $authorised = false;
                $excluded   = false;
                
                if(in_array($array['header']['softwareName'], $authorisedSoftwares))
                    $authorised = true;
                if(in_array($array['header']['softwareName'], $excludedSoftwares))
                    $excluded = true;
                
                echoLog('    - Software: ' . $array['header']['softwareName'] . ' / ' . $array['header']['softwareVersion']);
                echoLog('        - ' . (($authorised === true) 
                                            ? 'AUTHORISED' 
                                            : (( $excluded === true) ? 'EXCLUDED' : 'UNAUTHORISED')
                                        ));
                
                if($authorised === true && $excluded === false)
                {
                    // Do what you want with the data...
                    // Have fun !
                    
                }
                
                unset($authorised, $excluded);
            }
            
            echoLog('');
            echoLog('');
        }
    }
    catch (ZMQSocketException $e)
    {
        echoLog('ZMQSocketException: ' . $e);
        sleep(10);
    }
}

// Exit correctly
exit(0);