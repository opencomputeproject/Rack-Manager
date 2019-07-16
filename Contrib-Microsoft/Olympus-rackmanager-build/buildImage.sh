#!/bin/bash

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

STARTTIME=$(date +%s)
SCRIPTROOTDIR=$(pwd)
BUILDINTENT=$1
BUILDEXT=$2
BUILDROOTDIR=$SCRIPTROOTDIR/yoctoBuilds
IMAGEOUTDIR=$BUILDROOTDIR/images
VER_FILENAME=$SCRIPTROOTDIR"/yocto/meta-rackmanager/recipes-core/rm-versions/files/pkg-info"
FWUPSCRSOURCE=$SCRIPTROOTDIR"/rackmanager/ocs/ocsfwup/scripts/fwupgrade.sh"

function makeupgradepackage() {
	cd $IMAGEOUTDIR
	if [ "$1" != "bintgz" ]; then
		rm -f m2010fwimage-*
	fi
	rm -rf ./fwupgrade
	mkdir ./fwupgrade

	PKGFILES="am437x-msocs.dtb rootfs.jffs2 u-boot.bin zImage.bin fwupgrade.sh"
	cd ./fwupgrade
	echo "PACKAGE_VERSION = "$VER_STRING  >> pkg.manifest

	for file in $PKGFILES
	do
		if [ $file != "fwupgrade.sh" ]; then
			cp ../qspi/qspi-$file $file
		else
			cp $FWUPSCRSOURCE $file
		fi
		md5sum $file >> pkg.manifest
	done
	
	if [ "$1" = "bintgz" ]; then
		ftfile="zImage-initflasher.bin"
		cp $BUILDROOTDIR/tmp/deploy/images/ocs-am437x/zImage-initramfs-ocs-am437x.bin $ftfile
		md5sum $ftfile >> pkg.manifest
		BUNDLEEXT="bin.tgz"
	else
		cp pkg.manifest ../qspi/.
		BUNDLEEXT="tgz"
	fi
	
	tar -czf m2010fwimage-$VER_STRING.$BUNDLEEXT *
	mv m2010fwimage-$VER_STRING.$BUNDLEEXT ../
	cd $BUILDROOTDIR
	rm -rf $IMAGEOUTDIR/fwupgrade
}

if [ "$BUILDINTENT" = "makebintgz" ]; then
	VER_STRING=$(cat $VER_FILENAME | awk '{FS="_";$0=$0;print $4}')
	makeupgradepackage bintgz
	exit
fi

# Update component versions
./updatebuildver.sh $BUILDINTENT
VER_STRING=$(cat $VER_FILENAME | awk '{FS="_";$0=$0;print $4}')

# Setup environment for build
source yocto/oe-init-build-env $BUILDROOTDIR

# Create needed paths
rm -rf images/
mkdir -p images/qspi/
mkdir -p images/emmc/
mkdir -p images/uart/
mkdir -p images/tftp/

if [ "$BUILDINTENT" = "full" ] || [ "$BUILDINTENT" = "release" ]; then
	rm -rf cache/ sstate-cache/ tmp/
fi

## Build and save binaries for QSPI
bitbake -R conf/local.conf u-boot-ti-staging -c cleansstate
bitbake -R conf/local.conf core-image-msocs
if [ $? -ne 0 ]; then
	exit 1
fi

cp tmp/deploy/images/ocs-am437x/core-image-msocs-ocs-am437x.jffs2 images/qspi/qspi-rootfs.jffs2
cp tmp/deploy/images/ocs-am437x/zImage-ocs-am437x.bin images/qspi/qspi-zImage.bin
cp tmp/deploy/images/ocs-am437x/zImage-am437x-ms-ocs.dtb images/qspi/qspi-am437x-msocs.dtb
cp tmp/deploy/images/ocs-am437x/u-boot-ocs-am437x.bin images/qspi/qspi-u-boot.bin

## Build and save eMMC images
bitbake -R conf/local.conf u-boot-ti-staging -c cleansstate
bitbake -R conf/initramfs.conf u-boot-ti-staging
if [ $? -ne 0 ]; then
	exit 1
fi

cp tmp/deploy/images/ocs-am437x/u-boot-ocs-am437x.img images/emmc/emmc-u-boot.img
cp tmp/deploy/images/ocs-am437x/MLO images/emmc/MLO

## Create FW upgrade package that also generates pkg.manifest with md5sums
makeupgradepackage

## Build the bundled flash image
bitbake -R conf/initramfs.conf core-flasher-msocs
if [ $? -ne 0 ]; then
	exit 1
fi

## Copy TFTP specific items
cp tmp/deploy/images/ocs-am437x/zImage-initramfs-ocs-am437x.bin images/tftp/zImage-initflasher.bin
cp tmp/deploy/images/ocs-am437x/zImage-am437x-ms-ocs.dtb images/tftp/am437x-msocs.dtb

## Copy UART specific items
cp tmp/deploy/images/ocs-am437x/u-boot-ocs-am437x.img images/uart/u-boot.img
cp tmp/deploy/images/ocs-am437x/u-boot-spl.bin images/uart/u-boot-spl.bin
cp ../rackmanager/UARTScr/Send-MLO-UB.ttl images/uart/.
cp ../rackmanager/UARTScr/Send-MLO-MGMTSWPort.ttl images/uart/.
cp ../rackmanager/UARTScr/Send-UB-DIGIPort.ttl images/uart/.

ENDTIME=$(date +%s)
echo "* Build took $(($ENDTIME - $STARTTIME)) seconds"
echo "* Build package version: $VER_STRING"
echo "**************************************************************"
