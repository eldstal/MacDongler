#!/bin/bash
#
# Run MacDongler all the way through on each boot
# 1. Set up your command line below.
# 2. Ensure that the log file is cleared
# 3. Ensure that the resume file is cleared
# 4. Create the file /root/MCD_ONBOOT
# 5. Run this script as root in your autostart
# 6. Optionally, start a front-end on boot as well, and point it to the same status file
#
# Each time the machine powers up, a complete regiment of tests will be run against
# whichever host is connected.

RESUMEFILE=/root/macdongler.resume
LOGFILE=/root/macdongler.log
EMERGENCYFILE=/root/MCD_ONBOOT
MACDONGLER_ROOT=$(cd "`dirname ${BASH_SRC}`"; cd ..; pwd)

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
RESULT="/root/macdongler.${TIMESTAMP}.json5"


if [ ! -f ${EMERGENCYFILE} ]; then
  echo "MacDongler boot script. Emergency break pulled. Bailing out."
  exit 0
fi

${MACDONGLER_ROOT}/MacDongler \
                              --resume-file "${RESUMEFILE}" \
                              --resume \
                              --status-file "${LOGFILE}" \
                              --clobber-resume \
                              --delete-all-devices \
                              --test-duration 10 \
                              --setup-duration 2 \
                              --net-transmit-pcap ${MACDONGLER_ROOT}/pcaps/*.pcap \
                              --heuristics all \
                              --test-multiple-devices \
                              net serial

# After completing a run, remove the resume file so that next boot starts clean
rm "${RESUMEFILE}"
