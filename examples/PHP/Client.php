<?php
/**
 *  Configuration
 */
$relayEDDN              = 'tcp://eddn-relay.elite-markets.net:9500';

// A sample list of authorised softwares
$authorisedSoftwares    = array(
    "EliteOCR",
    "RegulatedNoise",
    "Maddavo's Market Share"
);

// Used this to excludes yourself for example has you don't want to handle your own messages ^^
$excludedSoftwares      = array(
    'ED-TD.SPACE'
);

/**
 * START
 */
function echoLog($str)
{
    fwrite(STDOUT, $str . PHP_EOL);
    
    file_put_contents(
        dirname(__FILE__) . '/Log_EDDN_' . date('Y-m-d') . '.htm',
        $str . '<br />',
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
                
                if(array_key_exists('itemName', $temp['message']))
                    $commodity['name'] = $temp['message']['itemName'];
                    
                if(array_key_exists('buyPrice', $temp['message']))
                    $commodity['buyPrice'] = $temp['message']['buyPrice'];
                if(array_key_exists('stationStock', $temp['message']))
                    $commodity['supply'] = $temp['message']['stationStock'];
                if(array_key_exists('supplyLevel', $temp['message']))
                    $commodity['supplyLevel'] = $temp['message']['supplyLevel'];
                
                if(array_key_exists('sellPrice', $temp['message']))
                    $commodity['sellPrice'] = $temp['message']['sellPrice'];
                if(array_key_exists('demand', $temp['message']))
                    $commodity['demand'] = $temp['message']['demand'];
                if(array_key_exists('demandLevel', $temp['message']))
                    $commodity['demandLevel'] = $temp['message']['demandLevel'];
                
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