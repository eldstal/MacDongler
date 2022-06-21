# MacDongler
A USB host scanner based on Linux USB Gadgets, designed to circumvent USB device blocklists.

MacDongler cycles through a list of known USB device configurations, Vendor IDs and Product IDs. It then emulates each device to see if the plugged in USB host allows or interacts with the device.

This is useful to, for example, identify specific brands or models of USB dongles allowed by a locked-down device.


## Prerequisites

These things need to be set up in the system before MacDongler will run properly. Wherever possible, the script performs these sanity checks automatically.

 1. Make sure your kernel is configured with the following options (override check with --no-check-kconfig)
    - `CONFIG_CONFIGFS_FS`
    - `CONFIG_USB_GADGET`
    - `CONFIG_USB_DUMMY_HCD`
    - `CONFIG_USB_CONFIGFS`
    - `CONFIG_USB_LIBCOMPOSITE`

 2. Make sure at least one `udc` kernel module is compiled in or loaded, i.e.
    your desired USB Device Controller is visible under `/sys/class/udc` (override check with `--no-check-sysdev`)
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

 5. 


## Raspbian hints

The above steps are general instructions for a typical linux install (tested on Kali linux with the `dummy_hdc` driver). If you're using a Rasbpberry Pi (from the 4 or Zero families) with raspbian OS, the following instructions may be helpful:

 1. Raspbian does not provide the `dummy_hcd` module, but is only needed if you want to do software-only tests.

 2. Add the line `dtoverlay=dwc2` to your `/boot/config.txt` and reboot to get the hardware UDC controller running.
  This should give you something under `/sys/class/udc`. It may have a different name, that's fine.
  ```
  # ls /sys/class/udc
  fe980000.usb
  ```


## Usage

### Results


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

To get an idea for the exact values expected from a device specification, take a look at `--list-devices`:

```
MacDongler --list-devices linksys-usb3gigv1
```

