import os


def find_mount(fstype):
  pass


def detect_gadgetfs(conf):
  if conf.gadgetfs: return

#
# Some command-line arguments default to auto-detection
# This is where that's done.
#
def detect_settings(conf):
  return conf
