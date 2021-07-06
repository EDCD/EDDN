#!/bin/bash -x

BASEPATH="${HOME}/dev"
LOGPATH="${BASEPATH}/logs"
PYTHON="python2.7"

cd "${BASEPATH}" || exit 1
mkdir -p ${LOGPATH} || exit 2
cd EDDN.git/src/eddn || exit 4

for d in Relay Monitor Gateway ;
do
	echo "$d"
	PID_FILE="${LOGPATH}/${d}.pid"
	if ps "$(cat ${PID_FILE})" >/dev/null 2>&1;
	then
		echo "$d: Already running as $(cat ${PID_FILE})"
		continue
	fi
	CONFIG_FILE="${HOME}/.local/share/eddn/dev/config.json"
	if [ -f "${CONFIG_FILE}" ];
	then
		CONFIG="--config ${CONFIG_FILE}"
	else
		echo "WARNING: No override settings found, you'll be using defaults"
		echo "WARNING: Did you forget to make ${CONFIG_FILE} ?"
		echo "         Continuing anyway..."
		CONFIG=""
	fi
	${PYTHON} -m eddn.${d} \
		${CONFIG} \
		> ${LOGPATH}/$d.log \
		2>&1 &
	echo $! > "${LOGPATH}/${d}.pid"
	#sleep 1
done

# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab
