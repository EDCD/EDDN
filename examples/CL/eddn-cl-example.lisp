;; This code has been tested on Ubuntu 18.04 and SBCL 1.4.5 with the
;; following packages installed: sbcl, cl-quicklisp, libzmq3-dev.
;; Install and configure Quicklisp, https://www.quicklisp.org/, prior
;; to running this.  For more information, refer to the PZMQ
;; documentation at http://orivej.github.io/pzmq/doc/index.html.

(mapc #'ql:quickload '("pzmq" "zlib" "cl-json"))

(defpackage #:eddn-cl-example
  (:use #:cl)
  (:export
   #:simple-client))

(in-package #:eddn-cl-example)

(defun simple-client ()
  "Subscribe to EDDN and return one message."
  (pzmq:with-socket s :sub                     ;create a 0MQ subscriber socket
    (pzmq:connect s "tcp://eddn.edcd.io:9500") ;connect to EDDN
    (pzmq:with-message msg                     ;allocate a 0MQ message
      (pzmq:msg-recv msg s)                    ;receive EDDN compressed data
      (json:decode-json-from-string            ;parse the uncompressed JSON
       (babel:octets-to-string                 ;convert uncompressed data to a string
        (zlib:uncompress                       ;decompress the 0MQ message
         (cffi:foreign-array-to-lisp           ;convert 0MQ message from C to Lisp byte array
          (pzmq:msg-data msg)
          `(:array :uchar ,(pzmq:msg-size msg))
          :element-type '(unsigned-byte 8))))))))

;; When run, it will output something like the following:
;;
;; CL-USER> (eddn-cl-example:simple-client)
;; ((:$SCHEMA-REF . "https://eddn.edcd.io/schemas/journal/1")
;;  (:HEADER (:GATEWAY-TIMESTAMP . "2020-01-11T17:05:17.915018Z")
;;   (:SOFTWARE-NAME . "E:D Market Connector [Windows]")
;;   (:SOFTWARE-VERSION . "3.4.3.0")
;;   (:UPLOADER-+ID+ . "8c07651144ad55f78ed79381e3274c718674abf1"))
;;  (:MESSAGE (:*BODY . "Elata") (:*BODY-+ID+ . 0) (:*BODY-TYPE . "Star")
;;   (:*FACTIONS
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Corporate") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.407) (:*NAME . "Elata Crimson Natural Industries"))
;;    ((:*ALLEGIANCE . "PilotsFederation") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Democracy") (:*HAPPINESS . "") (:*INFLUENCE . 0.0)
;;     (:*NAME . "Pilots' Federation Local Branch"))
;;    ((:*ALLEGIANCE . "Federation") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Democracy") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.208) (:*NAME . "Deuriara Progressive Party"))
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "PrisonColony") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.088) (:*NAME . "Kondriates Prison Colony"))
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Democracy") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.123) (:*NAME . "Revolutionary Elata Progressive Party"))
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Dictatorship") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.068) (:*NAME . "Elata Regulatory State"))
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Anarchy") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.044) (:*NAME . "Elata Gold Camorra"))
;;    ((:*ALLEGIANCE . "Independent") (:*FACTION-STATE . "None")
;;     (:*GOVERNMENT . "Communism") (:*HAPPINESS . "$Faction_HappinessBand2;")
;;     (:*INFLUENCE . 0.062) (:*NAME . "Elata Revolutionary Party")))
;;   (:*POPULATION . 6846425) (:*STAR-POS -82.875 93.09375 -89.15625)
;;   (:*STAR-SYSTEM . "Elata") (:*SYSTEM-ADDRESS . 3102837066083)
;;   (:*SYSTEM-ALLEGIANCE . "Independent")
;;   (:*SYSTEM-ECONOMY . "$economy_Terraforming;")
;;   (:*SYSTEM-FACTION (:*NAME . "Elata Crimson Natural Industries"))
;;   (:*SYSTEM-GOVERNMENT . "$government_Corporate;")
;;   (:*SYSTEM-SECOND-ECONOMY . "$economy_Industrial;")
;;   (:*SYSTEM-SECURITY . "$SYSTEM_SECURITY_medium;") (:EVENT . "FSDJump")
;;   (:TIMESTAMP . "2020-01-11T17:05:17Z")))
