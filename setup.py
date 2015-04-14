from setuptools import setup, find_packages
import re


VERSIONFILE = "src/eddn/_version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
except EnvironmentError:
    print "unable to find version in %s" % (VERSIONFILE,)
    raise RuntimeError("if %s exists, it is required to be well-formed" % (VERSIONFILE,))


setup(
    name='eddn',
    version=verstr,
    description='Elite: Dangerous Data Network',
    author='James Muscat',
    author_email='muscaat@elite-markets.net',
    url='https://github.com/jamesremuscat/eddn',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
    long_description="""\
      The Elite: Dangerous Data Network allows E:D players to share data. Not affiliated with Frontier Developments.
      """,
    install_requires=["bottle", "enum34", "gevent", "jsonschema", "pyzmq", "simplejson"],
    entry_points={
        'console_scripts': [
            'eddn-gateway = eddn.Gateway:main',
            'eddn-relay = eddn.Relay:main',
            ],
        }
      )
