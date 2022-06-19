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

def detect_configfs(conf):
  if conf.configfs: return
  mountpoint = find_mount("configfs")
  if mountpoint is None:
    status.error("Unable to detect a mounted configfs. Try something like   mount -t configfs -o noexec,nodev,nosuid,relatime none /sys/kernel/config")
    return

  conf.configfs = mountpoint

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

def detect_devices(conf):
  if conf.device_db: return

  default_dir = os.path.dirname(__file__)
  default_dir = os.path.join(default_dir, "devices")

  if not os.path.isdir(default_dir):
    status.error("Unable to auto-select device database dir. Make sure devices/ is in the script's directory, or pass --device-db.")
    return

  conf.device_db = default_dir


#
# Some command-line arguments default to auto-detection
# This is where that's done.
#
def detect_settings(conf):
  detect_gadgetfs(conf)
  detect_configfs(conf)
  detect_udc(conf)
  detect_devices(conf)
  return
