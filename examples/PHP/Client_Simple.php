<?php
/**
 *  Configuration
 */
$relayEDDN              = 'tcp://eddn.edcd.io:9500';
$timeoutEDDN            = 600000;



/**
 * START
 */
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
            $json       = $message;
            
            fwrite(STDOUT, $json . PHP_EOL);
        }
    }
    catch (ZMQSocketException $e)
    {
        fwrite(STDOUT, 'ZMQSocketException: ' . $e . PHP_EOL);
        sleep(10);
    }
}

// Exit correctly
exit(0);