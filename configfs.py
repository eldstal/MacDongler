import status
import os
import glob

def _globlinks(pattern):
  ret = glob.glob(pattern)
  ret = filter(os.path.islink, ret)
  return list(ret)

def _globdirs(pattern):
  ret = glob.glob(pattern)
  ret = filter(os.path.isdir, ret)
  return list(ret)

def _putstr(conf, root, subpath, contents):
  path = os.path.join(root, subpath)
  parent = os.path.dirname(path)

  if type(contents) != str:
    contents = str(contents)

  try:
    if not os.path.exists(parent):
      os.makedirs(parent)

    open(path, "w+").write(contents + "\n")

    if conf.debug:
      readback = open(path, "r").read().strip()
      status.debug(f"After writing {contents} to {path}, value is {readback}")

    return True,""

  except Exception as e:
    return False,str(e)

# Recursively apply a set of properties to the configfs,
# by creating directories and writing to files.
# If any write or mkdir fails, we bail out and report it.
def _put_properties(conf, root, tree):
  props = { name: val for name,val in tree.items() if type(val) in [ str, int, float, bool ]}
  subdirs = { name: val for name,val in tree.items() if type(val) == dict}

  for name,val in tree.items():
    if name not in props and name not in subdirs:
      return False,f"Property {name} applied to {root} is of unsupported type: {type(name)}"

  for key,val in props.items():
    if "/" in key:
      return False,f"Invalid key {key} in properties of {root}."

    ok,msg = _putstr(conf, root, key, val)
    if not ok:
      return False,(f"Failed to set configuration property {key} at {root}: " + msg)

  # Recurse down the tree of properties
  for key,sub_tree in subdirs.items():
    if "/" in key:
      return False,f"Invalid subdir {key} in properties of {root}."

    sub_root = f"{root}/{key}"
    ok,msg = _put_properties(conf, sub_root, sub_tree)
    if not ok:
      return False,(f"Failed to set up configuration tree {key} at {root}: " + msg)

  return True,""


# Generate a new, currently unused, configfs gadget directory
def select_gadget_path(conf):
  conf_root = os.path.join(conf.configfs, "usb_gadget")

  for n in range(100):
    name = f"macdongler_{n:02}"
    path = os.path.join(conf_root, name)

    if not os.path.exists(path):
      return path,""

  return None,"It seems that we've created too many gadgets already. Consider using --one-step and --resume, rebooting between runs."


# List all configfs directories which are created by MacDongler,
# in this instance or any other. Don't run multiple MacDonglers on the same
# machine.
def list_gadgets(conf):
  conf_root = os.path.join(conf.configfs, "usb_gadget")

  return list(glob.glob(os.path.join(conf_root, "macdongler_*")))


# Create a configfs directory and set up a device based on the provided spec
# returns the name of the created directory
def create_gadget(conf, dev):
  path,msg = select_gadget_path(conf)
  if path is None:
    return None,msg

  try:
    os.mkdir(path)
  except Exception as e:
    return None, (f"Failed to create gadget {path}: " + str(e))


  # Basic properties of the USB device
  if "properties" in dev:
    ok,msg = _put_properties(conf, path, dev["properties"])
    if not ok:
      status.warn(f"Failed to set property of {dev['name']}. Probably not supported by the kernel. Outdated device database? " + msg)

  #if conf.debug: input("RETURN to continue")


  # Device strings
  if "strings" in dev:
    os.mkdir(f"{path}/strings/{conf.language_code}")
    for key,val in dev["strings"].items():
      assert("/" not in key)
      ok,msg = _putstr(conf, path, f"strings/{conf.language_code}/{key}", val)
      if not ok:
        status.warn(f"Failed to set string {key} of {dev['name']}: " + msg)


  #if conf.debug: input("RETURN to continue")

  # Defined functions of the device
  if "functions" in dev:
    for fname,fspec in dev["functions"].items():
      assert("/" not in fname)

      fpath = f"{path}/functions/{fname}"
      os.mkdir(fpath)

      if "properties" in fspec:
        ok,msg = _put_properties(conf, fpath, fspec["properties"])
        if not ok:
          status.warn(f"Failed to configure function {fname} of {dev['name']}: " + msg)

  #if conf.debug: input("RETURN to continue")

  if "configs" in dev:
    for cname, cspec in dev["configs"].items():
      assert("/" not in cname)
      cpath = f"{path}/configs/{cname}"
      os.mkdir(cpath)

      if "properties" in cspec:
        ok,msg = _put_properties(conf, cpath, cspec["properties"])
        if not ok:
          status.warn(f"Failed to configure configuration {cname} of {dev['name']}: " + msg)

      if "strings" in cspec:
        os.mkdir(f"{cpath}/strings/{conf.language_code}")
        for key,val in cspec["strings"].items():
          assert("/" not in key)
          ok,msg = _putstr(conf, cpath, f"strings/{conf.language_code}/{key}", val)
          if not ok:
            status.warn(f"Failed to set configuration string {key} of {dev['name']} configuration {cname}: " + msg)

      if "functions" in cspec:
        for func in cspec["functions"]:
          if func not in dev["functions"].keys():
            status.warn("Device {dev['name']} configuration {cname} uses undefined function {func}. Ignoring.")
            continue

          os.symlink(f"{path}/functions/{func}", f"{cpath}/{func}")


  # Finally, connect the device to the host!
  ok,msg = _putstr(conf, path, "UDC", conf.udc_controller)
  if not ok:
    delete_gadget(conf, path)
    return None,msg


  return path,""


def delete_gadget(conf, path):
  if os.path.dirname(path) != os.path.join(conf.configfs, "usb_gadget"):
    return False,"Invalid path passed to delete_gadget. This is a bug in the software!. Bailing out."


  # Disconnect the USB device from the host
  _putstr(conf, path, "UDC", "")

  # Detach all functions from each config
  for l in _globlinks(f"{path}/configs/*/*"):
    os.remove(l)

  # Remove all strings for the configs
  for d in _globdirs(f"{path}/configs/*/strings/*"):
    os.rmdir(d)

  # Remove the OS description links
  for l in _globlinks(f"{path}/os_desc/*"):
    os.remove(l)

  # Remove configs
  for d in _globdirs(f"{path}/configs/*"):
    os.rmdir(d)

  # Remove functions
  for d in _globdirs(f"{path}/functions/*"):
    os.rmdir(d)

  # Remove global strings
  for d in _globdirs(f"{path}/strings/*"):
    os.rmdir(d)

  # Finally, remove the gadget itself
  os.rmdir(path)

  if os.path.exists(path):
    return False,"All operations succeeded, but gadget is still in place. This is a bug in the software!"

  return True,""
