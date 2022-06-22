
import os
import subprocess

import devicespec


def find_cmd(name):
  try:
    path = subprocess.check_output(f"which {name}", shell=True)
  except:
    return False
  if not os.path.exists(path): return None
  if not os.access(path, os.X_OK): return None
  return path




def sanity_options(conf):
  # --delete-devices can be specified together with another mode, if we so desire
  exclusive_modes = [ conf.test_multiple_devices,
                      conf.create_device,
                      conf.list_supported_devices,
                      conf.list_heuristics,
                      conf.sanity ]
  modes = [ conf.delete_devices ] + exclusive_modes
  if sum(exclusive_modes) > 1:
    return False, "More than one operation specified. Only one of --scan-devices, --create-device, --list-supported-devices, --list-heuristics, --sanity supported."

  if sum(modes) == 0:
    return False, "No operation specified. See --help for more information."

  return True, ""

def sanity_commands(conf):
  if conf.net_transmit_pcap:
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


def sanity_configfs(conf):
  if not conf.configfs:
    return False, (f"No configfs configured. Ensure that a configfs is mounted or specify its location with --configfs")

  if not os.path.isdir(conf.configfs):
    return False, (f"No configfs found at {conf.configfs}. Ensure that a configfs is mounted.")

  cfg_gadget = os.path.join(conf.configfs, "usb_gadget")
  if not os.path.isdir(cfg_gadget):
    return False, (f"Did not find the expected {cfg_gadget}. Ensure that the 'libcomposite' kernel module is loaded.")

  return True,""

def sanity_devices(conf):
  devices,msg = devicespec.load_devices(conf)
  if devices is None:
    return False,msg

  for name,dev in devices.items():
    if "metadata" not in dev:
      return False,f"A device is missing metadata. This is a bug in the device spec loader! Dev object: {str(dev)}"

    if "name" not in dev:
      return False,f"Device from {dev['metadata']['source']} has no name! Dev object: {str(dev)}"

    src = dev["metadata"]["source"]

    if "type" not in dev:
      return False,f"Device {name} from {src} has no type specified!"
  return True,""



def passes_sanity_checks(conf):

  for func in [ sanity_options,
                sanity_commands,
                sanity_udc,
                sanity_configfs,
                sanity_devices,
              ]:
    ok, msg = func(conf)
    if not ok: return False, msg

  return True, "All checks passed"
