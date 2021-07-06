<!-- vim: tabstop=2 softtabstop=2 shiftwidth=2 expandtab smartindent smarttab wrapmargin=0 textwidth=0
-->
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

---

# Further installation

## As 'root'

Some additional Debian packages and python modules are required:

    apt install python-pip virtualenv

You will need a mysql/mariab database:

    apt install mariadb-server
    mysqladmin create eddn
    # Generate a secure password somehow, e.g.
    dd if=/dev/urandom bs=512 count=1 | sha256sum
    mysql mysql # Connect to the database as root
    > CREATE USER IF NOT EXISTS 'eddn'@'localhost' IDENTIFIED BY ' SOME SECURE PASSWORD ';
    > GRANT ALL PRIVILEGES on eddn.* TO 'eddn'@'localhost';
    > \q

---

### Netdata
In order to get host performance metrics (CPU, RAM and network usage) you will
need to install netdata.  On Debian-based systems:

    apt install netdata

The default configuration should be all you need, listening on
`127.0.0.1:19999`.

---

### LetsEncrypt
We assume that you're using a TLS certificate from
[LetsEncrypt](https://letsencrypt.org/), it's free!

It will be necessary to renew the TLS certificate using certbot, or some
alternative ACME client.  We'll assume certbot.

#### Install certbot
On a Debian system simply:

    apt install certbot

Although this version might be a little old now, it does work.

#### LetsEncrypt TLS Certificates
If you are taking over hosting the EDDN relay then hopefully you have access
to the existing certificate files.

So, first copy those into place:

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

After this you need to ensure that the certificate stays renewed.  With a
Debian system using certbot:

1. There should already be a systemd timer set up:

    `systemctl status certbot.timer`

    If that doesn't show "`; enabled;`" in:
  
    `Loaded: loaded (/lib/systemd/system/certbot.timer; enabled; vendor preset: enabled)`

    then:

    `systemctl enable certbot.timer`

    This will renew the certificate as necessary (i.e. when <= 30 days until
    it expires, or whatever current LetsEncrypt and certbot policy causes).
    But it will not ensure the files are in all the places you might need
    them to be.

1. Ensure the certificate files are deployed to where they're needed.  When
  using the certbot timer the easiest thing to do is to utilise a script in
  `/etc/letsencrypt/renewal-hooks/deploy/`.

    There are example files for this in `contrib/letsencrypt/`:

        mkdir -p /etc/letsencrypt/renewal-hooks/deploy
        cp contrib/letsencrypt/deploy-changed-certs /etc/letsencrypt/renewal-hooks/deploy
        mkdir -p /etc/scripts
        cp contrib/letsencrypt/certbot-common /etc/scripts/

    **Remember to edit them to suit your setup!**

---

### Network Configuration
There are multiple ports that you'll have to ensure are allowed through any
firewall, and some of them also require being reverse proxied correctly.

The reverse proxies pertain to:

1. The port for the Gateway to receive uploads from senders (e.g. Elite
  Dangerous Market Connector).  This is also used for the 'monitor' web
  page to obtain stats about messages passing through the Gateway.

1. A set of URLs for accessing [netdata](#netdata).

#### Necessary ports
These all for TCP, no UDP:

1. `443` - a web server capable of reverse proxying set up for TLS on the
  public host name of the EDDN service.  This is used to serve the schemas,
  the monitor web page, and to reverse proxy URLs beginning `/netdata/` to
  the [netdata](#netdata) service.

1. Default: `4430` - Gateway 'http' port, used both for EDDN senders to
  upload, and also for the Gateway message rate stats on the monitor web
  page.

    But that's the *public* port.  The Gateway process itself listens on `8081`.
    So you'll need a reverse proxy listening on port `4430` and forwarding
    *all* requests to `127.0.0.1:8081`.

1. Default: `9091` - Monitor 'http' port, used for the monitor web page to
  query schema and software statistics. No reverse proxy setup.

1. Default: `9500` - The port on the Relay that EDDN listeners connect to in
  order to receive the zeromq stream.  No reverse proxy setup.

1. Default: `9090` - The Relay 'http' port for its portion of the message
  statistics on the monitor web page.  No reverse proxy setup.

There's also the internal `8500` port, but that's literally only used for
the Monitor and Relay to pick up zeromq messages forwarded from the
Gateway, so all over localhost.

See [Configuration](#configuration) for guidance on what override config
settings can be used to change any of these ports.

---

#### Reverse Proxy with Apache
If you already have an Apache installation it will be easier to just use
it for the reverse proxy.

Ensure you have these modules installed and active:

    a2enmod proxy proxy_http

##### Apache configuration
There is an example VirtualHost configuration in
`contrib/apache-eddn.conf` which makes the following assumptions:

  1. The usual Apache default configuration is in place elsewhere.
  1. The hostname being used - `ServerName`.
  1. The location of the monitor files - `DocumentRoot`.
  1. The location of the schema files - `Alias /schemas/ ...`.
  1. The location of the TLS certificate files - `SSLCertificateFile` and
   `SSLCertificateKeyFile.

You should be able to:

  1. Copy `contrib/apache-eddn.conf` into `/etc/apache/sites-available/`
   *as an appropriate filename for the hostname you're using*.
  1. Edit to suit the local situation/setup.  **Remember to ensure the
   configured log directory exists.**
  1. Enable the site:

         a2ensite <filename without trailing .conf>
         apache2ctl configtest
         # CHECK THE OUTPUT
         apache2ctl graceful

---

#### Reverse Proxy with nginx
If you don't yet have nginx installed then start with:

    apt install nginx-light

##### nginx configuration
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

If you're already using another web server you'll need to
duplicate at least the use of a TLS certificate and the Reverse Proxying as
required.

---

## In the 'eddn' account

### Clone a copy of the application project from gitub
We'll assume you're setting up a development environment so use `dev` in the
path and some other configuration.  The scripts currently support three
environments: `live`, `beta` and `dev`.

    mkdir -p ${HOME}/dev
    cd ${HOME}/dev
    git clone https://github.com/EDCD/EDDN.git EDDN.git
    cd EDDN.git

We'll assume this `${HOME}/dev/EDDN.git` path elsewhere in this document.

### Set up a python virtual environment
So as to not have any python package version requirements clash with
anything else it's best to use a Python virtual environment (venv).  You
will have installed the Debian package 'virtualenv' [above](#as-root) for
this purpose.

We'll put the venv in `${HOME}/dev/python2.7-venv` with the following
command:

    cd ${HOME}/dev
    virtualenv -p /usr/bin/python2.7 ${HOME}/dev/python2.7-venv

And for future ease of changing python versions:

    ln -s python2.7-venv python-venv

And now start using this venv:

    . python-venv/bin/activate

### Ensure necessary python modules are installed
Installing extra necessary python modules is simple:

    pip install -r requirements.txt

### Initialise Database Schema
You will need to get the database schema in place:

    mysql -p eddn < ${HOME}/eddn/dev/EDDN/schema.sql
    <the password you set in the "CREATE USER" statement above>

Ref: [As root](#as-root).

---

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

See also the [post-installation notes](#post-installation-steps) for some
caveats about running this other than on the actual eddn.edcd.io host.

---

# Configuration
Default application configuration is in the file `src/eddn/conf/Settings.py`.
Do **not** change anything in this file, see below about overriding using
another file.

1. You will need to obtain a TLS certificate from, e.g. LetsEncrypt.  The
   application will need access to this and its private key file.

       CERT_FILE = '/etc/letsencrypt/live/YOUROWN.eddn.edcd.io/fullchain.pem'
       KEY_FILE  = '/etc/letsencrypt/live/YOUROWN.eddn.edcd.io/privkey.pem'

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
       that these are full public URLs which are served by your web server.

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
        1. `password` - the secure password you set [above](#as-root) when
          installing and configuring mariadb/mysql.

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

---

# Running
You have some choices for how to run the application components:

## Running scripts from source
If you are just testing out code changes then you can choose to run
this application directly from the source using the script
`systemd/start-eddn-service`. You'll need to run it as, e.g.

    systemd/start-eddn-service dev gateway --from-source

When using `--from-source` you can also supply a `--background` argument to
put the process into the background with a `.pid` file written in the logs
directory.

Check the `systemd/eddn_<environment>_config` files for the location of
the logs directory.

## Running from installation
Otherwise you will want to  utilise the `setup.py` file to build and
install the application files.  You'll need to do some setup first as
there are necessary files *not* checked into git, because they're per
environment:

### Performing the installation
1. Change directory to the top level of the git clone.

1. Create a file `setup_env.py` with contents:

    ```
    EDDN_ENV="dev"
    ```

    Replace `dev` with the environment you're setting up for.

1. As we're using a python venv we can now just run:

    `python setup.py install`

    to install it all.  This will install a python egg into the python
    venv, and then also ensure that the monitor and schema files are in
    place, along with support scripts.

    There is an example systemd setup in `systemd` that assumes
    this local installation.

    There are also some SysV style init.d scripts in `contrib/init.d/` for
    running the components.  They will need the `DAEMON` lines tweaking for
    running from another location.

You should now have:

1. `~/.local/bin` - with some scripts and per-environment config files:

    1. `start-eddn-dev-service` - script that runs a specified EDDN service.
      This is intended to be used by the contrib systemd setup, but will
      work standalone as well.
    
    1. `eddn-logs-archive` - script that potentially archives and expires
      existing archival logs for the specified environment.

1. `~/.local/share/eddn/dev` - with the monitor and schema files, along
  with an example config override file if you didn't already have a
  `config.json` here.

### Post-installation steps
If you're not using the `live` environment then there are some edits you
need to make.

All of the `contrib/monitor` files have the hostname `eddn.edcd.io`
 hard-coded.  You will need to perform search and replace on the
 installed/live files to use a test host.  The files in question are:

    monitor/js/eddn.js
    monitor/schemas.html

Replace the string `eddn.edcd.io` with the hostname you're using.
You'll need to perform similar substitutions if you change the
configuration to use any different port numbers.

---

# Accessing the Monitor
There is an EDDN Status web page usually provided at, e.g.
https://eddn.edcd.io/.  This is enabled by the Monitor component through
the combination of the `contrib/monitor/` files and API endpoints provided
by the Monitor process itself.

You will need to configure a reverse proxy to actually enable access to this.
There is an example nginx configuration in `contrib/nginx-eddn.conf`.

The necessary files should be put in place by

The 'monitor' files are what form the status/statistics page at
https://eddn.edcd.io/, so they need to be installed somewhere in a
static manner accessible to nginx.

Although setup.py installs the files you might still need to ensure the
permissions are correct for your web server to access them.

    chmod -R og+rX ${HOME} ${HOME}/.local ${HOME}/.local/share ${HOME}/.local/share/eddn
    chmod -R og+rX ${HOME}/.local/share/eddn/schemas

---

# Testing all of this in a VM
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

