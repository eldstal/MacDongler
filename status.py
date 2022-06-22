import sys
import os

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

def setup(conf):
  global STATUS_FILE
  global DO_COLOR
  global DO_DEBUG

  if conf.status_file is not None:
    STATUS_FILE=open(conf.status_file, "a+")

  if conf.no_color:
    DO_COLOR=False

  if conf.debug:
    DO_DEBUG=True

def found_device(conf, dev, path):
  lbl = paint("FOUND", "green")
  msg = f"Device {dev['name']} appears to work!"
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return


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

  msg = f"{round(frac*100)}% |{bar}|"
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return

def error(msg):
  lbl = paint("ERROR", "red")
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return

def warn(msg):
  lbl = paint("WARNING", "yellow")
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return

def info(msg):
  lbl = "INFO"
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return

def debug(msg):
  lbl = paint("DEBUG", "dark_gray")
  if DO_DEBUG: sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return


