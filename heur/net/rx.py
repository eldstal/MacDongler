import subprocess
import json5

import status

import heur.net.util

class RX:
  def setup(self, conf, dev, path):
    self.iface = heur.net.util.find_iface(conf, dev, path)

    if self.iface is None:
      status.warn(f"net.rx: Unable to determine interface name for {path}.")
    else:
      status.debug(f"net.rx: Found network interface {self.iface}")


  def test(self, conf, dev, path):
    if self.iface is None: return False

    count = 0

    try:
      # The ip command can output json! Great!
      out = subprocess.check_output(["ip", "-stats", "-json", "link", "show", f"{self.iface}"])
      stats = json5.loads(out.decode())

      for netdev in stats:
        if netdev["ifname"] != self.iface: continue
        count = netdev["stats64"]["rx"]["bytes"]
    except Exception as e:
      status.warn("net.rx: Failed to invoke 'ip'. Test fails. " + str(e))

    return count > 0


  def cleanup(self, conf, dev, path):
    pass
