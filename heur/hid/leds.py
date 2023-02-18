import subprocess
import select
import json5
import os

import status

import heur.hid.util

class Leds:
  def init(self, conf, dev, path):
    # This may be multiple nodes.
    self.devnodes = heur.hid.util.find_hiddev(conf, dev, path)


  def stim(self, conf, dev, path):
    pass


  def test(self, conf, dev, path):
    if self.devnodes is None: return False

    success = False

    for n in self.devnodes:
      try:
        fd = os.open(n, flags=os.O_RDWR, mode=0o666)
      except Exception as e:
        status.debug(f"heur.hid.leds: Failed to open {n}: " + str(e))
        continue

      # Read out whatever report was already in the tube
      while True:
        rept = self.try_read_report(fd, 0.1)
        if rept is None: break

      #
      # Using the hid_gadget_test program from kernel sources,
      # we can glean this:
      # --caps-lock
      # xmit report: 00 00 39 00 00 00 00 00
      # xmit report: 00 00 00 00 00 00 00 00
      # recv report: 02
      # --caps-lock
      # xmit report: 00 00 39 00 00 00 00 00
      # xmit report: 00 00 00 00 00 00 00 00
      # recv report: 00

      for code in [ 0x53,     # Num lock
                    0x39,     # Caps lock
                    #0x84,     # Scroll lock, doesn't seem to work for this
                  ]:

        # Send a report to toggle that function
        tx_report = bytes([0x00, 0x00, code, 0x00, 0x00, 0x00, 0x00, 0x00])

        # Send the command once
        os.write(fd, tx_report)
        os.write(fd, bytes([0x00]*8))
        rept_1 = self.try_read_report(fd, 1)
        status.debug(f"heur.hid.leds: key code {code} once: {rept_1}")

        # Send the command twice!
        os.write(fd, tx_report)
        os.write(fd, bytes([0x00]*8))
        rept_2 = self.try_read_report(fd, 1)
        status.debug(f"heur.hid.leds: key code {code} twice: {rept_2}")

        if rept_1 != rept_2:
          success = True

      os.close(fd)


    return success


  def cleanup(self, conf, dev, path):
    pass


  def try_read_report(self, fd, timeout):
    r,_,_ = select.select([fd], [], [], timeout)

    if len(r) > 0:
      return os.read(fd, 1)
    else:
      return None
