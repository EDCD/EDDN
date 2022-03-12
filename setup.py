"""Setup for EDDN software."""
import glob
import os
import re
import shutil
import subprocess
import sys
from setuptools import setup, find_packages

import setup_env
from setuptools import find_packages, setup

VERSIONFILE = "src/eddn/conf/Version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)

except EnvironmentError:
    print(f'unable to find version in {VERSIONFILE}')
    raise RuntimeError(f'if {VERSIONFILE} exists, it is required to be well-formed')

# Read environment-specific settings


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
START_SCRIPT_BIN = f'{os.environ["HOME"]}/.local/bin'
# Location of web files
SHARE_EDDN_FILES = f'{os.environ["HOME"]}/.local/share/eddn/{setup_env.EDDN_ENV}'

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
    package_dir={'': 'src'},

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


def open_file_perms_recursive(dirname: str) -> None:
    """Open up file perms on the given directory and its contents."""
    print(f'open_file_perms_recursive: {dirname}')
    names = os.listdir(dirname)
    for name in names:
        n = f'{dirname}/{name}'
        print(f'open_file_perms_recursive: {n}')
        if (os.path.isdir(n)):
            os.chmod(n, 0o755)
            # Recurse
            open_file_perms_recursive(n)

        else:
            os.chmod(n, 0o644)


# Ensure the systemd-required start files are in place
print("""
******************************************************************************
Ensuring start script and its config file are in place...
""")
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
        print(f"{START_SCRIPT_BIN} can't be created, aborting!!!")
        exit(-1)

os.chdir(old_cwd)

shutil.copy(
    f'systemd/eddn_{setup_env.EDDN_ENV}_config',
    f'{START_SCRIPT_BIN}/eddn_{setup_env.EDDN_ENV}_config'
)
# NB: We copy to a per-environment version so that, e.g.live use won't break
#     due to changes in the other environments.
shutil.copy(
    'systemd/start-eddn-service',
    f'{START_SCRIPT_BIN}/start-eddn-{setup_env.EDDN_ENV}-service'
)

# Ensure the service log file archiving script is in place
print("""
******************************************************************************
Ensuring the service log file archiving script is in place
""")
shutil.copy(
    'contrib/eddn-logs-archive',
    START_SCRIPT_BIN
)

# Ensure the latest monitor files are in place
old_umask = os.umask(0o22)
print(f"""
******************************************************************************
Ensuring {SHARE_EDDN_FILES} exists...
""")
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
        print(f"{SHARE_EDDN_FILES} can't be created, aborting!!!")
        exit(-1)

os.chdir(old_cwd)
print("""
******************************************************************************
Ensuring latest monitor files are in place...
""")
# Copy the monitor (Web page) files
try:
    shutil.rmtree(f'{SHARE_EDDN_FILES}/monitor')
except OSError:
    pass
shutil.copytree(
    'contrib/monitor',
    f'{SHARE_EDDN_FILES}/monitor',
    # Not in Python 2.7
    # copy_function=shutil.copyfile,
)
# And a copy of the schemas too
print("""
******************************************************************************
Ensuring latest schema files are in place for web access...
""")
try:
    shutil.rmtree(f'{SHARE_EDDN_FILES}/schemas')

except OSError:
    pass

shutil.copytree(
    'schemas',
    f'{SHARE_EDDN_FILES}/schemas',
    # Not in Python 2.7
    # copy_function=shutil.copyfile,
)

print("""
******************************************************************************
Opening up permissions on monitor and schema files...
""")
os.chmod(SHARE_EDDN_FILES, 0o755)
open_file_perms_recursive(SHARE_EDDN_FILES)

# You still need to make an override config file
if not os.path.isfile(f'{SHARE_EDDN_FILES}/config.json'):
    shutil.copy('docs/config-EXAMPLE.json', SHARE_EDDN_FILES)
    print(f"""
******************************************************************************
There was no config.json file in place, so docs/config-EXAMPLE.json was
copied into:

     {SHARE_EDDN_FILES}

Please review, edit and rename this file to 'config.json' so that this
software will actually work.
See docs/Running-this-software.md for guidance.
******************************************************************************
""")
os.umask(old_umask)
