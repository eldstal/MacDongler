import argparse
import json
import os
import time

import status

def load(conf):
  if not os.path.exists(conf.resume_file):
    status.info("Resume file not found. Starting from scratch.")
    return

  j = json.loads(open(conf.resume_file, "r").read())

  argparse_dict = vars(conf)
  argparse_dict.update(j)

  status.info("Loaded resume file.")


def save(conf, careful=False):
  if not conf.resume_file: return

  if os.path.exists(conf.resume_file):
    if careful:
      status.warn("Resume file already exists. You have 10 seconds to hit CTRL+C to avoid overwriting it.")
      time.sleep(10)

  argparse_dict = vars(conf)
  open(conf.resume_file, "w+").write(json.dumps(argparse_dict))
