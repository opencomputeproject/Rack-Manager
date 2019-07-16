#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.


PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin

echo "----------------------------------------------------------"
echo "|    Microsoft OCS Rack Manager board init script v1.2   |"
echo "----------------------------------------------------------"

echo "Setting permissions for rpmsg dev file.."
chmod 666 /dev/rpmsg_pru31
echo "Setting permissions for rpmsg dev file. Done."

echo "Creating ocs-persist if not exist in emmc"
if [ ! -f /usr/srvroot/ocs-persist.txt ]; then
    cp /var/local/ocs-persist.txt /usr/srvroot/
fi
echo "Done creating ocs-persist"

echo "Starting network interfaces..."
PYTHONPATH=/usr/lib/commonapi python /usr/lib/commonapi/controls/manage_network.py -u eth0
PYTHONPATH=/usr/lib/commonapi python /usr/lib/commonapi/controls/manage_network.py -u eth1
echo "Done."

echo "Starting runtimewatchdog daemon.. "
/usr/bin/runtimewatchdog

echo "Starting GPIO export.. "
/usr/bin/ocs-gpio setupgpio /lib/modules/$(uname -r)/extra/gpio-mon.ko &

echo "Initializing PMIC.. "
/usr/bin/ocs-pmic initialize
/usr/bin/ocs-pmic setfseal
echo "Initializing PMIC done.. "

echo "Initializing HDC Sensor.. "
/usr/bin/ocs-hdc initialize
echo "Initializing HDC Sensor done.. "

echo "Clear faults on HSC Sensor.. "
/usr/bin/ocs-hsc clearfaults
echo "Clear faults on HSC Sensor done.. "

echo "ADC Calibration.. "
/usr/bin/ocs-adccalibration -c
echo "ADC Calibration done.. "

echo "PRU persist config replay.."
/usr/bin/ocs-pru replaypersistconfig
echo "PRU persist config replay done."

echo " "
RM_MODE=$(ocs-gpio getmode | grep "ID value" | awk '{print $4}')
if [ "$RM_MODE" = "0" ]; then
	echo "Rack manager is operating in WCS configuration"
elif [ "$RM_MODE" = "1" ]; then
	echo "Rack manager is operating in Row Manager / Non WCS configuration"
else
	echo "Rack manager is operating in manufacturing mode"
fi
echo " "
## No global bypass - only used by Row Manager PIB, but ok to set default in RM
/usr/bin/ocs-gpio throttlebypass off 0
## No local bypass
/usr/bin/ocs-gpio throttlebypass off 1
## Enable throttle output
/usr/bin/ocs-gpio throttlecontrol on 0
if [ "$RM_MODE" = "1" ]; then
	## Enable throttle output on Row Mgr PIB
	/usr/bin/ocs-gpio throttlecontrol on 1	
fi

echo "Starting Telemetry Daemon.. "
/usr/bin/ocstelemetry_daemon &
echo "OcsTelemetry Daemon Started.. "

echo "Starting RM service"
# Start Rack manager service
cd /usr/bin/rackmanager
if [ -e "firstboot" ]; then
	python RackManager.py compile
	rm -f firstboot
fi

python RackManager.py >/usr/srvroot/ocsrest.log 2>&1 &
echo "RM service started"

echo "Starting legacy compatibility service"
python RackManager.py legacy >/usr/srvroot/legacyrest.log 2>&1 &
echo "Legacy compatibility service started"

## Enable all port buffer
/usr/bin/ocs-gpio portbuffer on
echo "Port and throttle signals now initialized. FW Ready signalled."

echo " "
/etc/rmversions.sh
echo " "
