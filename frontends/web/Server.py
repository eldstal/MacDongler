#!/usr/bin/env python3
#
# Serves two things:
# 1. The MacDongler status-file passed in on the command line
# 2. A small webapp to fetch and show that status-file
#
# The webapp runs all its logic clientside. That's important
# for MacDongler, since we may need to reboot the web server
# (i.e. the USB device) periodically. The webapp is robust to this.

import argparse
import sys
import json
import hashlib

from flask import Flask, Response, redirect

STATUS_FILE_PATH=""


def hash_string(text):
  m = hashlib.md5()
  m.update(text.encode())
  return m.hexdigest()

# For most paths, just serve static files
app = Flask(__name__,
            static_url_path="",
            static_folder="content")


# For the root, redirect to our static index.html
@app.route("/")
def serve_file():
  return redirect("/index.html")


# For the status file, serve whatever data is in the MacDongler status-file.
# Optionally, allow the client to filter by timestamp, since the status-file
# may grow -very- large over time.
@app.route("/status", methods=["GET"], defaults={"timestamp": 0})
@app.route("/status/<int:timestamp>")
def serve_log(timestamp):

  # Load the MacDongler status-file from disk
  # It's one JSON object per line, which is kind of dirty.

  # Convert it to a good old proper JSON list, so we can handle it from JavaScript
  log_data = []

  lines = []
  try:
    lines = open(STATUS_FILE_PATH, "r").readlines()
  except:
    pass

  # Only return entries newer than the provided timestamp
  # In addition, give each object a handy hash, so we can avoid duplication
  for l in lines:
    try:
      msg = json.loads(l)

      if msg["timestamp"] < timestamp:
        continue

      msg["hash"] = hash_string(l)
      log_data.append(msg)

    except Exception as e:
      print(e)

  return Response(json.dumps(log_data), mimetype="application/json")



def configure():
  parser = argparse.ArgumentParser(description="Serve a MacDongler status frontend, so you can see scan progress in your browser")

  parser.add_argument("--status-file", "-f", required=True, type=str, help="Status file written by the MacDongler script.")

  parser.add_argument("--host", "-H", type=str, default="0.0.0.0",
                      help="Interface(s) to listen on. Default: 0.0.0.0")

  parser.add_argument("--port", "-P", type=int, default=80,
                      help="Port to listen on. Default: 80")

  conf = parser.parse_args()

  return conf


def main():
  global STATUS_FILE_PATH

  conf = configure()

  STATUS_FILE_PATH = conf.status_file

  app.run(debug=False,
          host="0.0.0.0", port=80,
          threaded=True, processes=1)

  return 0


if __name__ == "__main__":
  sys.exit(main())


