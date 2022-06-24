#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022 Albin Eldstål-Ahrens
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT
#
# MacDongler front-end for the Adafruit PiOLED 128x32
# Display: https://www.adafruit.com/product/3527
#
# Based on example code by AdaFruit

import time
import subprocess
import select
import argparse
import sys
import os

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import json


# This is a gross hack, courtesy of stackoverflow
# I love it!
# This function works as an endless generator,
# use it to poll for new log data
def try_read_line(filename):
  f = subprocess.Popen(['tail', '-n', '+0', '-F', filename],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  p = select.poll()
  p.register(f.stdout)

  while True:
    if p.poll(1):
      yield f.stdout.readline().decode()
    else:
      yield None

#
# Display setup, from AdaFruit's example code
#
def setup_display():
  # Create the I2C interface.
  i2c = busio.I2C(SCL, SDA)

  # Create the SSD1306 OLED class.
  # The first two parameters are the pixel width and pixel height.  Change these
  # to the right size for your display!
  disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

  # Clear display.
  disp.fill(0)
  disp.show()

  return disp

def get_text_length(text, font):
  l,t,r,b = font.getbbox(text)
  return r-l

def cut_text_to_length(text, width, font):
  l = font.getlength(text)
  ret = text
  while len(ret) > 0 and l > width:
    ret = ret[:-1]
    l = font.getlength(ret)

  if len(ret) < len(text):
    if len(ret) > 2:
      ret = ret[:-2] + ".."
  return ret

def draw_state(state, draw, font_small, font_large, w, h):

  if "anim" not in state:
    state["anim"] = {
      "circ": -90,
      "message": {
          "offset": 3,
          "direction": 1,
          "pause": 5,
          "text": ""
      }
    }

  draw.rectangle((0, 0, w, h), outline=0, fill=0)

  # Top indicator row, center
  tic = 10
  ric = w-10
  lic = 10

  ps = 16
  pm = 2
  if "progress" in state:
    state["anim"]["circ"] = (state["anim"]["circ"] + 10) % 360
    astart = state["anim"]["circ"]
    aend = astart + (360 * state["progress"] / 100)
    draw.arc([( ric-ps/2, tic-ps/2 ), (ric+ps/2, tic+ps/2)],
             astart, aend,
             1,
             1)

    draw.text((w-pm-(ps//2), pm+(ps//2)),
              str(state["progress"]),
              fill=1,
              font=font_small,
              anchor="mm",
              align="center"
              )


  draw.text((w/2,2),
            "MacDongler",
            fill=1,
            font=font_small,
            anchor="mt")


  if "found" in state:
    txt = f"Found:\n{state['found']}"

    draw.text((lic,tic),
              txt,
              fill=1,
              font=font_small,
              spacing=1,
              anchor="mm",
              align="center")

  if "current_device" in state:

    draw.text((w/2,tic+4),
              cut_text_to_length(state["current_device"], w-3*ps, font_large),
              fill=1,
              font=font_large,
              anchor="mm",
              align="center")

  if "message" in state:
    t = state["message"]
    if t != state["anim"]["message"]["text"]:
      state["anim"]["message"] = { "offset": 2, "direction": 1, "pause": 15, "text": t }

    # Long text animates, bouncing back and forth
    l = get_text_length(t, font_large)
    off_left = w - l - 2
    off_right = 2

    if l <= (w-4):
      # No need to animate at all. Just center it
      state["anim"]["message"]["offset"] = (w - l)//2

    elif state["anim"]["message"]["offset"] >= off_right and state["anim"]["message"]["pause"] > 0:
      # Paused left
      state["anim"]["message"]["pause"] -= 1

    elif state["anim"]["message"]["offset"] <= off_left and state["anim"]["message"]["pause"] > 0:
      # Paused right
      state["anim"]["message"]["pause"] -= 1

    elif state["anim"]["message"]["pause"] == 0:
      # Ready to switch direction and start moving
      state["anim"]["message"]["pause"] = 5
      state["anim"]["message"]["direction"] *= -1
      state["anim"]["message"]["offset"] += state["anim"]["message"]["direction"]

    else:
      # Plain old moving
      state["anim"]["message"]["offset"] += state["anim"]["message"]["direction"]

    draw.text((state["anim"]["message"]["offset"], h-5),
              t,
              fill=1,
              font=font_large,
              anchor="lm",
              align="left")

def update_state(state, log_text):
  try:
    log_entry = json.loads(log_text)

    if log_entry["kind"] == "message":
      if log_entry["level"] in [ "warning" ]:
        state["message"] = f"W:{log_entry['text']}"
      elif log_entry["level"] in [ "error" ]:
        state["message"] = f"E:{log_entry['text']}"

    elif log_entry["kind"] == "current_device":
      state["current_device"] = log_entry["device_name"]

    elif log_entry["kind"] == "progress":
      state["progress"] = log_entry["percent"]

    elif log_entry["kind"] == "found":
      nam = log_entry["device_name"]
      vid = log_entry["device_vid"]
      pid = log_entry["device_pid"]
      typ = log_entry["device_type"]
      state["message"] = f"! {typ} {vid:x}:{pid:x} {nam} !"
      state["found"] += 1

  except Exception as e:
    sys.stderr.write(f"Unable to parse line from status file: {log_text}")
    sys.stderr.write(str(e) + "\n")
    return state

  #print(str(log_entry))
  return state

def draw_loop(conf):
  # Load a font
  font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 7)
  font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

  disp = setup_display()

  # Create blank image for drawing.
  # Make sure to create image with mode '1' for 1-bit color.
  width = disp.width
  height = disp.height


  # Set up a canvas to draw on
  image = Image.new("1", (width, height))
  draw = ImageDraw.Draw(image)


  state = {
    "progress": 0,
    "found": 0,
    "current_device": "",
    "message": "Starting up"
  }

  for txt in try_read_line(conf.status_file):
    if txt is not None:
      state = update_state(state, txt)
      continue

    draw_state(state, draw, font_small, font_large, width, height)

    # Display image.
    disp.image(image)
    disp.show()

    time.sleep(0.1)


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument("--status-file", "-f", type=str, required=True,
                      help="Status file being written by a MacDongler instance. If it does not exist, it will be created.")

  conf = parser.parse_args()

  # Create the file if it doesn't exist yet
  if not os.path.isfile(conf.status_file):
    open(conf.status_file, "w+")

  draw_loop(conf)


if __name__ == "__main__":
  sys.exit(main())

