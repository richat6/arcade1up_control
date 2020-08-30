# Arcade1Up Control
Use Arcade1Up cabinet's built in power and volume switches and sliders to control the power and volume of a RaspberryPi.

Installs a systemd service that runs a Python3 script that listens for changes to the power switch or volume slider positions, responding appropriately.

Power is controlled (off) using system shutdown. Power on is controlled using GPIO power triggered pins 5 & 6. Power only controls the RaspberryPi - other devices will need to be be controlled separately.

Volume is controlled using the amixer command for the "PCM" mixer, toggling between mute (off), 60% (medium), 75% (high). These are configurable in the arcade1up_control.py script

## Setup
### Prerequisites
* RaspberryPi running Raspbian Jesse at least. Tested (only) with 3B.
* Arcade1Up cabinet with switches disconnected from the control board and conencted to RaspberryPI GPIO headers

### Hardware
* Connect power switch black end to GPIO pin 5, red end to pin 6.
* Connect volume slider brown end to GPIO pin 12, red to pin 14, black end to pin 16.

### Software
```
git clone https://github.com/richat6/arcade1up_control.git
sudo arcade1up_control/install.sh
```

### Config

After any config changes made in arcade1up_power_control.py or arcade1up_power_control.py, restart the service:

```
sudo systemctl restart arcade1up_power_control
sudo systemctl restart arcade1up_volume_control
```

### Logs

systemd logs are found in /var/log/daemon.log. To watch the script in action:

```
tail -f /var/log/daemon.log
```

### Acknowlegements

Initially based on dmanlfc's work:

https://github.com/dmanlfc/arcade1up/tree/master/Raspberry%20Pi

