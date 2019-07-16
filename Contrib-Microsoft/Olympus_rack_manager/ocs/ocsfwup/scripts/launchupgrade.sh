#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

FWUP_LOGFILE="/tmp/fwup.log"
PKGNAMEVAR=$(cat /proc/cmdline | awk '{print $5}' | awk '{FS="=";$0=$0;print $1}')
UPGRADEPKG=$(cat /proc/cmdline | awk '{print $5}' | awk '{FS="=";$0=$0;print $2}')

EMMC_DRIVE="/dev/mmcblk0"
PACKAGE_STORE="/dev/mmcblk0p2"
FWUP_TEMPDIR="/tmp/~ocsfwup"
PKG_STOREMNT=$FWUP_TEMPDIR"/pkgstore/"

if  [ ! "$PKGNAMEVAR"  ] || [ "$PKGNAMEVAR" != "fwup" ] || [ ! "$UPGRADEPKG" ]; then
	UPGRADEPKG="emmcprov"
fi

UserInput="debug"
while [[ "$UserInput" = "debug" ]]; do
	read -t 5 -p "Launching upgrade..." UserInput
	if [[ "$UserInput" = "debug" ]]; then
		echo PKGNAMEVAR=$PKGNAMEVAR
		echo UPGRADEPKG=$UPGRADEPKG
		/bin/sh
	fi
done

echo " "
echo "Firmware upgrade or recovery in progress.. the board should reboot in less than 10 minutes."
echo "Progress and status info are logged and will be available in package store after reboot."
echo " "

if  [ $UPGRADEPKG = "upgrade" ] || [ $UPGRADEPKG = "active" ] || [ $UPGRADEPKG = "rollback" ]; then
	## Mount package store	from EMMC
	fsck.vfat -a $PACKAGE_STORE	
	mkdir -p $PKG_STOREMNT
	mount -t vfat $PACKAGE_STORE $PKG_STOREMNT
	retval=$?
	if  [ "$retval" = "0" ] && [ -f $PKG_STOREMNT$UPGRADEPKG/fwupgrade.sh ];
	then
		echo Launching upgrade from package: $UPGRADEPKG...
		cp $PKG_STOREMNT$UPGRADEPKG/fwupgrade.sh /etc/fwupgrade.sh
	fi
	/etc/fwupgrade.sh $UPGRADEPKG > $FWUP_LOGFILE
else
	/etc/factorysetup.sh $UPGRADEPKG > $FWUP_LOGFILE
fi
