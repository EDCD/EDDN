"""Setup for EDDN software."""
import glob
import os
import pathlib
import re
import shutil
import subprocess
import sys

from setuptools import find_packages, setup

# isort: off
import setup_env
# isort: on

VERSIONFILE = "src/eddn/conf/Version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)

except EnvironmentError:
    print(f"unable to find version in {VERSIONFILE}")
    raise RuntimeError(f"if {VERSIONFILE} exists, it is required to be well-formed")

# Read environment-specific settings


###########################################################################
# Enforce the git status being "branch "live" checked out, at its HEAD"
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
if setup_env.EDDN_ENV == "live":

    try:
        git_cmd = subprocess.Popen(
            "git symbolic-ref -q --short HEAD".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        out, err = git_cmd.communicate()

    except Exception as e:
        print(f"Couldn't run git command to check branch: {e}")

    else:
        branch = out.decode().rstrip("\n")
        # - For any other branch checked out at its HEAD this will be a
        #   different name.
        # - For any "detached HEAD" (i.e. specific commit ID, or tag) it
        #   will be empty.
        if branch != "live":
            print(f"EDDN_ENV is '{setup_env.EDDN_ENV}' (and CWD is '{cwd}'), but branch is '{branch}', aborting!")
            sys.exit(-1)

###########################################################################

# Location of start-eddn-service script and its config file
START_SCRIPT_BIN = pathlib.Path(f"{os.environ['HOME']}/.local/bin")
# Location of web files
SHARE_EDDN_FILES = pathlib.Path(f"{os.environ['HOME']}/.local/share/eddn/{setup_env.EDDN_ENV}")

setup(
    name="eddn",
    version=verstr,
    description="Elite: Dangerous Data Network",
    long_description="""\
      The Elite Dangerous Data Network allows ED players to share data. Not affiliated with Frontier Developments.
      """,
    author="EDCD (https://edcd.github.io/)",
    author_email="edcd@miggy.org",
    url="https://github.com/EDCD/EDDN",
    packages=find_packages("src", exclude=["*.tests"]),
    package_dir={"": "src"},
    # This includes them for the running code, but that doesn't help
    # serve them up for reference.
    data_files=[("eddn/schemas", glob.glob("schemas/*.json"))],
    # Yes, we pin versions.  With python2.7 the latest pyzmq will NOT
    # work, for instance.
    install_requires=[
        "argparse",
        "bottle",
        "enum34",
        "gevent",
        "jsonschema",
        "pyzmq",
        "simplejson",
        "mysql-connector-python",
    ],
    entry_points={
        "console_scripts": [
            "eddn-gateway = eddn.Gateway:main",
            "eddn-relay = eddn.Relay:main",
            "eddn-monitor = eddn.Monitor:main",
            "eddn-bouncer = eddn.Bouncer:main",
        ],
    },
)


def open_file_perms_recursive(dirname: pathlib.Path) -> None:
    """Open up file perms on the given directory and its contents."""
    print(f"open_file_perms_recursive: {dirname}")

    for name in dirname.glob("*"):
        print(f"open_file_perms_recursive: {name}")
        if name.is_dir():
            name.chmod(0o755)
            open_file_perms_recursive(name)

        else:
            name.chmod(0o644)


# Ensure the systemd-required start files are in place
print(
    """
******************************************************************************
Ensuring start script and its config file are in place...
"""
)
try:
    START_SCRIPT_BIN.mkdir(mode=0o700, parents=True, exist_ok=True)

except Exception as e:
    print(f"{START_SCRIPT_BIN} can't be created, aborting!!!\n{e!r}")
    exit(-1)

shutil.copy(f"systemd/eddn_{setup_env.EDDN_ENV}_config", START_SCRIPT_BIN / f"eddn_{setup_env.EDDN_ENV}_config")
# NB: We copy to a per-environment version so that, e.g.live use won't break
#     due to changes in the other environments.
shutil.copy("systemd/start-eddn-service", START_SCRIPT_BIN / f"start-eddn-{setup_env.EDDN_ENV}-service")

# Ensure the service log file archiving script is in place
print(
    """
******************************************************************************
Ensuring the service log file archiving script is in place
"""
)
shutil.copy("contrib/eddn-logs-archive", START_SCRIPT_BIN)

# Ensure the latest monitor files are in place
old_umask = os.umask(0o22)
print(
    f"""
******************************************************************************
Ensuring {SHARE_EDDN_FILES} exists...
"""
)
try:
    SHARE_EDDN_FILES.mkdir(mode=0o700, parents=True, exist_ok=True)

except Exception as e:
    print(f"{SHARE_EDDN_FILES} can't be created, aborting!!!\n{e!r}")
    exit(-1)

print(
    """
******************************************************************************
Ensuring latest monitor files are in place...
"""
)
# Copy the monitor (Web page) files
try:
    shutil.rmtree(SHARE_EDDN_FILES / "monitor")

except OSError:
    pass

shutil.copytree(
    "contrib/monitor",
    SHARE_EDDN_FILES / "monitor",
    copy_function=shutil.copyfile,  # type: ignore
)
# And a copy of the schemas too
print(
    """
******************************************************************************
Ensuring latest schema files are in place for web access...
"""
)
try:
    shutil.rmtree(SHARE_EDDN_FILES / "schemas")

except OSError:
    pass

shutil.copytree(
    "schemas",
    SHARE_EDDN_FILES / "schemas",
    copy_function=shutil.copyfile,  # type: ignore
)

print(
    """
******************************************************************************
Opening up permissions on monitor and schema files...
"""
)
os.chmod(SHARE_EDDN_FILES, 0o755)
open_file_perms_recursive(SHARE_EDDN_FILES)

# You still need to make an override config file
if not (SHARE_EDDN_FILES / "config.json").is_file():
    shutil.copy("docs/config-EXAMPLE.json", SHARE_EDDN_FILES)
    print(
        f"""
******************************************************************************
There was no config.json file in place, so docs/config-EXAMPLE.json was
copied into:

     {SHARE_EDDN_FILES}

Please review, edit and rename this file to "config.json" so that this
software will actually work.
See docs/Running-this-software.md for guidance.
******************************************************************************
"""
    )
os.umask(old_umask)
