import time
import random

import status

#
# Pseudo-operation
# Generates log output to simulate a normal run,
# but does nothing else
#

def pretend(conf, devices):
  status.info("Running in play pretend mode - generating some log output")

  if len(conf.devices) == 0:
    status.info("No devices specified. Selecting 20 random devices.")
    conf.devices = random.sample(devices.keys(), 20)


  # Make sure there's at least one success, one failure and one error
  # The rest can be random.

  outcomes = [ "good", "bad", "error" ]

  for i in range(len(outcomes), len(conf.devices)):
    outcomes += [ random.choice(
                            [ "error" ]*1 +
                            [ "good", ]*2 +
                            [ "bad" ]*10
                           )]

  random.shuffle(outcomes)

  status.progress(0, len(conf.devices))

  for i in range(len(conf.devices)):
    name = conf.devices[i]
    dev = devices[name]
    path = f"/sys/config/kernel/usb_gadget/macdongler_{i}"

    status.testing_device(conf, dev)

    outcome = outcomes[i]

    time.sleep(random.uniform(3, 15))

    if outcome == "error":
      status.warn(f"Device creation seems slow...")
      time.sleep(2)
      status.error(f"Creating device {name}: Unable to set it up properly.")

    elif outcome == "good":
      status.found_device(conf, dev, path)

    elif outcome == "bad":
      status.info(f"Checked device {name}, was not accepted by the host")


    status.progress(i+1, len(conf.devices))



