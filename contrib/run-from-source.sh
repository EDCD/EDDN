#!/bin/bash
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab

BASEPATH="TOP LEVEL OF GIT CLONE"
LOGPATH="${BASEPATH}/logs"
PYTHON="python2.7"

cd "${BASEPATH}" || exit 1
mkdir -p ${LOGPATH} || exit 2
cd eddn/src/eddn || exit 4

for d in Relay Monitor Gateway ;
do
	echo "$d"
	if ps "$(cat ${LOGPATH}/${d}.pid)" >/dev/null 2>&1;
	then
		echo "$d: Already running as $(cat ${LOGPATH}/${d}.pid)"
		continue
	fi
	if [ -f "${BASEPATH}/etc/settings.json" ];
	then
		CONFIG="--config ${BASEPATH}/etc/settings.json"
	else
		echo "WARNING: No override settings found, you'll be using defaults"
		echo "WARNING: Did you forget to make ${BASEPATH}/etc/settings.json ?"
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

