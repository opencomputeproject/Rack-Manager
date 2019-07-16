#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

## Variables---------------------##
## System settings
MAX_UPGRADE_ATTEMPTS=2
FLASH_ERASE_BLOCKSIZE=65536

EMMC_DRIVE="/dev/mmcblk0"
PACKAGE_STORE="/dev/mmcblk0p2"
PERSIST_PART="/dev/mmcblk0p3"

QSPI_UBOOTPRI="/dev/mtd0"
QSPI_UBOOTBAK="/dev/mtd1"
QSPI_UBOOTENV="/dev/mtd2"
QSPI_ROOTFS="/dev/mtdblock5"

FWUP_TEMPDIR="/tmp/~ocsfwup"
FWUP_ROOTFSMNT=$FWUP_TEMPDIR"/rootfs/"
FWUP_PERSISTMNT=$FWUP_TEMPDIR"/srvroot/"

## Error Codes
ERR_SUCCESS=0
ERR_FAILED=1
ERR_NO_MOUNT=2
ERR_MISSINGFILE=3
ERR_BADPACKAGE=4
ERR_ERASEFAIL=5
ERR_FLASHCOPYFAIL=6
ERR_NOFILESIZE=7
ERR_MISSINGUSERDATA=8

## Image files in package
PKGFILE_UBOOT="u-boot.bin"
PKGFILE_KERNEL="zImage.bin"
PKGFILE_DEVICETREE="am437x-msocs.dtb"
PKGFILE_ROOTFS="rootfs.jffs2"
PKGFILE_MANIFEST="pkg.manifest"
PKGFILE_ENV="env.bin"

PKGFILES="$PKGFILE_MANIFEST
$PKGFILE_UBOOT
$PKGFILE_KERNEL
$PKGFILE_DEVICETREE
$PKGFILE_ROOTFS"

## Package store related
PKGNAME_FACTORY="factory"
PKGNAME_ROLLBACK="rollback"
PKGNAME_ACTIVE="active"
PKGNAME_UPGRADE="upgrade"

PKG_STOREMNT=$FWUP_TEMPDIR"/pkgstore/"
FWUP_CONFIG=$PKG_STOREMNT"fwup.config"
FWUP_BACKUP=$PKG_STOREMNT"backup/"
FWUP_LOGFILE="/tmp/fwup.log"
FWUP_LOGPERSIST=$PKG_STOREMNT"fwup.log"
FWUP_LOGPERSISTPUB=$FWUP_PERSISTMNT"shared/ocsfwup.log"

## User data files
USRDATAFILES="etc/shadow
etc/passwd
etc/group
etc/network/interfaces
etc/hostname
etc/ntp.conf"
USRDATAPERMS=(400 644 644 644 644 644)

G_UBOOTSKIP=$ERR_SUCCESS

## Functions --------------------##
function publish_log() {
	## Mount package store	from EMMC
	mkdir -p $FWUP_PERSISTMNT
	mount $PERSIST_PART $FWUP_PERSISTMNT
	retval=$?
	if  [ "$retval" != 0 ];
	then
		echo Problem mounting emmc partition to copy logs: $retval
		return $ERR_FAILED
	fi
	
	cp $FWUP_LOGPERSIST $FWUP_LOGPERSISTPUB
	sync
	
	umount $FWUP_PERSISTMNT
}

function check_uboot_skip() {
	chk_md5=$1
	chk_sz=$2
	curdir=$(pwd)
	cd $FWUP_TEMPDIR
	## echo ...saving UBoot from $QSPI_UBOOTPRI into $ubootfile
	dd if=$QSPI_UBOOTPRI of=$PKGFILE_UBOOT bs=1 count=$chk_sz
	retval=$?
	if  [ "$retval" != 0 ]; then
		echo WARNING: Failed to get data from UBoot partition
		cd $curdir
		return $ERR_FAILED
	fi
	file_md5=$(md5sum "$PKGFILE_UBOOT")
	if [ "$file_md5" != "$chk_md5" ]; then	
		cd $curdir
		return $ERR_FAILED
	fi
	cd $curdir
	return $ERR_SUCCESS
}

