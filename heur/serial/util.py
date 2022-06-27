#
# Code shared between the serial heuristic modules
#

import glob
import os

import status

def find_tty(conf, dev, path):

  devnode = None

  if conf.serial_device is not None:
    devnode = conf.serial_device
    if not os.path.exists(devnode):
      status.warn(f"Configured gadget serial device {devnode} does not exist.")
      return None

  # There appears to be no perfectly reliable mapping between our
  # USB gadget and the device-side serial device.
  # The serial device is always (?) /dev/ttyGS*

  devs = glob.glob("/dev/ttyGS*")

  if len(devs) == 0:
    status.warn(f"No suitable serial device found for {dev['name']}. Device spec faulty? Try increasing --setup-duration.")
    return None

  if len(devs) > 1:
    status.warn(f"Auto-selecting from {len(devs)} serial devices. There may be additional USB gadgets interfering. Trying our best.")

  # The latest added one is probably it. Probably.
  return devs[-1]
