#!/bin/bash

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#Change this to match source tree path
TI_SDK_PATH=/home/user/source/Development/M2010/SDK/ocs-ti-sdk
KERNEL_DIR=$TI_SDK_PATH/board-support/linux-4.1.18+gitAUTOINC+bbe8cfc1da-gbbe8cfc

HOMEPATH=$(pwd)
GITPATH=yoctoBuilds/tmp/work/ocs_am437x-poky-linux-gnueabi/linux-ti-staging/4.1.21+gitAUTOINC+1c9b6ad8bb-r3ll/git
PATCHPATH=yocto/meta-rackmanager/recipes-kernel/linux/files/m0Patch.patch

FILES="arch/arm/boot/dts/Makefile
arch/arm/boot/dts/am4372.dtsi
arch/arm/mach-omap2/omap_hwmod_43xx_data.c
arch/arm/mach-omap2/prcm43xx.h
drivers/iio/adc/Makefile
drivers/remoteproc/pru_rproc.c
arch/arm/boot/dts/am437x-ms-ocs.dts
drivers/iio/adc/ti_am437x_adc1.c
include/linux/mfd/ti_am437x_adc1.h"

cd $GITPATH

for file in $FILES
do
	cp  $KERNEL_DIR/$file $file
	git add $file
done
git diff --cached > $HOMEPATH/$PATCHPATH

cd $HOMEPATH

