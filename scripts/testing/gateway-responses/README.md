# Gateway Testing Scripts

## Introduction
This directory contains some very "rough and ready" scripts, plus 
supporting files, that can be utilised to test that the EDDN Gateway code 
is properly responding in the face of a variety of bad messages.

Ultimately the plan is to use these as a basis for implementing some proper 
automated tests.

## Use
The scripts are mostly written against Python 3.x and expect a single 
filename to be passed on the commandline.  The exception is `test-bad-gzip.
sh` which is a Bourne Shell script, using `curl` to send a request that 
claims to be gzipped, but isn't valid.

They all have the beta EDDN Gateway URL hard-coded.  **NEVER** change this 
to run them against the live service!