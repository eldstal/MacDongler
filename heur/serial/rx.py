
import os

import status
import heur.serial.util


class RX:
  def setup(self, conf, dev, path):
    self.dev = heur.serial.util.find_tty(conf, dev, path)

    if self.dev is None:
      status.warn(f"serial.rx: Unable to determine interface name for {path}.")
    else:
      status.debug(f"serial.rx: Found serial interface {self.dev}")

    if self.dev is not None:
      try:
        self.fd = open(self.dev, "rb")
        os.set_blocking(self.fd.fileno(), False)
      except Exception as e:
        status.error(f"serial.rx: Failed to open serial port {self.dev} for reading: " + str(e))
        self.dev = None
        self.fd = None

  def test(self, conf, dev, path):
    if self.dev is None: return False
    if self.fd is None: return False

    # Non-blocking read!
    data = self.fd.read()

    if data is None:
      return False

    if len(data) > 0:
      status.debug(f"serial.rx: Received {len(data)} bytes on the serial port!")

    return len(data) > 0



  def cleanup(self, conf, dev, path):
    if self.fd is not None:
      self.fd.close()