function check_pkg() {
	## Check if all needed files are present and valid
	workdir=$(pwd)
	
	if [ -d $PKG_STOREMNT$1 ]; then
		cd $PKG_STOREMNT$1
	else
		return $ERR_BADPACKAGE
	fi
	
	for file in $PKGFILES
	do
		#echo Checking file "$1$file"
		if [ ! -f $file ]; then
			echo ERROR: Missing file "$file" in package
			cd $workdir
			return $ERR_MISSINGFILE
		fi
		if [ "$file" != "$PKGFILE_MANIFEST" ]; then
			chk_md5=$(cat "$PKGFILE_MANIFEST" | grep "$file")
			file_md5=$(md5sum "$file")
			if [ "$file_md5" != "$chk_md5" ]; then
				echo ERROR: Integrity check failed for "$file"
				return $ERR_BADPACKAGE
			elif [ "$file" = "$PKGFILE_UBOOT" ]; then
				check_uboot_skip "$chk_md5" "$(stat -c %s "$file")"
				G_UBOOTSKIP=$?
			fi
		fi
	done
	cd $workdir
	return $ERR_SUCCESS
}

function usrdata_action() {
	actionstatus=$ERR_SUCCESS
	FILEID=0

	mkdir -p $FWUP_ROOTFSMNT
	mount -t jffs2 $QSPI_ROOTFS $FWUP_ROOTFSMNT
	retval=$?
	if  [ "$retval" != 0 ];
	then
		echo ERROR: Cannot mount rootfs for user data backup: $retval
		return $retval
	fi
	
	for file in $USRDATAFILES
	do
		filetocopy=$FWUP_ROOTFSMNT$file
		#echo ..Attempting to backup file $filetocopy
		if  [ "$1" = "backup" ]; then
			if [ -f $filetocopy ]; then
				cp -pf $filetocopy $FWUP_BACKUP"usrdata$FILEID"
				sync
			else 
				echo WARNING: Missing user data file $filetocopy
				actionstatus=$ERR_MISSINGUSERDATA
			fi
		else
			if [ -f $FWUP_BACKUP"usrdata$FILEID" ]; then
				cp -pf $FWUP_BACKUP"usrdata$FILEID" $filetocopy
				sync
				chmod ${USRDATAPERMS[FILEID]} $filetocopy
				sync
				#echo ..Permissions for file $filetocopy set to ${USRDATAPERMS[FILEID]}
			else 
				echo WARNING: Missing user data file $file in backup
				actionstatus=$ERR_MISSINGUSERDATA
			fi
		fi
		FILEID=$(($FILEID+1))
	done

	sync
	umount $FWUP_ROOTFSMNT	
	return $actionstatus
}

function program_flash() {
	#Perform programming in the reverse order to ensure U-boot is written last
	FLASHFILES="$PKGFILE_ROOTFS
	$PKGFILE_KERNEL
	$PKGFILE_DEVICETREE
	$PKGFILE_ENV	
	$PKGFILE_UBOOT
	$PKGFILE_UBOOT"

	#Wipe out QSPI environment first
	flash_erase -q $QSPI_UBOOTENV 0 0	
	
	PARTID=5
	for file in $FLASHFILES
	do
		filetowrite=$PKG_STOREMNT$1"/"$file
		echo ...writing $filetowrite to /dev/mtd$PARTID
		if [ -f $filetowrite ]; then
			flashcp $filetowrite /dev/mtd$PARTID
			retval=$?
			if  [ "$retval" != 0 ];
			then
				echo ERROR: Flash copy failed for $file
				return $ERR_FLASHCOPYFAIL
			else
				echo ...Success
			fi
		fi
		PARTID=$(($PARTID-1))
		if [ $PARTID = 0 ] && [ "$G_UBOOTSKIP" = "$ERR_SUCCESS" ]; then
			return $ERR_SUCCESS
		fi
	done
	return $ERR_SUCCESS
}

