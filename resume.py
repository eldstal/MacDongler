import argparse
import json5
import os
import time

import status

def load(conf):
  if not os.path.exists(conf.resume_file):
    status.info("Resume file not found. Starting from scratch.")
    return

  j = json5.loads(open(conf.resume_file, "r").read())

  argparse_dict = vars(conf)
  argparse_dict.update(j)

  status.info(f"Loaded resume file {conf.resume_file}.")


def save(conf, careful=False):
  if not conf.resume_file: return

  if os.path.exists(conf.resume_file):
    if careful:
      status.warn(f"Resume file {conf.resume_file} already exists. You have 15 seconds to hit CTRL+C to avoid overwriting it.")
      time.sleep(15)

  argparse_dict = vars(conf)
  open(conf.resume_file, "w+").write(json5.dumps(argparse_dict))
