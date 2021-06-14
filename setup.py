import glob
import os
import re
import shutil
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

# Location of start-eddn-service script and its config file
START_SCRIPT_BIN='%s/.local/bin' % ( os.environ['HOME'] )
# Location of web files
SHARE_EDDN_FILES='%s/.local/share/eddn' % ( os.environ['HOME'] )

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
        ],
    }
)

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
for f in ( 'contrib/systemd/start-eddn-service', 'contrib/systemd/eddn_config'):
    shutil.copy(f, START_SCRIPT_BIN)

# Ensure the latest monitor files are in place
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
shutil.copytree('contrib/monitor', '%s/monitor' % ( SHARE_EDDN_FILES ))
# And a copy of the schemas too
print """
******************************************************************************
Ensuring latest schema files are in place for web access...
"""
try:
    shutil.rmtree('%s/schemas' % ( SHARE_EDDN_FILES ))
except OSError:
    pass
shutil.copytree('schemas', '%s/schemas' % ( SHARE_EDDN_FILES ))

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
