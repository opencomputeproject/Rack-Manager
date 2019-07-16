#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

## Variables---------------------##

## Declare eMMC device name here
EMMC_DRIVE="/dev/mmcblk0"
PACKAGE_STORE="/dev/mmcblk0p2"
FWUP_TEMPDIR="/tmp/~ocsfwup/"
PKG_STOREMNT=$FWUP_TEMPDIR"pkgstore/"
UPGRADEPKG_DIR=$FWUP_TEMPDIR"upfiles/"

## Image files
PKGFILE_UBOOT="u-boot.bin"
PKGFILE_KERNEL="zImage.bin"
PKGFILE_DEVICETREE="am437x-msocs.dtb"
PKGFILE_ROOTFS="rootfs.jffs2"
PKGFILE_MANIFEST="pkg.manifest"
PKGFILE_FWUP="fwupgrade.sh"
PKGFILE_FTBIN="zImage-initflasher.bin"

## Package store
PKGMNT_UPGRADE=$PKG_STOREMNT"upgrade/"
FWUP_CONFIG=$PKG_STOREMNT"fwup.config"
FWUP_BACKUP=$PKG_STOREMNT"backup/"

## Error Codes
ERR_SUCCESS=0
ERR_FAILED=1
ERR_NO_MOUNT=2
ERR_MISSINGFILE=3
ERR_BADPACKAGE=4

## Functions --------------------##
function check_pkg() {
	## Check if all needed files are present and valid
	PKGFILES="$PKGFILE_MANIFEST
	$PKGFILE_UBOOT
	$PKGFILE_KERNEL
	$PKGFILE_DEVICETREE
	$PKGFILE_ROOTFS
	$PKGFILE_FWUP
	$PKGFILE_FTBIN"

	workdir=$(pwd)
	cd $1
	for file in $PKGFILES
	do
		#echo Checking file "$1$file"
		if [ ! -f $file ]; then
			if [ $file != $PKGFILE_FWUP ] && [ $file != $PKGFILE_FTBIN ]; then
				echo ERROR: Missing file "$file" in package
				cd $workdir
				return $ERR_MISSINGFILE
			fi
		elif [ "$file" != "$PKGFILE_MANIFEST" ]; then
			chk_md5=$(cat "$PKGFILE_MANIFEST" | grep "$file")
			file_md5=$(md5sum "$file")
			if [ "$file_md5" != "$chk_md5" ]; then
				echo ERROR: Integrity check failed for "$file"
				return $ERR_BADPACKAGE
			fi
		fi
	done
	cd $workdir
	return $ERR_SUCCESS
}

function mount_pkgstore() {
	STARTTIME=$(date +%s)

	#fsck.vfat -a $PACKAGE_STORE	
	mkdir -p $PKG_STOREMNT
	
	mount -t vfat $PACKAGE_STORE $PKG_STOREMNT
	retval=$?
	if  [ "$retval" != 0 ];
	then
		echo Problem mounting package store: $retval
	fi
	return $retval
}

function finish_upgrade() {
	sync
	umount $PKG_STOREMNT
	sync
	exit "$1"
}

## Top level --------------------##
echo "The device will reboot automatically once the update is initialized..."

if [ "$1" = "recovery" ]; then
	recovery_type="$2"
	## Mount package store	from EMMC
	mount_pkgstore
	retval=$?
	if  [ "$retval" = "$ERR_SUCCESS" ] && [ -f $FWUP_CONFIG ]; then
		sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME="$recovery_type'/' $FWUP_CONFIG
		sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS=0"'/' $FWUP_CONFIG
		sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=pending"'/' $FWUP_CONFIG
		## fwupinstid=$(($(grep "UPGRADE_INST" $FWUP_CONFIG | awk '{FS="=";$0=$0;print $2}')+1))
		## sed -i 's/^UPGRADE_INST.*/'"UPGRADE_INST="$fwupinstid'/' $FWUP_CONFIG
	else
		echo ERROR: EMMC is not setup for firmware upgrade, run factory restore from UBoot to fix
		finish_upgrade $ERR_FAILED
	fi
else
	## Extract tar file
	upgrade_pkg_file="$2"
	mkdir -p $UPGRADEPKG_DIR
	tar -xf $upgrade_pkg_file -C $UPGRADEPKG_DIR

	## Check new upgrade package tar file
	check_pkg $UPGRADEPKG_DIR
	retval=$?
	if  [ "$retval" != "$ERR_SUCCESS" ]; then
		finish_upgrade $retval
	fi

	## Mount package store	from EMMC
	mount_pkgstore
	retval=$?
	if  [ "$retval" = "$ERR_SUCCESS" ] && [ -f $FWUP_CONFIG ]; then
		## Publish package files for upgrade
		mkdir -p $PKGMNT_UPGRADE
		if [ -f $UPGRADEPKG_DIR$PKGFILE_FTBIN ]; then
			mv -f $UPGRADEPKG_DIR$PKGFILE_FTBIN $FWUP_TEMPDIR$PKGFILE_FTBIN
		fi
		cp -f $UPGRADEPKG_DIR* $PKGMNT_UPGRADE
	
		sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME=upgrade"'/' $FWUP_CONFIG
		sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS=0"'/' $FWUP_CONFIG
		sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=pending"'/' $FWUP_CONFIG
		## fwupinstid=$(($(grep "UPGRADE_INST" $FWUP_CONFIG | awk '{FS="=";$0=$0;print $2}')+1))
		## sed -i 's/^UPGRADE_INST.*/'"UPGRADE_INST="$fwupinstid'/' $FWUP_CONFIG

		rm -rf $FWUP_BACKUP
	else
		echo ERROR: EMMC is not setup for firmware upgrade, run factory restore from Uboot to fix
		finish_upgrade $ERR_FAILED
	fi
fi

## Wrap up
finish_upgrade $ERR_SUCCESS
