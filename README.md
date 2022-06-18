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

 5. Mount the `gadgetfs` under `/dev/gadget/` (override check with `--no-check-gadgetfs`)
    ```
    # mkdir /dev/gadget
    # mount -t gadgetfs -o user,group gadget /dev/gadget
    ```

 6. 


## Raspbian hints

The above steps are general instructions for a typical linux install (tested on Kali linux with the `dummy_hdc` driver). If you're using a Rasbpberry Pi (from the 4 or Zero families) with raspbian OS, the following instructions may be helpful:

 2. The `gadgetfs` module does not need to be loaded. `dummy_hcd` is not built, but is only needed if you want to do software-only tests.

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

#### Rebooting
TODO: Add a `--reboot` flag to auto-reboot the dongle machine after each test. With `--resume`, this lets you work with a clean setup. It's slow, but may help with unstable UDC drivers, etc.

#### Delaying
TODO: Add a configurable delay between tests.
