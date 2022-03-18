#!/bin/sh
#
# Run the EDDN Monitor from source

set -e

# Need to be in the src directory, relative to this script
cd "$(dirname $0)/src" 
# And we invoke the *module*, not the script by filename.
python -m eddn.Monitor $@
