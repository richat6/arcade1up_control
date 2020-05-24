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
GPIO_VOLUME_BROWN = 12 # brown to 12, red to 14 (GND)
GPIO_VOLUME_BLACK = 16 # black to 16

# which mixer to control
AMIXER_MIXER = "PCM"
# medium volume level
AMIXER_VOLUME_MEDIUM = "60%"
# high volume level
AMIXER_VOLUME_HIGH = "75%"

BOUNCEBACK=150 #ms - no bounceback detected during switch/slider testing, but just in case
POWER_BOUNCEBACK=BOUNCEBACK # use default bounceback
VOLUME_BOUNCEBACK=BOUNCEBACK # use default bounceback

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
        call(["poweroff"])
    else:
        print("Power ON")
        # let the hardware system power itself on - this case is when the Pi is already running,
        # but the power switch was Off and has moved to On - ie. nothing to see here, move along please

def setup_power_control():
    # setup power button pin(s)
    GPIO.setup(GPIO_POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # register for power switch changes
    GPIO.add_event_detect(GPIO_POWER, GPIO.BOTH, callback=_power_callback, bouncetime=POWER_BOUNCEBACK)

#
# Volume Control
#
def set_volume_from_gpio():
    # Volume state GPIO[brown black]:
    # 0/Mute: [1 1]
    # Medium: [1 0]
    # High:   [0 0]
    volume_brown = GPIO.input(GPIO_VOLUME_BROWN)
    volume_black = GPIO.input(GPIO_VOLUME_BLACK)
    if volume_brown and volume_black:
        print("Set Volume: MUTE")
        call(["amixer", "set", AMIXER_MIXER, "mute"])
    elif volume_brown:
        print("Set Volume: MEDIUM")
        call(["amixer", "set", AMIXER_MIXER, "unmute"])
        call(["amixer", "set", AMIXER_MIXER, AMIXER_VOLUME_MEDIUM])
    else:
        print("Set Volume: HIGH")
        call(["amixer", "set", AMIXER_MIXER, "unmute"])
        call(["amixer", "set", AMIXER_MIXER, AMIXER_VOLUME_HIGH])

def _volume_callback(channel):
    debug("Channel " + str(channel) + ": " + str(GPIO.input(channel)))
    set_volume_from_gpio()

def setup_volume_control():
    # setup volume slider pins
    GPIO.setup(GPIO_VOLUME_BROWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_VOLUME_BLACK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # in case the volume slider has moved sinced last run, initialise volume to current slider
    set_volume_from_gpio()

    # register for volume slider changes
    GPIO.add_event_detect(GPIO_VOLUME_BROWN, GPIO.BOTH, callback=_volume_callback, bouncetime=VOLUME_BOUNCEBACK)
    GPIO.add_event_detect(GPIO_VOLUME_BLACK, GPIO.BOTH, callback=_volume_callback, bouncetime=VOLUME_BOUNCEBACK)

def _on_exit(a, b):
    print("Exiting...")
    GPIO.cleanup()
    sys.exit(0)

# test mode to check GPIO import and initial mode setting, exit quickly and cleanly if they are OK
test_mode = "--test-only" in sys.argv
if test_mode:
    debug("Test-only mode - will exit after quick GPIO setup test")

setup_gpio()

if test_mode:
    debug("Test OK")
    sys.exit(0)

setup_power_control()
setup_volume_control()

# register for interrupt signal
signal.signal(signal.SIGINT, _on_exit)

# wait for GPIO or signal events
while True:
    time.sleep(1e6)