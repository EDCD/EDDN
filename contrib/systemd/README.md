# systemd unit files for running EDDN services

## eddn.target
This is a systemd target specifying that each of the services be run.
Place it in `/etc/systemd/system`.

## eddn@.service
This is a systemd *template* service file, negating the need for a
separate file per service.

Place it in `/etc/systemd/system`.  Edit it for:

 1. `AssetPathExists` - The path to where `python setup.py install --user`
   installed the files: `eddn-gateway`, `eddn-monitor`, `eddn-relay`.
 1. `ExecStart` - The path to where the wrapper scripts (see below) are
   installed.  Probably the same path.
 1. The `User` and `Group` you need the services to run as.

## Wrapper scripts
Each service is started by a wrapper script:

 - start-eddn-gateway
 - start-eddn-monitor
 - start-eddn-relay

Each of these utilises the file `eddn_config` for some basic
configuration:

 - The config override file to be used.
 - The directory to redirect all output to.

Each script will start its service with output redirected to an
appropriate file in the configured log directory, e.g.:

    ./eddn-gateway --config "${CONFIG_OVERRIDE}" >> "${LOG_DIR}/eddn-gateway.log" 2>&1
