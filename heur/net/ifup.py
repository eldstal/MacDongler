import subprocess
import json5

import status

import heur.net.util

class IfUp:
  def init(self, conf, dev, path):
    self.iface = heur.net.util.find_iface(conf, dev, path)

    self.was_up = False

    if self.iface is None:
      status.warn(f"net.ifup: Unable to determine interface name for {path}.")
    else:
      status.debug(f"net.ifup: Found network interface {self.iface}")

    # Do the actual test here, because we need to measure before the
    # global stimulation forces the interface up

    try:
      # The ip command can output json! Great!
      out = subprocess.check_output(["ip", "-json", "link", "show", f"{self.iface}"])
      stats = json5.loads(out.decode())

      for netdev in stats:
        if netdev["ifname"] != self.iface: continue
        self.was_up = "UP" in netdev["flags"]
    except Exception as e:
      status.warn("net.ifup: Failed to invoke 'ip'. Test fails. " + str(e))


  def stim(self, conf, dev, path):
    pass

  def test(self, conf, dev, path):
    if self.iface is None: return False

    return self.was_up


  def cleanup(self, conf, dev, path):
    pass
