#!/bin/bash
# Script to install the Arcade1Up control software as a system service
# Install Python3/GPIO
echo "Checking for missing packages"
PACKAGES=python3-rpi.gpio
MISSING=$(dpkg --get-selections $PACKAGES 2>&1 | grep -v 'install$' | awk '{ print $6 }')
[[ ! -z $MISSING ]] && apt-get --yes install $MISSING

DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Testing packages and control script"
python3 ${DIRNAME}/bin/arcade1up_control.py --test-only || ( echo "Setup failed - error testing control script"; exit 1 )

# Copy service file to /etc/systemd/system/
echo "Copying systemd service file"
cp ${DIRNAME}/arcade1up_control.service /etc/systemd/system/arcade1up_control.service
chmod -x /etc/systemd/system/arcade1up_control.service
chmod +r /etc/systemd/system/arcade1up_control.service

# Enable and start the service
echo "Enabling and starting arcade1up_control service"
systemctl enable arcade1up_control.service
systemctl restart arcade1up_control.service

echo $'Done, usage:\n  sudo systemctl [start|stop] arcade1up_control'