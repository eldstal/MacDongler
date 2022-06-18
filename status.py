

STATUS_FILE=None

def setup(conf):
  if conf.status_file is not None:
    STATUS_FILE=open(conf.status_file, "a+")

def progress(current, target):
  if not STATUS_FILE: return

def error(msg):
  print("ERROR: " + msg)
  if not STATUS_FILE: return

def warn(msg):
  print("WARNING: " + msg)
  if not STATUS_FILE: return

def info(msg):
  print("INFO: " + msg)
  if not STATUS_FILE: return
