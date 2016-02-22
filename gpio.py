#!/usr/bin/env python

# 2016-02-17 J Cummings (cummingsj@gmail.com)

# Some of this is reused from the pigpio examples
# Other parts are unique garbage that I wrote - J

import cgi
import subprocess
import pigpio
import time

# Define some of the values we will be using
sleep_time = 1.5 # How long to sleep for a power cycle command
# This var is critical, you need a "device":GPIO mapping for every
# GPIO controlled relay and the controlled device that you are using
relay_pins = { "repeater":18, "pi":23, "master":24, "extra":25 }

print("Content-type:text/html\r\n\r\n")

print("""<html><head><title>POWGPIO Control</title><link rel="stylesheet" href="style1.css"></head><body>""")

### DO NOT MODIFY ANYTHING BELOW HERE UNLESS YOU KNOW WHAT YOU ARE DOING ###

form = cgi.FieldStorage(keep_blank_values=True)

if "action" in form:
   action = form["action"].value
else:
   action = ""

lvl = [0]*4

# These are backwards to account for the fact that we are using either the NC side of the relay
# and/or the fact that we will be controlling the NC side of a larger relay
lvlstr = ["Off", "On"]

pigpio.exceptions = False # Get error code returned, not exceptions.

pi=pigpio.pi()

# Conditionals to handle our form input for power on/off/reboot command
try:

   command = ""

   err = 0

   if "gpio" in form:
      gpio = int(form["gpio"].value)
   else:
      gpio = -1

   if action == "Off":

      err = pi.write(gpio, 0) # Set GPIO to OUT, HIGH

      command = "Off {}".format(gpio)

   if action == "On":

      err = pi.write(gpio, 1) # Set GPIO to OUT, LOW

      command = "On {}".format(gpio)

   if action == "Reboot": # Cycle to High then Low to power cycle with a 1.5 second delay

      err = pi.write(gpio, 0)
      time.sleep(sleep_time)
      err = pi.write(gpio, 1)

      command = "Reboot {}".format(gpio)

except:
   pass

print('<table><tr><th>Device</th><th>State</th></tr>')

# Read state values for our pins and print them in a human readable way
# Using shiny colors
for relay_pin, board_pin in relay_pins.iteritems():
   lvl = pi.read(board_pin)
   if lvl == 1:
      div = '<div style="background-color:#00CC66">'
   else:
      div = '<div style="background-color:#F62817">'
   print("<tr><td>{}{}</div></td><td>{}{}</div></td></tr>".format(div, relay_pin, div, lvlstr[lvl]))
print("</table>")

pi.stop()

print("""<table><tr><th>Device</th><th>Action</th></tr><form method="post" action="gpio.py">
<tr><td><select name = "gpio">
""")

# Build the radio options from our device mapping list
for relay_pin, board_pin in relay_pins.iteritems():
   print("""   <option value="{}">{}</option>""".format(board_pin, relay_pin))

print("""</select></td><td>
<select name="action">
   <option value="On">On</option>
   <option value="Off">Off</option>
   <option value="Reboot">Reboot</option>
</select>
</td></tr><tr><td colspan="2"><br>
<input class="button" type="submit" value="Execute">
<br>
<br>
</form>
</td></tr>
""")

print("""<tr><td colspan="2">
<form method="post" action="gpio.py"><br>
<input class="button" type="submit" value="Refresh" name="action">
<br>
</td></tr></form></table>""")

if err < 0:
   command = command + ' <span style="color:red">(Error: {})</span>'.format(pigpio.error_text(err))

if command != "":
   print("<br>Last command: " + command)

print("</body></html>")