<?php
/**
 *
 * $eddn = new EDDN(array(
 *     'uploaderID'        => 'abcdef0123456789',
 *     'softwareName'      => 'My Awesome Market Uploader',
 *     'softwareVersion'   => 'v3.14'
 * )); *
 *
 * $result = $eddn->publishCommodityV3(
 *     'Eranin',
 *     'Azeban Orbital',
 *     time(),
 *     array(
 *         array(
 *             "name"          => "Gold",
 *             "buyPrice"      => 1024,
 *             "supply"        => 7,
 *             "supplyLevel"   => "Low",
 *             "sellPrice"     => 1138,
 *             "demand"        => 42,
 *             "demandLevel"   => "Med"
 *         ),
 *         array(
 *             "name"          => "Explosives",
 *             "buyPrice"      => 999,
 *             "supply"        => 1500,
 *             "supplyLevel"   => "Low",
 *             "sellPrice"     => 0,
 *             "demand"        => 0
 *         )
 *     )
 * ); // return true;
 *
 **/

class EDDN
{
    private static $_debug    = true;

    private static $_gateways = array(
        'https://eddn.edcd.io:8080/upload/',
    );

    private static $_schemas   = array(
        'commodity-v3' => array(
            'production'    => 'https://eddn.edcd.io/schemas/commodity/3',
            'test'          => 'https://eddn.edcd.io/schemas/commodity/3/test',
        ),
    );

    private $_uploaderID      = null;
    private $_softwareName    = null;
    private $_softwareVersion = null;

    public function __Construct(array $options)
    {
        if(array_key_exists('uploaderID', $options))
            $this->setUploaderID($options['uploaderID']);
        else
            throw new Exception('Option "uploaderID" is required.');

        if(array_key_exists('softwareName', $options))
            $this->setSoftwareName($options['softwareName']);
        else
            throw new Exception('Option "softwareName" is required.');

        if(array_key_exists('softwareVersion', $options))
            $this->setSoftwareVersion($options['softwareVersion']);
        else
            throw new Exception('Option "softwareVersion" is required.');
    }

    public function publishCommodityV3($systemName, $stationName, $timestamp, array $commodities)
    {
        $schema                 = self::$_schemas['commodity-v3'][((self::$_debug === true) ? 'test' : 'production')];

        $message                = array();
        $message['systemName']  = $systemName;
        $message['stationName'] = $stationName;
        $message['timestamp']   = date('c', $timestamp);

        $message['commodities'] = $commodities;

        return $this->_postToEDDN($schema, $message);
    }


    private function _generateHeader()
    {
        $header = array();

        $header['uploaderID']       = $this->getUploaderID();
        $header['softwareName']     = $this->getSoftwareName();
        $header['softwareVersion']  = $this->getSoftwareVersion();

        return $header;
    }

    private function _postToEDDN($schema, array $message)
    {
        $array                  = array();
        $array['$schemaRef']    = $schema;
        $array['header']        = $this->_generateHeader();
        $array['message']       = $message;

        $json                   = json_encode($array);

        if(function_exists('curl_version'))
        {
            $gateway = self::$_gateways[array_rand(self::$_gateways)];

            $ch = curl_init();

            curl_setopt($ch, CURLOPT_URL, $gateway);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $json);
            curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));

            $result = curl_exec($ch);
            curl_close($ch);
            unset($ch);

            if($result == 'OK')
                return true;
            else
                return $result;
        }
        else
            throw new Exception('You must have CURL extension in order to publish to EDDN');
    }


    public function setUploaderID($value)
    {
        $this->_uploaderID = $value;
    }

    public function getUploaderID()
    {
        return $this->_uploaderID;
    }


    public function setSoftwareName($value)
    {
        $this->_softwareName = $value;
    }

    public function getSoftwareName()
    {
        return $this->_softwareName;
    }


    public function setSoftwareVersion($value)
    {
        $this->_softwareVersion = $value;
    }

    public function getSoftwareVersion()
    {
        return $this->_softwareVersion;
    }


    public function setDebug($value)
    {
        self::$_debug = $value;
    }

    public function getDebug()
    {
        return self::$_debug;
    }
}