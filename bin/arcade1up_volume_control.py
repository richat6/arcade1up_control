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
AMIXER_MIXER = 'Headphone'
# medium volume level
AMIXER_VOLUME_MEDIUM = '65%'
# high volume level
AMIXER_VOLUME_HIGH = '80%'

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

def amixer(mixer, volume_level):
    call_args = []
    if volume_level is None:
        # mute
        call_args = ['amixer', 'set', mixer, 'mute']
    else:
        call_args = ['amixer', 'set', mixer, volume_level, 'unmute']
    if debug:
        print(' '.join(call_args))
    call(call_args)

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
    debug("BROWN: " + str(volume_brown) + ", BLACK: " + str(volume_black))
    if volume_brown and volume_black:
        print("Set Volume: MUTE")
        amixer(AMIXER_MIXER)
    elif volume_brown:
        print("Set Volume: MEDIUM (" + AMIXER_VOLUME_MEDIUM + ")")
        amixer(AMIXER_MIXER, AMIXER_VOLUME_MEDIUM)
    else:
        print("Set Volume: HIGH(" + AMIXER_VOLUME_HIGH + ")")
        amixer(AMIXER_MIXER, AMIXER_VOLUME_HIGH)

def _volume_callback(channel):
    debug("Channel " + str(channel) + ": " + str(GPIO.input(channel)))
    set_volume_from_gpio()

def setup_volume_control():
    # setup volume slider pins
    GPIO.setup(GPIO_VOLUME_BROWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_VOLUME_BLACK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # in case the volume slider has moved sinced last run, initialise volume to current slider
    debug("Initialising volume...")
    set_volume_from_gpio()

    # register for volume slider changes
    GPIO.add_event_detect(GPIO_VOLUME_BROWN, GPIO.BOTH, callback=_volume_callback, bouncetime=VOLUME_BOUNCEBACK)
    GPIO.add_event_detect(GPIO_VOLUME_BLACK, GPIO.BOTH, callback=_volume_callback, bouncetime=VOLUME_BOUNCEBACK)

def _on_exit(a, b):
    print("Exiting...")
    GPIO.cleanup()
    sys.exit(0)

debug("DEBUG = True")

# test mode to check GPIO import and initial mode setting, exit quickly and cleanly if they are OK
test_mode = '--test-only' in sys.argv
if test_mode:
    debug("Test-only mode - will exit after quick GPIO setup test")

setup_gpio()

if test_mode:
    debug("Test OK")
    sys.exit(0)

setup_volume_control() # needs to run as same user as EmulationStation (pi)

# register for interrupt signal
signal.signal(signal.SIGINT, _on_exit)

# wait for GPIO or signal events
while True:
    time.sleep(1e6)
