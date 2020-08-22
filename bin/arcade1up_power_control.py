#!/usr/bin/python3
import sys
import signal
import time
from subprocess import call
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    sys.exit(1)

#
# Config Section
#

# the GPIO pins we connect the switch headers to
GPIO_POWER = 5 # red, black to 4 (GND)


BOUNCEBACK=150 #ms - no bounceback detected during switch/slider testing, but just in case
POWER_BOUNCEBACK=BOUNCEBACK # use default bounceback

#
# End of Config Section
#

DEBUG = False
def debug(str):
    if DEBUG:
        print(str)

def setup_gpio():
    # Useful reference https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
    GPIO.setmode(GPIO.BOARD)

#
# Power Control
#
def _power_callback(channel):
    # Power state GPIO[5]
    # Off: [1]
    # On:  [0]
    debug("Channel " + str(channel) + ": " + str(GPIO.input(channel)))
    if GPIO.input(GPIO_POWER):
        print("Power OFF")
        call(['poweroff'])
    else:
        print("Power ON")
        # let the hardware system power itself on - this case is when the Pi is already running,
        # but the power switch was Off and has moved to On - ie. nothing to see here, move along please

def setup_power_control():
    # setup power button pin(s)
    GPIO.setup(GPIO_POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # register for power switch changes
    GPIO.add_event_detect(GPIO_POWER, GPIO.BOTH, callback=_power_callback, bouncetime=POWER_BOUNCEBACK)

def _on_exit(a, b):
    print("Exiting...")
    GPIO.cleanup()
    sys.exit(0)

# test mode to check GPIO import and initial mode setting, exit quickly and cleanly if they are OK
test_mode = '--test-only' in sys.argv
if test_mode:
    debug("Test-only mode - will exit after quick GPIO setup test")

setup_gpio()

if test_mode:
    debug("Test OK")
    sys.exit(0)

setup_power_control()

# register for interrupt signal
signal.signal(signal.SIGINT, _on_exit)

# wait for GPIO or signal events
while True:
    time.sleep(1e6)
