These instructions are based on getting the software up and running from
scratch on a Debian Buster (10.9, stable as of 2021-05-16) system.

In the end the installed packages were as per the files:

  - [debian-vm-dpkg-selections.txt](./debian-vm-dpkg-selections.txt)
  - [debian-vm-dpkg_-l.txt](./debian-vm-dpkg_-l.txt)

# Base Debian Install
A simple Debian install was performed in a VirtualBox VM to ensure no
confounding factors.  Only the bare minimum was installed, and then the
following packages also installed:

    apt install screen sudo git

A specific user was created:

    useradd -c 'EDDN Gateway' -m -s /bin/bash eddn

# Further installation

## As 'root'

Some additional Debian packages and python modules are required:

    apt install python-pip

You will need a mysql/mariab database:

    apt install mariadb-server
    mysqladmin create eddn
    # Generate a secure password somehow, e.g.
    dd if=/dev/urandom bs=512 count=1 | sha256sum
    mysql mysql # Connect to the database as root
    > CREATE USER IF NOT EXISTS 'eddn'@'localhost' IDENTIFIED BY ' SOME SECURE PASSWORD ';
    > GRANT ALL PRIVILEGES on eddn.* TO 'eddn'@'localhost';
    > \q

### Netdata
In order to get host performance metrics (CPU, RAM and network usage) you will
need to install netdata.  On Debian-based systems:

    apt install netdata

The default configuration should be all you need, listening on
`127.0.0.1:19999`.

### LetsEncrypt: certbot
It will be necessary to renew the TLS certificate using certbot (or some
alternative ACME client).

    apt install certbot

### Reverse Proxy with nginx
If you don't yet have nginx installed then start with:

    apt install nginx-light

#### LetsEncrypt TLS Certificates

You will need a LetsEncrupt/ACME client in order to keep the TLS certificate
renewed.

    cd /etc/letsencrypt
    mkdir -p archive/eddn.edcd.io
    mkdir -p live/eddn.edcd.io
    cd archive/eddn.edcd.io
    cp <source for all *.pem files> .
    chmod 644 *.pem
    chmod 600 privkey*.pem
    cd ../../live/eddn.edcd.io
    # NB: You need to check what the *newest* file is.  The `1` will be a
    # greater number if the certificate has ever been renewed.
    ln -s ../../archive/eddn.edcd.io/fullchain1.pem fullchain.pem
    ln -s ../../archive/eddn.edcd.io/privkey1.pem privkey.pem

#### nginx configuration
There is an example configuration in `contrib/nginx-eddn.conf` which makes
some assumptions:

  1. That it will listen on the standard HTTP and HTTPS ports.
  1. The hostname being used - `server_name` directives.
  1. The location of the monitor files - `root` directive.
  1. The location of the schema files - `location` directive.
  1. The location of the TLS certificate files - `ssl_certificate` and
     `ssl_certificate_key` directives.

You should be able to:

  1. Copy `contrib/nginx-eddn.conf` into `/etc/nginx/sites-available/eddn`.
  1. Edit to suit the local situation/setup.
  1. Enable the site:

         cd /etc/nginx/sites-enabled
         ln -s /etc/nginx/sites-available/eddn        
         systemctl restart nginx.service

If you're already using another web server, such as Apache, you'll need to
duplicate at least the use of a TLS certificate and the Reverse Proxying as
required.

For Apache you would reverse proxy using something like the following in an
appropriate `<VirtualHost>` section:

        <IfModule mod_proxy.c>
                SSLProxyEngine On
                SSLProxyVerify none
                ProxyPreserveHost On

                # Pass through 'gateway' upload URL to Debian VM
                ProxyPass "/upload/" "https://EDDNHOST:8081/upload/"
                # Pass through 'monitor' URLs to Debian VM
                ProxyPass "/" "https://EDDNHOST/"
        </IfModule>

## In the 'eddn' account

### Clone a copy of the application project from gitub

    mkdir -p ~/eddn/dev
    cd ~/eddn/dev
    git clone https://github.com/EDCD/EDDN.git

We'll assume this `~/eddn/dev/EDDN` path elsewhere in this document.

### Ensure necessary python modules are installed
Installing extra necessary python modules is simple:

    pip install -r requirements.txt

### Initialise Database Schema
You will need to get the database schema in place:

    mysql -p eddn < ~/eddn/dev/EDDN/schema.sql
    <the password you set in the "CREATE USER" statement above>

### Monitor and Schema files
The Monitor files are not currently installed anywhere by the `setup.py`
script, so you'll need to manually copy them into somewhere convenient,
e.g.:

    mkdir -p ${HOME}/.local/share/eddn
    cp -r ~/eddn/dev/EDDN/contrib/monitor ${HOME}/.local/share/eddn
    chmod -R og+rX ${HOME} ${HOME}/.local ${HOME}/.local/share ${HOME}/.local/share/eddn