function replace_package() {
	sync
	if  [ "$1" = $PKGNAME_UPGRADE ]; then
		rm -rf $PKG_STOREMNT$PKGNAME_ROLLBACK
		retval=$?
		if  [ "$retval" != 0 ]; then		
			echo WARNING: Failed to remove outdated rollback package, code 1
		fi
		sync
		mv $PKG_STOREMNT$PKGNAME_ACTIVE $PKG_STOREMNT$PKGNAME_ROLLBACK
		retval=$?
		if  [ "$retval" != 0 ]; then		
			echo ERROR: Replace packages for $1 failed, code 2
			return $ERR_COPYFAIL
		fi
		sync
		mv $PKG_STOREMNT$1 $PKG_STOREMNT$PKGNAME_ACTIVE
		retval=$?
		if  [ "$retval" != 0 ]; then		
			echo ERROR: Replace packages for $1 failed, code 3
			return $ERR_COPYFAIL
		fi
		sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME="$PKGNAME_ACTIVE'/' $FWUP_CONFIG
		sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS=0"'/' $FWUP_CONFIG
	elif [ "$1" = $PKGNAME_ROLLBACK ]; then
		mv $PKG_STOREMNT$PKGNAME_ROLLBACK $PKG_STOREMNT$PKGNAME_ACTIVE
		retval=$?
		if  [ "$retval" != 0 ]; then		
			echo ERROR: Replace packages for $1 failed, code 4
			return $ERR_COPYFAIL
		fi
	fi
	sync
	return $ERR_SUCCESS	
}

function finish_up() {
	ENDTIME=$(date +%s)

	retval=$1
	sync
	if  [ "$retval" = "$ERR_SUCCESS" ];
	then
		echo Upgrade completed successfully in $(($ENDTIME-$STARTTIME)) seconds
		sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=complete"'/' $FWUP_CONFIG
		rm -rf $FWUP_BACKUP
	else
		echo Upgrade failed: $retval
		sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=failed"'/' $FWUP_CONFIG
		if [ "$UPGRADE_CANCELLABLE" = "true" ]; then
			rm -rf $FWUP_BACKUP
		fi	
	fi
	
	if [ -f $FWUP_LOGFILE ]; then
		cat $FWUP_LOGFILE >> $FWUP_LOGPERSIST
		publish_log
	fi

	cd ~/
	umount $PKG_STOREMNT
	sync

	echo " "
	echo " "
	echo " "
	reboot
	exit $retval	
}

