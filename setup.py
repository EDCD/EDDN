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
    install_requires=["argparse", "bottle", "enum34", "gevent", "jsonschema", "pyzmq", "strict_rfc3339", "simplejson", "mysql-connector-python"],
    entry_points={
        'console_scripts': [
            'eddn-gateway = eddn.Gateway:main',
            'eddn-relay = eddn.Relay:main',
            'eddn-monitor = eddn.Monitor:main',
            ],
        }
      )
