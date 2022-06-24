import json5
import os
import copy
import pathlib

import status

# Cached copy of the loaded device database
DEVICE_DB=None

def _merge_databases(dest_db, src_db):
  for name,src_dev in src_db.items():
    if name in dest_db:
      dst_dev = dest_db[name]
      return None,f"Device name {name} is defined in both {src_dev['metadata']['source']} and {dst_dev['metadata']['source']}"

    dest_db[name] = src_dev

  return dest_db,""

def _merge_dicts(a, b):
  res = copy.deepcopy(a)

  for key,new_val in b.items():
    if key not in res:
      res[key] = new_val
    elif type(res[key]) != type(new_val):
      # Override!
      res[key] = new_val
    elif type(res[key]) != dict:
      res[key] = new_val
    elif type(res[key]) == dict:
      merged,msg = _merge_dicts(res[key], new_val)
      if merged is None:
        return None, f"{key}." + msg
      else:
        res[key] = merged
  return res,""


# Fill a device spec in with template data, if it has a template specified
def _apply_template(conf, parent_db, dev):
  if "template" not in dev: return dev,""

  if dev["template"] not in parent_db:
    return None, f"Unable to resolve template name {dev['template']} for device {dev['name']}."
  template = parent_db[dev["template"]]

  res,msg = _merge_dicts(template, dev)
  if res is None:
    return None,f"Failed to apply template {dev['template']} to device {dev['name']}: " + msg

  return res,""


# Load a device file containing multiple device specs.
def _load_device_file(conf, parent_db, filepath):
  try:
    devlist = json5.loads(open(filepath, "r").read())
  except Exception as e:
    return None,f"Failed to load device file {filepath}: " + str(e)

  if type(devlist) is not list:
    return None,f"Malformed device file {filepath}. Should be a list of objects."

  # Perform some sanity checks on the new device
  for dev in devlist:
    if "name" not in dev:
      return None,f"Device in {filepath} is missing a name. Device object contents: {str(dev)}"
    if type(dev) is not dict:
      return None,f"Device in {filepath} is not an object. Device contents: {str(dev)}"

  # Add some metadata to each device definition
  for dev in devlist:
    if "metadata" not in dev: dev["metadata"] = {}
    dev["metadata"]["source"] = filepath

  resolved = { }
  # Resolve templates as needed
  for dev in devlist:

    if dev['name'] in resolved:
      return None,f"Device file {filepath} contains multiple devices named {dev['name']}"

    dev,msg = _apply_template(conf, parent_db, dev)
    if dev is None:
      return None,f"Failed to load device file {filepath}: " + msg

    resolved[dev['name']] = dev

  return resolved,""


def _is_dev_file(path):
  b = os.path.basename(path)
  if b[0] == ".": return False
  if os.path.splitext(b)[-1] == ".json5": return True
  return False


# Recursively load a device database directory
def _load_devices_dir(conf, root, parent_db=None):
  if parent_db is None: parent_db = {}
  else: parent_db = copy.deepcopy(parent_db)

  #print(f"Loading dev dir {root}")

  subs = os.listdir(root)
  subs = [ os.path.join(root, s) for s in subs ]
  subdirs = list(filter(os.path.isdir, subs))
  subfiles = list(filter(os.path.isfile, subs))
  subfiles = list(filter(_is_dev_file, subfiles))

  #print("dirs: " + str(subdirs))
  #print("files: " + str(subfiles))

  this_db = {}

  for subfile in subfiles:

    file_db,msg = _load_device_file(conf, parent_db, subfile)
    if file_db is None:
      return None,msg

    this_db,msg = _merge_databases(this_db, file_db)
    if this_db is None:
      return None,f"While merging {subfile}: " + msg

  #print(f"Dir {root} has devices {this_db.keys()}")

  parent_db,msg = _merge_databases(parent_db, this_db)
  if parent_db is None:
    return None,f"While merging root {root} to parent: " + msg

  ret_db = {}

  for subdir in subdirs:
    sub_db,msg = _load_devices_dir(conf, subdir, parent_db)
    if sub_db is None:
      return None, msg

    #print(f"Subdir {subdir} has devices {sub_db.keys()}")

    ret_db,msg = _merge_databases(ret_db, sub_db)
    if ret_db is None:
      return None,f"While merging subdir {subdir}: " + msg

  ret_db,msg = _merge_databases(this_db, ret_db)
  if ret_db is None:
    return None,f"While merging all subdirs of {root}: " + msg

  return ret_db,""



# Load the device database from its directory of cascading JSON5 files
# This will apply templates so that all device descriptions are "complete".
def load_devices(conf):
  global DEVICE_DB
  if DEVICE_DB is None:

    db = None
    msg = f"Device database is not a directory or file: {conf.device_db}"

    if os.path.isfile(conf.device_db):
      # Load a single file database,
      # probably output from an earlier test
      db,msg = _load_device_file(conf, {}, conf.device_db)

    elif os.path.isdir(conf.device_db):
      db,msg = _load_devices_dir(conf, conf.device_db)


    if db is None:
      msg = "Failed to load device database: " + msg
      status.error(msg)
      return None,msg
    DEVICE_DB = db

  return copy.deepcopy(DEVICE_DB),""


# Given some globs, expand to device names that are present in the device database
# A glob either matches device names using wildcards, or it exactly matches a device type.
def expand_device_list(conf, patterns):
  if type(patterns) == str: patterns = [patterns]

  devices,msg = load_devices(conf)
  if devices is None:
    return []

  ret = []

  all_dev_names = list(devices.keys())
  all_devs = list(devices.values())
  for p in patterns:
    name_matches = [ n for n in all_dev_names if pathlib.PurePath(n).match(p) ]
    ret += name_matches

    type_matches = [ dev['name'] for dev in all_devs if dev['type'] == p ]
    ret += type_matches

  # Don't return template-only devices
  ret = [ r for r in ret if devices[r]["type"] != "template" ]

  return ret


