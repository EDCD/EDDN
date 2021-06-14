from setuptools import setup, find_packages
import re
import glob


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


setup(
    name='eddn',
    version=verstr,
    description='Elite: Dangerous Data Network',
    author='EDCD (https://edcd.github.io/)',
    author_email='edcd@miggy.org',
    url='https://github.com/EDCD/EDDN',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
    data_files=[('eddn/schemas', glob.glob("schemas/*.json"))],
    long_description="""\
      The Elite: Dangerous Data Network allows E:D players to share data. Not affiliated with Frontier Developments.
      """,
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
