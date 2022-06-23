#
# Code shared between multiple net heuristic modules
#

import glob

def find_iface(conf, dev, path):
  iface = None

  # RNDIS and ECM devices list their local interface name in configfs
  for g in glob.glob(f"{path}/functions/*/ifname"):
    try:
      iface = open(g,"r").read().strip()
    except:
      pass

  return iface