You will need to ensure that the Monitor nginx setup can see the schema files
in order to serve them for use by the Gateway. So perform, e.g.:

    mkdir -p ${HOME}/.local/share/eddn
    cp -r ~/eddn/dev/EDDN/schemas ${HOME}/.local/share/eddn
    chmod -R og+rX ${HOME}/.local/share/eddn/schemas

# Concepts
There are three components to this application.

1. Gateway - this is where senders connect to upload messages.  It performs
   schema validation and then passes the messages on to both the Monitor and
   the Relay (they connect and perform zeromq subscription).  This requires
   port `4430` to make it past any firewall, NAT etc and to the Gateway process.
   However, the actual Gateway *process* listens on port `8081` and the reverse
   proxy setup forwards port `4430` traffic to this.

1. Monitor - this gathers statistics about the messages, such as the sending
   software name and version.  This requires port `9091` to make it past any
   firewall, NAT etc, and to the Monitor process.

1. Relay - this is where listeners connect in order to be sent messages that
   have passed the schema and duplicate checks.  This requires ports 9500
   and `9090` to make it past any firewall, NAT etc, and to the Relay process.

There also port `8500` which is used purely over localhost for the communication
from the Gateway to the Relay and Monitor.

As the code currently (2021-05-16) stands it MUST run on a standalone host
such that everything is served relative to the path root, not a path prefix.

Also all of the `contrib/monitor` files have `eddn.edcd.io` hard-coded.  You
will need to perform search and replace on the installed/live files to use a
test host.  The files in question are:

    monitor/js/eddn.js
    monitor/schemas.html

Replace the string `eddn.edcd.io` with the hostname you're using.

# Configuration
Default application configuration is in the file `src/eddn/conf/Settings.py`.
Do **not** change anything in this file, see below about overriding using
another file.

1. You will need to obtain a TLS certificate from, e.g. LetsEncrypt.  The
   application will need access to this and its private key file.

       CERT_FILE = '/etc/letsencrypt/live/eddn.edcd.io/fullchain.pem'
       KEY_FILE  = '/etc/letsencrypt/live/eddn.edcd.io/privkey.pem'

