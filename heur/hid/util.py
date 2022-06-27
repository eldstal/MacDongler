import glob
import os

import status

# Returns a list, since HID devices are often composite
def find_hiddev(conf, dev, path):
  if dev["type"] != "hid": return None

  ret = []
  for f in glob.glob(f"{path}/functions/hid.*/dev"):
    try:
      # This file contains a major:minor device number pair
      devpair = open(f, "r").read().strip()

      # sysfs provides more info about that device
      uevents = open(f"/sys/dev/char/{devpair}/uevent", "r").read().split("\n")

      # One line will be DEVNAME=hidg0 or similar
      for l in uevents:
        if "DEVNAME=" in l:
          devname = l.split("=")[1]
          devnode = f"/dev/{devname}"
          if os.path.exists(devnode):
            ret.append(devnode)

    except Exception as e:
      status.debug(f"heur.hid: Failed to find device information from {f}. Probably won't find the HID device we're looking for. " + str(e))
      continue

  if len(ret) == 0:
    return None
  return ret
