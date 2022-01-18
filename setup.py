import glob
import os
import re
import shutil
import subprocess
import sys
from setuptools import setup, find_packages

VERSIONFILE = "src/eddn/conf/Version.py"
verstr      = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE       = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo         = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
except EnvironmentError:
    print "unable to find version in %s" % (VERSIONFILE,)
    raise RuntimeError("if %s exists, it is required to be well-formed" % (VERSIONFILE,))

# Read environment-specific settings
import setup_env


###########################################################################
# Enforce the git status being "branch 'live' checked out, at its HEAD"
# if setup_env.py says this is the live environment.
#
# The idea is to have the `live` branch, *which includes documentation*
# always match what is actually running as the live service (modulo the
# small window between pull/install/restart).  Thus it shouldn't use
# `master`, or any other branch than `live`, which may have changes merged
# some time before they become live.
###########################################################################
cwd = os.getcwd()
# e.g. /home/eddn/live/EDDN.git
if setup_env.EDDN_ENV == 'live':

    try:
        git_cmd = subprocess.Popen(
            'git symbolic-ref -q --short HEAD'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        out, err = git_cmd.communicate()

    except Exception as e:
        print("Couldn't run git command to check branch: %s" % (e))

    else:
        branch = out.decode().rstrip('\n')
        # - For any other branch checked out at its HEAD this will be a
        #   different name.
        # - For any 'detached HEAD' (i.e. specific commit ID, or tag) it
        #   will be empty.
        if branch != 'live':
            print("EDDN_ENV is '%s' (and CWD is %s), but branch is '%s', aborting!" % (setup_env.EDDN_ENV, cwd, branch))
            sys.exit(-1)

###########################################################################

# Location of start-eddn-service script and its config file
START_SCRIPT_BIN='%s/.local/bin' % ( os.environ['HOME'] )
# Location of web files
SHARE_EDDN_FILES='%s/.local/share/eddn/%s' % ( os.environ['HOME'], setup_env.EDDN_ENV )

setup(
    name='eddn',
    version=verstr,
    description='Elite: Dangerous Data Network',
    long_description="""\
      The Elite Dangerous Data Network allows ED players to share data. Not affiliated with Frontier Developments.
      """,
    author='EDCD (https://edcd.github.io/)',
    author_email='edcd@miggy.org',
    url='https://github.com/EDCD/EDDN',

    packages=find_packages(
        'src',
         exclude=["*.tests"]
    ),
    package_dir = {'':'src'},

    # This includes them for the running code, but that doesn't help
    # serve them up for reference.
    data_files=[
        (
            'eddn/schemas', glob.glob("schemas/*.json")
        )
    ],

    # Yes, we pin versions.  With python2.7 the latest pyzmq will NOT
    # work, for instance.
    install_requires=[
        "argparse",
        "bottle==0.12.15",
        "enum34==1.1.6",
        "gevent==1.3.7",
        "jsonschema==2.6.0",
        "pyzmq==17.1.2",
        "strict_rfc3339==0.7",
        "simplejson==3.16.0",
        "mysql-connector-python==8.0.17"
    ],

    entry_points={
        'console_scripts': [
            'eddn-gateway = eddn.Gateway:main',
            'eddn-relay = eddn.Relay:main',
            'eddn-monitor = eddn.Monitor:main',
            'eddn-bouncer = eddn.Bouncer:main',
        ],
    }
)

def open_file_perms_recursive(dirname):
    """Open up file perms on the given directory and its contents."""
    print 'open_file_perms_recursive: %s' % ( dirname )
    names = os.listdir(dirname)
    for name in names:
        n = '%s/%s' % ( dirname, name )
        print 'open_file_perms_recursive: %s' % ( n )
        if (os.path.isdir(n)):
            os.chmod(n, 0755)
            # Recurse
            open_file_perms_recursive(n)
         
        else:
            os.chmod(n, 0644)

# Ensure the systemd-required start files are in place
print """
******************************************************************************
Ensuring start script and its config file are in place...
"""
old_cwd = os.getcwd()
if not os.path.isdir(START_SCRIPT_BIN):
    # We're still using Python 2.7, so no pathlib
    os.chdir('/')
    for pc in START_SCRIPT_BIN[1:].split('/'):
        try:
            os.mkdir(pc)

        except OSError:
            pass

        os.chdir(pc)

    if not os.path.isdir(START_SCRIPT_BIN):
        print "%s can't be created, aborting!!!" % (START_SCRIPT_BIN)
        exit(-1)

os.chdir(old_cwd)

shutil.copy(
    'systemd/eddn_%s_config' % ( setup_env.EDDN_ENV),
    '%s/eddn_%s_config' % ( START_SCRIPT_BIN, setup_env.EDDN_ENV )
)
# NB: We copy to a per-environment version so that, e.g.live use won't break
#     due to changes in the other environments.
shutil.copy(
    'systemd/start-eddn-service',
    '%s/start-eddn-%s-service' % ( START_SCRIPT_BIN, setup_env.EDDN_ENV )
)

# Ensure the latest monitor files are in place
old_umask = os.umask(022)
print """
******************************************************************************
Ensuring %s exists...
""" % ( SHARE_EDDN_FILES )
old_cwd = os.getcwd()
if not os.path.isdir(SHARE_EDDN_FILES):
    # We're still using Python 2.7, so no pathlib
    os.chdir('/')
    for pc in SHARE_EDDN_FILES[1:].split('/'):
        try:
            os.mkdir(pc)

        except OSError:
            pass

        os.chdir(pc)

    if not os.path.isdir(SHARE_EDDN_FILES):
        print "%s can't be created, aborting!!!" % (SHARE_EDDN_FILES)
        exit(-1)

os.chdir(old_cwd)
print """
******************************************************************************
Ensuring latest monitor files are in place...
"""
# Copy the monitor (Web page) files
try:
    shutil.rmtree('%s/monitor' % ( SHARE_EDDN_FILES ))
except OSError:
    pass
shutil.copytree(
    'contrib/monitor',
    '%s/monitor' % ( SHARE_EDDN_FILES ),
    # Not in Python 2.7
    # copy_function=shutil.copyfile,
)
# And a copy of the schemas too
print """
******************************************************************************
Ensuring latest schema files are in place for web access...
"""
try:
    shutil.rmtree('%s/schemas' % ( SHARE_EDDN_FILES ))
except OSError:
    pass
shutil.copytree(
    'schemas',
    '%s/schemas' % ( SHARE_EDDN_FILES ),
    # Not in Python 2.7
    # copy_function=shutil.copyfile,
)

print """
******************************************************************************
Opening up permissions on monitor and schema files...
"""
os.chmod(SHARE_EDDN_FILES, 0755)
open_file_perms_recursive(SHARE_EDDN_FILES)

# You still need to make an override config file
if not os.path.isfile('%s/config.json' % ( SHARE_EDDN_FILES )):
    shutil.copy('docs/config-EXAMPLE.json', SHARE_EDDN_FILES)
    print """
******************************************************************************
There was no config.json file in place, so docs/config-EXAMPLE.json was
copied into:

     %s
     
Please review, edit and rename this file to 'config.json' so that this
software will actually work.
See docs/Running-this-software.md for guidance.
******************************************************************************
""" % ( SHARE_EDDN_FILES )
os.umask(old_umask)