1. Network configuration
    1. `RELAY_HTTP_BIND_ADDRESS` and `RELAY_HTTP_PORT` define the IP and port
       on which the Relay listens for, e.g. `/stats/` requests.
    1. `RELAY_RECEIVER_BINDINGS` defines where the Relay connects in order to
       subscribe to messages from the Gateway.  Should match
       `GATEWAY_SENDER_BINDINGS`.
    1. `RELAY_SENDER_BINDINGS` defines the address the application listens on
       for connections from listeners such as eddb.io.
    1. `RELAY_DUPLICATE_MAX_MINUTES` how many minutes to keep messages hashes
       cached for so as to detect, and not Relay out, duplicate messages.  If
       you set this to the literal string `false` the duplication checks will be
       disabled.  This is **very handy** when testing the code.
    1. `GATEWAY_HTTP_BIND_ADDRESS` and `GATEWAY_HTTP_PORT` define where the
       Gateway listens to for incoming messages from senders.  Might be
       forwarded from nginx or other reverse proxy.
    1. `GATEWAY_SENDER_BINDINGS` is where the Gateway listens for connections
       from the Relay and Monitor in order to send them messages that passed
       schema checks.
    1. `GATEWAY_JSON_SCHEMAS` defines the schemas used for validation.  Note
       that these are full public URLs which are served by nginx (or whatever
       else you're using as the reverse proxy).
    1. `GATEWAY_OUTDATED_SCHEMAS` any past schemas that are no longer valid.
    1. `MONITOR_HTTP_BIND_ADDRESS` and `MONITOR_HTTP_PORT` define where the
       Monitor listens to for web connections, e.g. the statistics page.
    1. `MONITOR_RECEIVER_BINDINGS` defines where the Monitor connects in order
       to subscribe to messages from the Gateway.  Should match
       `GATEWAY_SENDER_BINDINGS`.
    1. `MONITOR_UA` appears to be unused.

1. Database Configuration
    1. `MONITOR_DB` - defines the necessary information for the application to
       connect to a mysql/mariadb database for storing stats.
        1. `database` - the name of the database
        1. `user` - the user to connect as
        1. `password` - the secure password you set above when installing and
           configuring mariadb/mysql.

    It is assumed that the database is on `localhost`.

To change anything from the defaults create an override config file, which
must be in valid JSON format (so no comments, no dangling commas etc).
You can then pass this file to the application scripts, e.g.:

    python Gateway.py --config some/other/configfile.json

You only need to define the settings that you need to change from defaults,
e.g. certificate files and database credentials, without worrying about the
basic setup.

There is an **example** of this in
[eddn-settings-overrides-EXAMPLE.json](./eddn-settings-overrides-EXAMPLE.json).
It sets:

  1. The TLS CERT and KEY files.
  1. The gateway to listen on `0.0.0.0` rather than localhost (necessary
    when testing in a VM).
  1. Configures the database connection and credentials.
  1. Turns off the relay duplicate check.

# Running
You have some choices for how to run the application components:

1. You can choose to run this application directly from the source using the
  provided script in `contrib/run-from-source.sh`.

1. Or you can utilise the `setup.py` file to build and install the application
  files.  By default this requires write permissions under `/usr/local`, but
  you can run:

       python setup.py install --user

   to install under `~/.local/` instead.

   There is an example systemd setup in `contrib/systemd` that assumes
   this local installation.

   If you install into `/usr/local/` then there are SysV style init.d scripts
   in `contrib/init.d/` for running the components.  They will need the
   `DAEMON` lines tweaking for running from another location.

1. For quick testing purposes you can run them as follows, assuming you
   installed into `~/.local/`, and have your override settings in
   `${HOME}/etc/eddn-settings-overrides.json`:

        ~/.local/bin/eddn-gateway --config ${HOME}/etc/eddn-settings-overrides.json >> ~/logs/eddn-gateway.log 2>&1 &
        ~/.local/bin/eddn-monitor --config ${HOME}/etc/eddn-settings-overrides.json >> ~/logs/eddn-monitor.log 2>&1 &
        ~/.local/bin/eddn-relay --config ${HOME}/etc/eddn-settings-overrides.json >> ~/logs/eddn-relay.log 2>&1 &
  
# Accessing the Monitor
There is an EDDN Status web page usually provided at, e.g.
https://eddn.edcd.io/.  This is enabled by the Monitor component through
the combination of the `contrib/monitor/` files and API endpoints provided
by the Monitor process itself.

You will need to configure a reverse proxy to actually enable access to this.
There is an example nginx configuration in `contrib/nginx-eddn.conf`.

## Testing all of this in a VM
In order to test all of this in a VM you might need to set up a double
proxying:

  Internet -> existing server -> VM -> nginx -> EDDN scripts

If using Apache on a Debian server then you need some ProxyPass directives:

        <IfModule mod_proxy.c>
                SSLProxyEngine On
                SSLProxyVerify none
                ProxyPreserveHost On

                # Pass through 'gateway' upload URL to Debian VM
                ProxyPass "/eddn/upload/" "https://VM_HOST:8081/upload/"
                # Pass through 'monitor' URLs to Debian VM
                ProxyPass "/eddn/" "https://VM_HOST/"
        </IfModule>

This assumes you don't have a dedicated virtual host in this case, hence the
"/eddn" prefix there.  Remove that if you are using a dedicated virtual host
on the 'existing server'.

You'll also need to redirect the Gateway and Relay ports using firewall rules.
With iptables:

        PUB_INT=<your public facing interface>
        PRIV_INT=<internal interface if testing on internal network>
        ANYWHERE="0.0.0.0/0"  # Not strictly necessary, but it's good to be explicit
        # The IP your host/VM can be reached on.
        YOUR_EDDN_IP=...
        # Port 4430 is for senders to the Gateway
        iptables -t nat -A PREROUTING -i ${PUB_INT} -p tcp -s ${ANYWHERE} --dport 4430 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A PREROUTING -i ${PRIV_INT} -p tcp -s ${ANYWHERE} --dport 4430 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A OUTPUT -p tcp -s ${ANYWHERE} --dport 4430 -j DNAT --to-destination ${YOUR_EDDN_IP}
        # Port 9500 is for listeners connecting to the Relay
        iptables -t nat -A PREROUTING -i ${PUB_INT} -p tcp -s ${ANYWHERE} --dport 9500 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A PREROUTING -i ${PRIV_INT} -p tcp -s ${ANYWHERE} --dport 9500 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A OUTPUT -p tcp -s ${ANYWHERE} --dport 9500 -j DNAT --to-destination ${YOUR_EDDN_IP}
        # Port 9090 is for the Relay web server, stats API
        iptables -t nat -A PREROUTING -i ${PUB_INT} -p tcp -s ${ANYWHERE} --dport 9090 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A PREROUTING -i ${PRIV_INT} -p tcp -s ${ANYWHERE} --dport 9090 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A OUTPUT -p tcp -s ${ANYWHERE} --dport 9090 -j DNAT --to-destination ${YOUR_EDDN_IP}
        # Port 9091 is for the Monitor web server, stats API
        iptables -t nat -A PREROUTING -i ${PUB_INT} -p tcp -s ${ANYWHERE} --dport 9091 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A PREROUTING -i ${PRIV_INT} -p tcp -s ${ANYWHERE} --dport 9091 -j DNAT --to-destination ${YOUR_EDDN_IP}
        iptables -t nat -A OUTPUT -p tcp -s ${ANYWHERE} --dport 9091 -j DNAT --to-destination ${YOUR_EDDN_IP}

