
import subprocess
import json5

import status

import heur.net.util

class Link:
  def init(self, conf, dev, path):
    self.iface = heur.net.util.find_iface(conf, dev, path)

    if self.iface is None:
      status.warn(f"net.link: Unable to determine interface name for {path}.")
    else:
      status.debug(f"net.link: Found network interface {self.iface}")


  def stim(self, conf, dev, path):
    pass

  def test(self, conf, dev, path):
    if self.iface is None: return False

    link_down = True
    try:
      # The ip command can output json! Great!
      out = subprocess.check_output(["ip", "-json", "link", "show", f"{self.iface}"])
      stats = json5.loads(out.decode())

      for netdev in stats:
        if netdev["ifname"] != self.iface: continue
        link_down = "NO-CARRIER" in netdev["flags"]

    except Exception as e:
      status.warn("net.link: Failed to invoke 'ip'. Test fails. " + str(e))

    return not link_down


  def cleanup(self, conf, dev, path):
    pass
