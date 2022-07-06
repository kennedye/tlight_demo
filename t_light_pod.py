#!/usr/bin/env python3

# simple script to demonstrate running a Python script
# that uses the GPIO pins on a Raspberry Pi
# which is part of a k3s cluster
#
# this assumes several things:
# - you already have a kubernetes cluster of Pis
# - the script is packaged into an accessible container (don't forget to make it ARM-compatible)
# - whichever Pi node you're running the pod on has one of these plugged into it:
#   https://lowvoltagelabs.com/products/pi-traffic/

import time
import os
try:
    import RPi.GPIO as GPIO
except ImportError:
    exit('unable to load RPi.GPIO library')

# do the usual GPIO setup stuff
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# read environment variables to determine which ins to use for which colors -
# depending on where you plug it in, the traffic light module will either use
# pins 13, 19, and 26 or pins 9, 10, and 11 for the lights; this way, it can
# be configured for either from the pod spec itself
red = os.environ.get('GPIO_RED')
yellow = os.environ.get('GPIO_YELLOW')
green = os.environ.get('GPIO_GREEN')

# activate the pins for output
chan_list = (red,yellow,green)
GPIO.setup(chan_list, GPIO.OUT)

# the main loop, basically just a cycle through all three colors with a one second
# delay between them - a preStop command in the pod spec will allow the script to
# hit the finally clause and run GPIO.cleanup() upon pod termination
try:
    while True:
        GPIO.output(red, True)
        time.sleep(1)
        GPIO.output(red, False)
        GPIO.output(yellow, True)
        time.sleep(1)
        GPIO.output(yellow, False)
        GPIO.output(green, True)
        time.sleep(1)
        GPIO.output(green, False)
except KeyboardInterrupt:
    exit()
finally:
    GPIO.cleanup()