function main_toplevel() {
	STARTTIME=$(date +%s)
	UPGRADE_CANCELLABLE="true"
	UPGRADEPKG=$1

	echo " "
	echo "--------------------------------------------------"
	echo " Microsoft OCS Rack Manager Firmware Upgrade v1.4 "
	echo " "
	echo "  Upgrade start local time: " $(date +"%D %T %z")
	echo "  Upgrader OS versions:"
	echo "  U-Boot     :" $(cat /proc/cmdline | awk '{print $4}' | awk '{FS="_";$0=$0;print $4}')
	echo "  Kernel     :" $(cat /proc/sys/kernel/osrelease | awk {'FS="-";$0=$0;print $2}' | awk '{FS="_";$0=$0;print $4}')
	echo "  Devicetree :" $(cat /proc/device-tree/model | awk '{FS="_";$0=$0;print $4}')
	echo " "
	echo "--------------------------------------------------"
	
	## Mount package store from EMMC as needed
	fsck.vfat -a $PACKAGE_STORE	
	retval=$(mount | grep $PACKAGE_STORE)
	if [ ! "$retval" ] || [ "$retval" = "" ]; then
		mkdir -p $PKG_STOREMNT
		mount -t vfat $PACKAGE_STORE $PKG_STOREMNT
		retval=$?
		if  [ "$retval" != 0 ];
		then
			echo Problem mounting package store: $retval
			finish_up $retval
		fi
	fi
	
	## Read config. If no upgrade pacakge is specified at UBoot, read in.
	if [ ! "$UPGRADEPKG" ] || [ "$UPGRADEPKG" = "" ]; then
		UPGRADEPKG=$(grep "PACKAGE_NAME" $FWUP_CONFIG | awk '{FS="=";$0=$0;print $2}')
	fi
	UPGRADEATTEMPTS=$(($(grep "UPGRADE_ATTEMPTS" $FWUP_CONFIG | awk '{FS="=";$0=$0;print $2}')+1))
	UPGRADESTATUS=$(grep "UPGRADE_STATUS" $FWUP_CONFIG | awk '{FS="=";$0=$0;print $2}')
	
	manifestfile=$PKG_STOREMNT$UPGRADEPKG/$PKGFILE_MANIFEST
	
	## Display config
	echo "--------------------------------------------------"
	echo " "
	echo "  Upgrade package type   :" $UPGRADEPKG
	if [ -f $manifestfile ]; then
		echo "  Upgrade package version:" $(cat $manifestfile | grep PACKAGE_VERSION |  awk '{print $3}')
	fi
	echo "  Upgrade status         :" $UPGRADESTATUS
	echo "  Upgrade attempt        :" $UPGRADEATTEMPTS
	echo " "
	echo "--------------------------------------------------"
	
	if [ $UPGRADESTATUS = "active" ]; then
		UPGRADE_CANCELLABLE="false"
	fi

	## If max upgrade attempts was hit, go back or halt
	if [ $UPGRADEATTEMPTS -gt $MAX_UPGRADE_ATTEMPTS ];
	then
		echo Too many failed attempts for package $UPGRADEPKG...
		if [ "$UPGRADEPKG" = "$PKGNAME_UPGRADE" ]; then
			UPGRADEPKG=$PKGNAME_ACTIVE
			sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME="$UPGRADEPKG'/' $FWUP_CONFIG
			sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS=0"'/' $FWUP_CONFIG
		elif [ "$UPGRADEPKG" = "$PKGNAME_ACTIVE" ]; then
			UPGRADEPKG=$PKGNAME_ROLLBACK
			sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME="$UPGRADEPKG'/' $FWUP_CONFIG
			sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS=0"'/' $FWUP_CONFIG
		else
			sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=halt"'/' $FWUP_CONFIG
			echo ...Halting system
			finish_up $ERR_HALT
		fi
		echo ...switching to package $UPGRADEPKG
	fi

	## Check upgrade package 
	echo " "
	echo Checking package: \'$UPGRADEPKG\'
	check_pkg $UPGRADEPKG
	retval=$?
	if  [ "$retval" != "$ERR_SUCCESS" ];
	then
		finish_up $retval
	fi
	echo ...complete

	## Backup user data from rootfs
	echo " "
	if [ ! -d $FWUP_BACKUP ]; then
		echo Backing up user data...
		mkdir $FWUP_BACKUP
		usrdata_action "backup"
		retval=$?
		if  [ "$retval" != "$ERR_SUCCESS" ]; then
			echo ...complete with error code $retval
		else
			echo ...complete
		fi
	fi

	## Program upgrade package to flash
	UPGRADE_CANCELLABLE="false"
	echo " "
	echo Programming QSPI NOR flash...
	sed -i 's/^PACKAGE_NAME.*/'"PACKAGE_NAME="$UPGRADEPKG'/' $FWUP_CONFIG
	sed -i 's/^UPGRADE_ATTEMPTS.*/'"UPGRADE_ATTEMPTS="$UPGRADEATTEMPTS'/' $FWUP_CONFIG
	sed -i 's/^UPGRADE_STATUS.*/'"UPGRADE_STATUS=active"'/' $FWUP_CONFIG
	program_flash $UPGRADEPKG
	retval=$?
	retval=$ERR_SUCCESS
	if  [ "$retval" != "$ERR_SUCCESS" ];
	then
		finish_up $retval
	fi
	echo ...complete

	## Restore user data to rootfs
	echo " "
	echo Restoring user data...
	usrdata_action "restore"
	retval=$?
	if  [ "$retval" != "$ERR_SUCCESS" ]; then
		echo ...complete with error code $retval
	else
		echo ...complete
	fi
		
	## Replace packages
	if [ "$UPGRADEPKG" != "$PKGNAME_ACTIVE" ]; then
		echo " "
		echo Replacing package 'active' with package \'$UPGRADEPKG\'
		replace_package $UPGRADEPKG
		retval=$?
		if  [ "$retval" != "$ERR_SUCCESS" ];
		then
			finish_up $retval
		fi
		echo ...complete
	fi
}

## Top level --------------------##
main_toplevel $1

## Wrap up
echo Finishing upgrade...
finish_up $ERR_SUCCESS

