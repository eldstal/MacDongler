
import os
import subprocess


def find_cmd(name):
  try:
    path = subprocess.check_output(f"which {name}", shell=True)
  except:
    return False
  if not os.path.exists(path): return None
  if not os.access(path, os.X_OK): return None
  return path




def sanity_options(conf):
  modes = [ conf.create_device, conf.delete_device, conf.list_devices, conf.sanity ]
  if sum(modes) > 1:
    return False, "More than one operation specified. Only one of --create-device, --delete-device, --list-devices, --sanity supported."

  if sum(modes) == 0:
    return False, "No operation specified. See --help for more information."

  return True, ""

def sanity_commands(conf):
  if conf.transmit_pcap:
    if not find_cmd("tcpreplay"):
      return False, "Could not find 'tcpreplay', but --transmit-pcap is specified."
  return True,""

def sanity_udc(conf):
  if not os.path.isdir("/sys/class/udc"):
    return False, ("No /sys/class/udc/ found. Ensure your UDC driver is loaded. "+
                  " If this system has no UDC controller in hardware, load the 'dummy_hdc' kernel module.")

  _,dirnames,_ = next(os.walk("/sys/class/udc/", followlinks=True))
  if not conf.udc_controller:
    return False, "No --udc-controller specified. This system supports the following: " + str(dirnames)
  if conf.udc_controller not in dirnames:
    return False, "Unknown --udc-controller specified. This system supports the following: " + str(dirnames)
  return True,""


def passes_sanity_checks(conf):

  for func in [ sanity_options,
                sanity_commands,
                sanity_udc,
              ]:
    ok, msg = func(conf)
    if not ok: return False, msg

  return True, "All checks passed"
