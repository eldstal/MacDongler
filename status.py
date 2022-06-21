import sys

# Color isn't a vital feature.
# If you're missing the `colored` library, so be it.
DO_COLOR=False
try:
  import colored
  DO_COLOR=True
except:
  DO_COLOR=False

STATUS_FILE=None

def paint(text, color):
  global DO_COLOR
  if DO_COLOR:
    return colored.stylize(text, colored.fg(color))
  else:
    return text

def setup(conf):
  global STATUS_FILE
  global DO_COLOR

  if conf.status_file is not None:
    STATUS_FILE=open(conf.status_file, "a+")

  if conf.no_color:
    DO_COLOR=False

def progress(current, target):
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
  sys.stderr.write(f"{lbl}: {msg}\n")
  if not STATUS_FILE: return
