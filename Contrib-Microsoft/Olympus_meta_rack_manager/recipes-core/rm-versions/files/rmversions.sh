#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

PKG_FILE=/etc/pkg-info
PRU_FILE=/usr/bin/ocs-pru

echo " "
echo "--------------------------------------------------------"
echo "  Microsoft OCS Rack Manager software version summary"
echo " "
if [ -f $PKG_FILE ];
then
	echo "  Package version    :" $(cat /etc/pkg-info | awk '{FS="_";$0=$0;print $4}')
	echo " "
	echo "  Rootfs version     :" $(cat /etc/rfs-info | awk '{FS="_";$0=$0;print $4}')
	echo "  U-Boot version     :" $(cat /proc/cmdline | awk '{print $4}' | awk '{FS="_";$0=$0;print $4}')
	echo "  Kernel version     :" $(cat /proc/sys/kernel/osrelease | awk {'FS="-";$0=$0;print $2}' | awk '{FS="_";$0=$0;print $4}')
	echo "  Devicetree version :" $(cat /proc/device-tree/model | awk '{FS="_";$0=$0;print $4}')
	echo " "
	if [ -f $PRU_FILE ]; then
		echo "  PRU FW version     :" $(/usr/bin/ocs-pru GetPruVersion | grep "Firmware version:"  | awk '{print $3}')
	fi
else
   echo "  Kernel build time   :" $(sed 's/#1 PREEMPT //' /proc/sys/kernel/version)
fi
echo " "
echo "--------------------------------------------------------"
echo " "