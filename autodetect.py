import os
import status


def find_mount(fstype):
  mounts = open("/proc/mounts", "r").readlines()
  for l in mounts:
    fields = l.split()
    if fields[2] == fstype:
      return fields[1]
  return None


def detect_gadgetfs(conf):
  if conf.gadgetfs: return
  mountpoint = find_mount("gadgetfs")
  if mountpoint is None:
    status.error("Unable to detect a mounted gadgetfs. Try something like   mount -t gadgetfs -o user,group gadget /dev/gadget")
    return

  conf.gadgetfs = mountpoint

def detect_udc(conf):
  if conf.udc_controller: return

  if not os.path.isdir("/sys/class/udc"):
    status.error("Unable to autodetect UDC controller. No /sys/class/udc/ found.")
    return

  _,dirnames,_ = next(os.walk("/sys/class/udc/", followlinks=True))

  # Make sure any dummy devices are always at the end
  dirnames = sorted(dirnames, key=lambda x: 1 if "dummy" in x else 0)

  if len(dirnames) == 0:
    status.error("Unable to autodetect UDC controller. No controllers found.")
    return

  conf.udc_controller = dirnames[0]
  status.info(f"Auto-selected UDC controller {conf.udc_controller}")

  if "dummy" in conf.udc_controller:
    status.warn(f"This UDC controller appears to be a software dummy. This means you are targeting _this_ system.")



#
# Some command-line arguments default to auto-detection
# This is where that's done.
#
def detect_settings(conf):
  detect_gadgetfs(conf)

  detect_udc(conf)
  return
