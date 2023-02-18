#
# Active stimulation of the host via emulated devices
#

import os
import subprocess

import status
import heur.net.util
import heur.serial.util

def _net_force_up(conf, dev, path):

  iface = heur.net.util.find_iface(conf, dev, path)

  if iface is None:
    status.warn(f"stim.net.force_up: Unable to determine interface name of {path}")
    return

  try:
    subprocess.run(["ip", "link", "set", iface, "up"],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT)
  except:
    status.warn(f"stim.net.force_up: Unable to bring up device {iface}")

  return

# Triggered by --net-transmit-pcap
def _net_transmit_pcap(conf, dev, path):
  if not conf.net_transmit_pcap: return
  if dev["type"] != "net": return

  iface = heur.net.util.find_iface(conf, dev, path)

  if iface is None:
    status.warn(f"stim.net.pcap: Unable to determine interface name of {path}")
    return

  for filename in conf.net_transmit_pcap:
    if not os.path.exists(filename):
      status.warn(f"stim.net.pcap: pcap file not found: {filename}")
      continue

    try:
      result = subprocess.run(["tcpreplay", f"--intf1={iface}", filename],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
      #status.debug("tcpreplay output: " + result.stdout)
    except Exception as e:
      status.warn("stim.net.pcap: Failed to invoke tcpreplay: " + str(e))


def _serial_transmit_file(conf, dev, path):
  if not conf.serial_transmit_file: return
  if dev["type"] != "serial": return

  iface = heur.serial.util.find_tty(conf, dev, path)

  if iface is None:
    status.warn(f"stim.serial.transmit: Unable to determine device name of {path}")
    return

  try:
    # Must open non-blocking, because an unconnected tty won't buffer data
    fd = os.open(iface, os.O_WRONLY | os.O_NONBLOCK)
  except:
    status.warn(f"stim.serial.transmit: Failed to open device {iface} for writing")
    return

  for filename in conf.serial_transmit_file:
    if not os.path.exists(filename):
      status.warn(f"stim.serial.transmit: input file not found: {filename}")
      continue

    data = open(filename, "rb").read()
    status.debug(f"stim.serial.transmit: Writing data to serial port (non-blocking)")
    os.write(fd, data)
    os.close(fd)
    status.debug(f"stim.serial.transmit: done")

# Look at the user's configuration and carry out whichever stimulation
# is appropriate for this device
def stimulate_device(conf, dev, path):

  if dev["type"] == "net":
    _net_force_up(conf, dev, path)
    _net_transmit_pcap(conf, dev, path)

  if dev["type"] == "serial":
    _serial_transmit_file(conf, dev, path)
