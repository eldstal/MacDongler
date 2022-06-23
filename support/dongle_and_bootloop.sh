#!/bin/bash
#
# Run MacDongler in a rebooting loop
# 1. Set up your command line below. Ensure that --resume and --single-step are present.
# 2. Ensure that the log file is cleared
# 3. Ensure that the resume file is cleared
# 4. Create the file /tmp/MCD_BOOTLOOP
# 4. Run this script as root in your autostart
#
# After testing each dongle, the machine will reboot.
# Once all dongles have been tested, the rebooting will cease.
#
# To stop the reboot loop early, ssh into the machine and remove the file /tmp/MCD_BOOTLOOP

RESUMEFILE=/tmp/macdongler.resume
LOGFILE=/tmp/macdongler.log


if [ ! -f /tmp/MCD_BOOTLOOP ]; then
  echo "MacDongler boot loop script. Emergency break pulled. Bailing out of boot loop."
  exit 0
fi

MACDONGLER_ROOT=$(cd "`dirname ${BASH_SRC}`"; cd ..; pwd)

${MACDONGLER_ROOT}/MacDongler --resume-file "${RESUMEFILE}" \
                              --status-file "${LOGFILE}" \
                              --delete-all-devices \
                              --resume --single-step \
                              --test-multiple-devices \
                              --test-duration 15 \
                              --heuristics net.rx serial.rx \
                              net serial

if [ $? -eq 10 ]; then
  echo "MacDongler terminated, return code shows there are tests remaining."
  echo "Rebooting."
  reboot
  exit 1
else
  echo "MacDongler finished testing. Removing emergency break to disable boot loop."
  rm /tmp/MCD_BOOTLOOP
fi
