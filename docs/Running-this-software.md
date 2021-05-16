These instructions are based on getting the software up and running from
scratch on a Debian Buster (10.9, stable as of 2021-05-16) system.

# Base Debian Install
A simple Debian install was performed in a VirtualBox VM to ensure no
confounding factors.  Only the bare minimum was installed, and then the
following packages also installed:

    apt install screen sudo git

    useradd -c 'EDDN Gateway' -m -s /bin/bash eddn

# Further installation

## As 'root'

Some additional Debian packages and python modules are required:

    apt install python-pip

## In the 'eddn' account

    mkdir -p ~/eddn/dev
    cd ~/eddn/dev
    git clone https://github.com/EDCD/EDDN.git
    pip install -r requirements.txt  # NB: Needs merging from ...

## Concepts
There are three components to this application.

1. Gateway - this is where senders connect to upload messages.  It performs
   schema validation and then passes the messages on to...

1. Monitor - this gathers statistics about the messages, such as the sending
   software name and version.

1. Relay - this is where listeners connect in order to be sent messages that
   have passed the schema and duplicate checks.

## Configuration
Application configuration is in the file `rc/eddn/conf/Settings.py`.

1. You will need to obtain a TLS certificate from, e.g. LetsEncrypt.  The
   application will need access to this and its private key file.

       CERT_FILE = '/etc/letsencrypt/live/eddn.edcd.io/fullchain.pem'
       KEY_FILE  = '/etc/letsencrypt/live/eddn.edcd.io/privkey.pem'

1. Network configuration
  1. `RELAY_HTTP_BIND_ADDRESS` and `RELAY_HTTP_PORT` define the IP and port on
     which the application listens for new messages from the Gateway.
  1. `RELAY_RECEIVER_BINDINGS` defines where the Relay connects in order to
     subscribe to messages from the Gateway.  Should match
     `GATEWAY_SENDER_BINDINGS`.
  1. `RELAY_SENDER_BINDINGS` defines the address the application listens on
     for connections from listeners such as eddb.io.
  1. `RELAY_DUPLICATE_MAX_MINUTES` how many minutes to keep messages hashes
     cached for so as to detect, and not Relay out, duplicate messages.
  1. `GATEWAY_HTTP_BIND_ADDRESS` and ``GATEWAY_HTTP_PORT` define where the
     Gateway listens to for incoming messages from senders.  Might be
     forwarded from nginx or other reverse proxy.
  1. `GATEWAY_SENDER_BINDINGS` is where the Gateway listens for connections
     from the Relay and Monitor in order to send them messages that passed
     schema checks.
  1. `GATEWAY_JSON_SCHEMAS` defines the schemas used for validation.  Note
     that these are full public URLs which are served by ...
  1. `GATEWAY_OUTDATED_SCHEMAS` any past schema that is no longer valid.
  1. `MONITOR_HTTP_BIND_ADDRESS` and `MONITOR_HTTP_PORT` define where the
     Monitor listens for web connections to, e.g. the statistics page.
  1. `MONITOR_RECEIVER_BINDINGS` defines where the Monitor connects in order to
     subscribe to messages from the Gateway.  Should match
     `GATEWAY_SENDER_BINDINGS`.
  1. `MONITOR_DB` - defines the necessary information for the application to
     connect to a mysql/mariadb database for storing stats.
  1. `MONITOR_UA` appears to be unused.
