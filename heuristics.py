
# These are the heuristics supported, which help determine if a device is accepted by the host.
# The key is the name of the heuristic,
# the value is a dict of of { description, device_types=[], handler=class) }

# The class shall expose three methods:
# - setup will be called right after the device is created
# - test will be called after any user-configured test duration (--test-duration)
# - cleanup will be called before the device is torn down
#
# All methods will be called with (conf, devspec, gadget_path)
#
# test_function should return True if the device is deemed to have been active, i.e. it is
# recognized and accepted by the target USB host.

import copy
import time

import status

import heur.net.rx
import heur.serial.rx

HEURISTICS = {

  "net.rx": {
              "description": "Test if any data is received on the interface. Combine with --net-send-pcap to stimulate the host",
              "device_types": [ "net" ],
              "handler": heur.net.rx.RX
            },

  "serial.rx": {
              "description": "Test if any data is received on the serial port.",
              "device_types": [ "serial" ],
              "handler": heur.serial.rx.RX
            },
}

def list_heuristics(conf):
  return copy.deepcopy(HEURISTICS)



# Provide a loaded and active gadget
# returns True heuristic tests indicate an active device
# returns False if the device appears inactive
# This is controlled by --and
def test_device(conf, dev, path):

  tests = {}
  for name, spec in HEURISTICS.items():
    if dev["type"] in spec["device_types"]:
      tests[name] = spec["handler"]()

  if len(tests) == 0:
    status.warn(f"No tests relevant for device {dev['name']} of type {dev['type']}.")
    return False

  if len(tests) > 1:
    status.info(f"{len(tests)} tests relevant for this device: {list(tests.keys())}")

  for name,obj in tests.items():
    obj.setup(conf, dev, path)

  time.sleep(conf.test_duration)

  results = []
  for name,obj in tests.items():
    results.append(obj.test(conf, dev, path))

  for name,obj in tests.items():
    obj.cleanup(conf, dev, path)


  if conf.any:
    return any(results)
  else:
    return all(results)
