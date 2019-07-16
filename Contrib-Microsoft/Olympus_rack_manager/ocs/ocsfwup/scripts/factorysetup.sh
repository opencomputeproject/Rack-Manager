#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

echo " "
echo " "
echo "--------------------------------------------------------"
echo "  Microsoft OCS Rack Manager Factory recovery v1.7      "
echo " "
echo "  Setup start local time: " $(date +"%D %T %z")
echo "  Factory recovery software package :" $(cat /etc/pkg-info | awk '{FS="_";$0=$0;print $4}')
echo " "
echo "  Upgrader OS versions:"
echo "  U-Boot     :" $(cat /proc/cmdline | awk '{print $4}' | awk '{FS="_";$0=$0;print $4}')
echo "  Kernel     :" $(cat /proc/sys/kernel/osrelease | awk {'FS="-";$0=$0;print $2}' | awk '{FS="_";$0=$0;print $4}')
echo "  Devicetree :" $(cat /proc/device-tree/model | awk '{FS="_";$0=$0;print $4}')
echo " "
echo "--------------------------------------------------------"
echo " "

STARTTIME=$(date +%s)

##---------Start of variables---------------------##

## Declare eMMC device name here
EMMC_DRIVE="/dev/mmcblk0"

## QSPI images
QSPI_UBOOT="/etc/images/qspi/u-boot.bin"
QSPI_KERNEL="/etc/images/qspi/zImage.bin"
QSPI_DEVICETREE="/etc/images/qspi/am437x-msocs.dtb"
QSPI_ROOTFS="/etc/images/qspi/rootfs.jffs2"

## EMMC images
EMMC_IMAGE="zImage-initflasher.bin"
EMMC_DTBIMAGE="am437x-msocs.dtb"
EMMC_LOCAL_IMAGE="/mnt/bootpart/boot/zImage-initflasher.bin"

FWUP_LOGFILE="/tmp/fwup.log"
FWUP_LOGPERSIST="/mnt/emmc/fwup.log"
FWUP_LOGPERSISTPUB="/mnt/srvroot/shared/ocsfwup.log"

##----------End of variables-----------------------##


## Partitions for the 4GB EMMC on EV boards
##  1. FAT, size = 32 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~250MB
##  2. FAT, size = 32 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~250MB
##  3. EXT4, size = 206 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~1620MB
##  4. EXT4, size = 205 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~1610MB
partition_emmc_4GB(){
sfdisk -q -D -H 255 -S 63 -C $CYLINDERS $EMMC_DRIVE << EOF
,32,0x0C,*
,32,0x0C,
,206,,-
,,,-
EOF
}

## Partitions for the 8GB EMMC on DV+ boards
##  1. FAT, size = 32 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~250MB
##  2. FAT, size = 32 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~250MB
##  3. EXT4, size = 636 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~4250MB
##  4. EXT4, size = 250 cylinders * 255 heads * 63 sectors * 512 bytes/sec = ~2000MB
partition_emmc_8GB(){
sfdisk -q -D -H 255 -S 63 -C $CYLINDERS $EMMC_DRIVE << EOF
,32,0x0C,*
,32,0x0C,
,636,,-
,,,-
EOF
}

UPGRADETYPE="$1"
BOOTMEDIUM=$(cat /proc/cmdline | awk '{print $2}')

if  [ $UPGRADETYPE = "emmcprov" ] || [ $BOOTMEDIUM != 'bootmedium=EMMC' ]; then
	echo "--------------------------------------------------------"
	echo "#                  Setting up eMMC Flash               #"
	echo " "
	## Make temp directories for mountpoints
	mkdir -p /mnt
	mkdir -p /mnt/emmc
	mkdir -p /mnt/bootpart
	mkdir -p /mnt/srvroot
	
	mount -t vfat ${EMMC_DRIVE}p1 /mnt/bootpart
	if [ $UPGRADETYPE = "emmcprov" ] && [ -f $EMMC_LOCAL_IMAGE ]; then
		cp $EMMC_LOCAL_IMAGE /mnt/.
	fi
	umount /mnt/bootpart
	
	##mkdir /mnt/emmc/fs

	## Figure out how big the eMMC is in bytes
	## Translate size into segments, which traditional tools call Cylinders. eMMC is not a spinning disk.
	## We are basically ignoring what FDISK and SFDISK are reporting because it is not really accurate.
	## we are translating this info to something that makes more sense for eMMC.
	## 1 cylinder = 63 (heads) * 255 (secotrs) * 512 (bytes/sector) = 8225280
	SIZE=$(fdisk -l $EMMC_DRIVE | grep ${EMMC_DRIVE}: | awk 'NR==1 {print $5}')
	CYLINDERS=$(($SIZE/8225280))

	## Erase partition area 
	dd if=/dev/zero of=$EMMC_DRIVE bs=4k count=1
	sync
	
	## Partitioning the eMMC using information gathered.
	echo ""
	echo "# Partitioning the eMMC..."
	if [[ "$CYLINDERS" -gt '900' ]]; then
		partition_emmc_8GB
	else
		partition_emmc_4GB
	fi
	echo "# ...complete"

	## This sleep is necessary as there is a service which attempts
	## to automount any filesystems that it finds as soon as sfdisk
	## finishes partitioning.  We sleep to let it run.  May need to
	## be lengthened if you have more partitions.
	sleep 2

	## Check here if there has been a partition that automounted.
	## This will eliminate the old partition that gets
	## automatically found after the sfdisk command.  It ONLY
	## gets found if there was a previous file system on the same
	## partition boundary.  Happens when running this script more than once.
	## To fix, we just unmount and write some zeros to it.
	## check_mounted;

	## Clean up the dos (FAT) partition as recommended by SFDISK
	echo ""
	echo "# Cleaning FAT partition"
	dd if=/dev/zero of=${EMMC_DRIVE}p1 bs=512 count=1
	sync
	echo "# ...complete"
	
	## read -p "Press any key to continue formating partitions... " -n1 -s
	
	## Format the eMMC into 2 partitions
	echo ""
	echo "# Formatting the eMMC partitions..."

	## Format the boot partition to fat32
	mkfs.vfat -F 32 -n "EMMCBOOT" ${EMMC_DRIVE}p1
	sync

	## Format the package store partition to fat32
	mkfs.vfat -F 32 -n "PKGSTORE" ${EMMC_DRIVE}p2
	sync	
	
	## Format srvroot to ext4 
	mkfs.ext4 -q -F -F -L "SRVROOT" ${EMMC_DRIVE}p3
	sync
	mount ${EMMC_DRIVE}p3 /mnt/srvroot/
	mkdir -p /mnt/srvroot/shared
	sync
	umount /mnt/srvroot
	
	## Format persist to ext4 
	mkfs.ext4 -q -F -F -L "PERSIST" ${EMMC_DRIVE}p4
	sync
	echo "# ...complete"
	echo ""
	
	## Mount package store partition for initial setup
	echo "# Copying images for future firmware recovery..."
	mount -t vfat ${EMMC_DRIVE}p2 /mnt/emmc/
	mkdir /mnt/emmc/active
	mkdir /mnt/emmc/rollback
	mkdir /mnt/emmc/upgrade
	cp /etc/images/qspi/* /mnt/emmc/active
	cp /etc/images/qspi/* /mnt/emmc/rollback
	cp /etc/fwup.config /mnt/emmc/
	sync
	echo "# ...complete"
	
	## Mount boot part for factory image backup	and copy files into eMMC boot part
	mount -t vfat ${EMMC_DRIVE}p1 /mnt/bootpart 
	echo ""
	echo "# Copying boot files..."
	mkdir -p /mnt/bootpart/boot
	cp /etc/images/emmc/* /mnt/bootpart/
	mv /mnt/bootpart/${EMMC_DTBIMAGE} /mnt/bootpart/boot/
	sync

	if [ $UPGRADETYPE = "emmcprov" ] && [ -f /mnt/$EMMC_IMAGE ]; then
		cp /mnt/$EMMC_IMAGE $EMMC_LOCAL_IMAGE
	else
		## TFTP in the emmc image 
		SERVER_IP=$(cat /proc/cmdline | awk '{print $3}' | awk '{FS="=";$0=$0;print $2}')
		echo "# Fetching eMMC recovery image over TFTP from" $SERVER_IP
		busybox tftp -g -r ${EMMC_IMAGE} -l ${EMMC_LOCAL_IMAGE} ${SERVER_IP}	
	fi
	sync
	echo "# ...complete"
	
	umount /mnt/emmc
	umount /mnt/bootpart
	
	echo " "	
	echo "#              eMMC Flash setup complete               #"
	echo "--------------------------------------------------------"
fi


echo ""
#read -p "Press y and then enter key to setup QSPI flash: " UserInput
UserInput=y
if  [[ "$UserInput" != 'n' ]]; then
	echo "--------------------------------------------------------"
	echo "#              Setting up QSPI NOR Flash               #"
	echo " "
	echo "# Wiping out U-Boot env partition.."
	flash_erase -q /dev/mtd2 0 0
	echo "# ...complete"
	echo ""
	
	echo "# Preparing Devicetree partition.."
	flashcp $QSPI_DEVICETREE /dev/mtd3
	echo "# ...complete"
	echo ""
	
	echo "# Preparing Kernel partition.."
	NBlocks=$((1 + $(stat -c%s $QSPI_KERNEL) / 65536))
	flashcp $QSPI_KERNEL /dev/mtd4
	echo "# ...complete"
	echo ""
	
	echo "# Preparing Root filesystem partition.."
	flashcp $QSPI_ROOTFS /dev/mtd5
	echo "# ...complete"
	echo ""
	
	echo "# Preparing U-Boot backup partition.."
	flashcp $QSPI_UBOOT /dev/mtd1
	echo "# ...complete"
	echo ""
	
	echo "# Preparing U-Boot partition.."
	flashcp $QSPI_UBOOT /dev/mtd0
	echo "# ...complete"
	echo ""
	
	echo ""
	echo "#              QSPI NOR Flash setup complete           #"
	echo "--------------------------------------------------------"
fi

ENDTIME=$(date +%s)
echo Completed in $(($ENDTIME - $STARTTIME)) seconds
echo "**************************************************************"

if [ -f $FWUP_LOGFILE ]; then
	cat $FWUP_LOGFILE >> $FWUP_LOGPERSIST
	mount ${EMMC_DRIVE}p3 /mnt/srvroot/
	cp $FWUP_LOGPERSIST $FWUP_LOGPERSISTPUB
	sync
	umount /mnt/srvroot
fi

sync
umount /mnt/emmc/

echo ""
echo "" 
reboot
