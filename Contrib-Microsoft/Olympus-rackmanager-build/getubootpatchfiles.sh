#!/bin/bash

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

TI_SDK_PATH=/home/user/source/Development/M2010/SDK/ocs-ti-sdk
UBOOT_DIR=$TI_SDK_PATH/board-support/u-boot-2015.07+gitAUTOINC+46c915c963
YOCTO_UBOOT_GIT=yoctoBuilds/tmp/work/ocs_am437x-poky-linux-gnueabi/u-boot-ti-staging/2015.07+gitAUTOINC+2cc2dbc876-r25/git

FILES="arch/arm/Kconfig
arch/arm/cpu/armv7/am33xx/Kconfig
arch/arm/cpu/armv7/am33xx/ddr.c
arch/arm/cpu/armv7/am33xx/board.c
arch/arm/cpu/armv7/am33xx/clock_am43xx.c
arch/arm/include/asm/arch-am33xx/hardware.h
arch/arm/include/asm/arch-am33xx/hardware_am43xx.h
arch/arm/include/asm/arch-am33xx/sys_proto.h
include/configs/am43xx_ocs.h
include/configs/ti_armv7_common.h
include/configs/ti_armv7_omap.h
board/ti/am43xx_ocs/mux.c
board/ti/am43xx_ocs/board.c
board/ti/am43xx_ocs/board.h
board/ti/am43xx_ocs/Kconfig
board/ti/am43xx_ocs/Makefile
configs/am43xx_ocs_emmcboot_defconfig
configs/am43xx_ocs_qspiboot_defconfig"

mkdir -p $YOCTO_UBOOT_GIT/board/ti/am43xx_ocs

for file in $FILES
do
	cp  $UBOOT_DIR/$file $YOCTO_UBOOT_GIT/$file
done
