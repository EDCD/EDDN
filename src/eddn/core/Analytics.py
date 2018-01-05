# coding: utf8
import requests

from hashlib import sha1
from random import randint

from traceback import print_exc
from eddn.conf.Settings import Settings

class Analytics(object):
    mobileProperty  = 'MO' + Settings.MONITOR_UA[2:]
    utmUrl          = 'http://www.google-analytics.com/__utm.gif'
    
    def hit(self, schema, uploaderId, uploaderIp):
        try:
            if(uploaderId):
                uploaderId      = str(int("0x%s" % sha1(uploaderId).hexdigest(), 0))[:10]
            else:
                uploaderId      = 'DUPLICATE'
            
            payload             = {}
            payload['utmwv']    = "5.2.2d",
            payload['utmn']     = str(randint(1, 9999999999)),
            payload['utmp']     = schema,
            payload['utmac']    = self.mobileProperty
            payload['utmcc']    = "__utma=%s;" % ".".join(["1", uploaderId, "1", "1", "1", "1"])
            payload['utmip']    = uploaderIp
            
            r = requests.get(self.utmUrl, params=payload)
        except:
            print_exc()

        return