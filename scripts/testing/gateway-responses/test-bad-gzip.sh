#!/bin/sh
#
# python `requests` appears to perform compression when you set the
# 'Content-Encoding: gzip' header, so do this with curl.

curl --verbose -d 'wegiuweuygtfawgep9aqe8fpq2387lfbr;iufvypq38764tpgf' -H 'Content-Encoding: gzip' 'https://dev.eddn.edcd.io:4432/upload/'
