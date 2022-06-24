import sys
import os
import json
import time

# Color isn't a vital feature.
# If you're missing the `colored` library, so be it.
DO_COLOR=False
try:
  import colored
  DO_COLOR=True
except:
  DO_COLOR=False

STATUS_FILE=None
DO_DEBUG=False

def paint(text, color):
  global DO_COLOR
  if DO_COLOR:
    return colored.stylize(text, colored.fg(color))
  else:
    return text

# Drop a JSON object to the status file

def _log_status(kind, obj):
  if STATUS_FILE is None: return

  obj["kind"] = kind
  obj["timestamp"] = int(time.time())
  j = json.dumps(obj).replace("\n", "").strip()
  with open(STATUS_FILE, "a+") as f:
    f.write(j + "\n")

def _fallback(obj, key, val):
  if key in obj:
    return obj[key]
  return val

def setup(conf):
  global STATUS_FILE
  global DO_COLOR
  global DO_DEBUG

  if conf.status_file is not None:
    STATUS_FILE=conf.status_file

  if conf.no_color:
    DO_COLOR=False

  if conf.debug:
    DO_DEBUG=True

def found_device(conf, dev, path):
  lbl = paint("FOUND", "green")
  msg = f"Device {dev['name']} appears to work!"
  sys.stderr.write(f"{lbl}: {msg}\n")
  _log_status("found",
      {
        "device_name": dev["name"],
        "device_type": dev["type"],
        "device_vid": dev["properties"]["idVendor"],
        "device_pid": dev["properties"]["idProduct"],
      })

def testing_device(conf, dev):
  lbl = paint("TESTING", "blue")
  msg = f"Preparing to test {dev['name']}!"
  sys.stderr.write(f"{lbl}: {msg}\n")

  vid = _fallback(dev["properties"], "idVendor", 0)
  pid = _fallback(dev["properties"], "idProduct", 0)
  _log_status("current_device",
      {
        "device_name": dev["name"],
        "device_type": dev["type"],
        "device_vid": vid,
        "device_pid": pid
      })


def progress(current, target):
  lbl = paint("PROGRESS", "violet")
  try:
    w,h = os.get_terminal_size()
  except:
    w,h = 60,25

  w = min(w, 80)

  tot = w - len(lbl) - 4
  frac = current / target
  barw = int(frac * tot)

  bar = "=" * barw
  bar += " " * (tot-barw)

  msg = f"{round(frac*100):3d}% |{bar}|"
  sys.stderr.write(f"{lbl}: {msg}\n")

  _log_status("progress",
      {
        "current": current,
        "target": target,
        "percent": round(frac*100)
      })

def error(msg):
  lbl = paint("ERROR", "red")
  sys.stderr.write(f"{lbl}: {msg}\n")

  _log_status("message",
      {
        "level": "error",
        "text": msg,
      })

def warn(msg):
  lbl = paint("WARNING", "yellow")
  sys.stderr.write(f"{lbl}: {msg}\n")

  _log_status("message",
      {
        "level": "warning",
        "text": msg,
      })

def info(msg):
  lbl = "INFO"
  sys.stderr.write(f"{lbl}: {msg}\n")

  _log_status("message",
      {
        "level": "info",
        "text": msg,
      })

def debug(msg):
  if not DO_DEBUG: return
  lbl = paint("DEBUG", "dark_gray")
  sys.stderr.write(f"{lbl}: {msg}\n")
  _log_status("message",
      {
        "level": "debug",
        "text": msg,
      })


