# MacDongler
A USB host scanner based on Linux USB Gadgets, designed to circumvent USB device blocklists.

MacDongler cycles through a list of known USB device configurations, Vendor IDs and Product IDs. It then emulates each device to see if the plugged in USB host allows or interacts with the device.

This is useful to, for example, identify specific brands or models of USB dongles allowed by a locked-down device.


## Prerequisites

These things need to be set up in the system before MacDongler will run properly. Wherever possible, the script performs these sanity checks automatically.

 1. Make sure your kernel is configured with the following options
    - `CONFIG_CONFIGFS_FS`
    - `CONFIG_USB_GADGET`
    - `CONFIG_USB_DUMMY_HCD`
    - `CONFIG_USB_CONFIGFS`
    - `CONFIG_USB_LIBCOMPOSITE`

 2. Make sure at least one `udc` kernel module is compiled in or loaded, i.e.
    your desired USB Device Controller is visible under `/sys/class/udc`
    ```
    # modprobe dummy_hcd
    # ls -l /sys/class/udc
    dummy_udc.0
    ```

 3. Mount the `configfs` under `/sys/kernel/config` if it isn't already:
    ```
    # mount -t configfs none /sys/kernel/config
    # ls /sys/kernel/config
    ```

 4. Make sure the `libcomposite` kernel module is loaded


## Raspbian hints

The above steps are general instructions for a typical linux install (tested on Kali linux with the `dummy_hcd` driver). If you're using a Rasbpberry Pi (from the 4 or Zero families) with raspbian OS, the following instructions may be helpful:

 1. Raspbian does not provide the `dummy_hcd` module, but is only needed if you want to do software-only tests.

 2. Add the line `dtoverlay=dwc2` to your `/boot/config.txt` and reboot to get the hardware UDC controller running.
  This should give you something under `/sys/class/udc`. It may have a different name, that's fine.
  ```
  # ls /sys/class/udc
  fe980000.usb
  ```


## Usage

### Results

The output file follows the exact same format as the device database, and can be used as such. If a device is tested and heuristics indicate that the device is accepted by the host, a complete device specification is appended to the output file. You can then inspect the properties (e.g VID and PID of the device) or use `--create-device` to set up persistent emulation with the same parameters

```
    # Run the scan against our host
  $ ./MacDongler --output /tmp/network.json5 --test-multiple net
    ...
    FOUND: Device acm-2.0 appears to work!
    ...

    # Take a look at what was found
  $ ./MacDongler --device-db /tmp/network.json5 --list-devices
    ...
    acm-2.0
    ...

    # Emulate one of the successful devices
  $ ./MacDongler --device-db /tmp/network.json5 --create-device acm-2.0
    ...
    INFO: Created device acm-2.0 at /dev/ttyGS0

```

### Stability hacks
Given the risk of driver failure, since this script is basically fuzzing your USB stack, a number of features exist to help make the process more robust.

#### Resuming
By providing `--resume`, you can pick up where the last execution left off. This will start from the next un-tested USB device. This allows you to reboot your dongle machine, if needed.

#### Single-step
Run with the `--single-step` (`-1`) to terminate after testing a single device. On particularly troublesome hardware, this allows you to easily script a rebooting loop by putting something like this in your autostart:

```
MacDongler --resume --single-step --scan-devices 'ecm.*' 'rndis.*'
[ $_ -eq 10 ] && reboot
```

This way, the system will boot, a single new device will be tested (`--resume` ensures that progress is saved), and then the system will reboot again. This will continue until all devices have been tested.

#### Delaying
TODO: Add a configurable delay between tests.



## Device database
Supported devices are specified in JSON5 files, in a simple hierarchical directory structure. Each device specification has a name, which is how it is referred to on the command line.

Each device specification can designate a single "template", which is another device name. The new device will be based on the template device, only overriding the settings present in the new specification.

The template can be the name of any device defined __in a parent directory__ of the current device specification. The following example illustrates the template support:

```
File structure:
devices/net/rndis_template.json5
devices/net/rndis_devices/abcd.json5
devices/msc/msc_template.json5


rndis_template.json5:
[
   { "name": "rndis",
     "feature": "value",
     "identifier": "TMPL",
   },
]


abcd.json5:
[
  { "name": "abcd",
    "template": "rndis",
    "identifier": "ABCD",
  },

  { "name": "qwer",
    "template": "rndis",
    "feature": "another_value",
  }
]

```


The two devices `abcd` and `qwer` will inherit all properties from the `rndis` device. `abcd` will override the `identifier` field, and get `feature` from the template.

These devices **cannot** specify anything from `msc_template` as their template, since that file isn't in a parent directory.

To get an idea for the exact values expected from a device specification, take a look at `--list-devices` with exactly one device:

```
MacDongler --list-devices linksys-usb3gigv1
```


## TODO
 - Sanity check device database. Are you using functions that aren't defined? Do you have a valid device type? Are the function types as expected (soft error)
 - More device types
    - HID
    - Audio?
 - Database generator
    - Create generic devices with a template (such as rndis-2.0)
    - Take VID/PID from the [open database](http://www.linux-usb.org/usb.ids)
 - One-shot mode
    - test-multiple, but stop at the first successful device and leave it up
    - immediately bridge the network to eth0 or expose the serial port or whatever
    - plug in, auto-hack, success!
 - Automatic activity test once a device is set up
    - net: is the link up? (conflicts with having to bring the link up for pcap transmission.)
        - May have to do setup -> stim -> test delay -> test
    - serial: got configured?
    - storage: was the FAT read?
    - storage: was anything updated (last mount time?!)
    - storage: transferred bytes?
    - generic: number of USB commands received...?
