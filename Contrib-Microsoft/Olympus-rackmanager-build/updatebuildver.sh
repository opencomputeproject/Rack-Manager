#!/bin/bash

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# --------------------------------------------------------------------------------
# Distinguish dev builds from release builds
if [ "$1" ] && [ "$1" = "release" ]; then
	DEVTAG=0
else
	DEVTAG=100
fi

VER_FILENAME=./buildver.inc
BSP_FILENAME=./yocto/meta-rackmanager/recipes-bsp/u-boot/files/ubootPatch.patch
DTS_FILENAME=./yocto/meta-rackmanager/recipes-kernel/linux/files/m0Patch.patch
KER_FILENAME=./yocto/meta-rackmanager/recipes-kernel/linux/files/ocs437x-rm.cfg
RFS_FILENAME=./yocto/meta-rackmanager/recipes-core/rm-versions/files/rfs-info
PKG_FILENAME=./yocto/meta-rackmanager/recipes-core/rm-versions/files/pkg-info

# --------------------------------------------------------------------------------
# Update rolling build ID into buildver.inc
VER_BLD=$((1 + $(cat $VER_FILENAME | grep ROLLING_BUILD_ID | awk '{print $3}')))
BLD_STRING="#define ROLLING_BUILD_ID            "$VER_BLD" "
sed -i 's/^#define ROLLING_BUILD_ID.*/'"$BLD_STRING"'/' $VER_FILENAME

# --------------------------------------------------------------------------------
# Update U-boot version info from buildver.inc
UBMD5="$(md5sum $BSP_FILENAME | awk '{print $1}')"
UBMD5REF="$(grep BSP_PATCH_MD5SUM ${VER_FILENAME} | awk '{print $3}')"
if [ "$UBMD5" != "$UBMD5REF" ]; then
	VER_MAJ="$(($(cat $VER_FILENAME | grep BSP_VERSION_MAJOR    | awk '{print $3}') + $DEVTAG))"
	VER_MIN="$(cat $VER_FILENAME | grep BSP_VERSION_MINOR    | awk '{print $3}')"
	VER_REV="$(cat $VER_FILENAME | grep BSP_VERSION_REVISION | awk '{print $3}')"
	VER_STRING=$VER_MAJ.$VER_MIN.$VER_REV.$VER_BLD

	# Update U-boot version line
	BSP_STRING="+#define CONFIG_IDENT_STRING    "\""-MS_OCS_RM_"$VER_STRING\"
	sed -i 's/^+#define CONFIG_IDENT_STRING.*/'"$BSP_STRING"'/' $BSP_FILENAME
	UBMD5="$(md5sum $BSP_FILENAME | awk '{print $1}')"
	BSP_STRING="#define BSP_PATCH_MD5SUM            "$UBMD5
	sed -i 's/^#define BSP_PATCH_MD5SUM.*/'"$BSP_STRING"'/' $VER_FILENAME
fi

# --------------------------------------------------------------------------------
# Update DTS version info from buildver.inc
VER_MAJ="$(($(cat $VER_FILENAME | grep DTS_VERSION_MAJOR    | awk '{print $3}') + $DEVTAG))"
VER_MIN="$(cat $VER_FILENAME | grep DTS_VERSION_MINOR    | awk '{print $3}')"
VER_REV="$(cat $VER_FILENAME | grep DTS_VERSION_REVISION | awk '{print $3}')"
VER_STRING=$VER_MAJ.$VER_MIN.$VER_REV.$VER_BLD

# Update DTS version line
DTS_STRING="+    model = \"MS_OCS_RM_"$VER_STRING"\";"
sed -i 's/^+    model =.*/'"$DTS_STRING"'/' $DTS_FILENAME

# --------------------------------------------------------------------------------
# Update Kernel version info from buildver.inc
VER_MAJ="$(($(cat $VER_FILENAME | grep KER_VERSION_MAJOR    | awk '{print $3}') + $DEVTAG))"
VER_MIN="$(cat $VER_FILENAME | grep KER_VERSION_MINOR    | awk '{print $3}')"
VER_REV="$(cat $VER_FILENAME | grep KER_VERSION_REVISION | awk '{print $3}')"
VER_STRING=$VER_MAJ.$VER_MIN.$VER_REV.$VER_BLD

# Update Kernel version line
KER_STRING="CONFIG_LOCALVERSION="\""-MS_OCS_RM_"$VER_STRING\"
sed -i 's/^CONFIG_LOCALVERSION.*/'"$KER_STRING"'/' $KER_FILENAME

# --------------------------------------------------------------------------------
# Update Rootfs version info from buildver.inc
VER_MAJ="$(($(cat $VER_FILENAME | grep RFS_VERSION_MAJOR    | awk '{print $3}') + $DEVTAG))"
VER_MIN="$(cat $VER_FILENAME | grep RFS_VERSION_MINOR    | awk '{print $3}')"
VER_REV="$(cat $VER_FILENAME | grep RFS_VERSION_REVISION | awk '{print $3}')"
VER_STRING=$VER_MAJ.$VER_MIN.$VER_REV.$VER_BLD

# Update Rootfs version line
echo "MS_OCS_RM_"$VER_STRING > $RFS_FILENAME

# --------------------------------------------------------------------------------
# Update Package version info from buildver.inc
VER_MAJ="$(($(cat $VER_FILENAME | grep PKG_VERSION_MAJOR    | awk '{print $3}') + $DEVTAG))"
VER_MIN="$(cat $VER_FILENAME | grep PKG_VERSION_MINOR    | awk '{print $3}')"
VER_REV="$(cat $VER_FILENAME | grep PKG_VERSION_REVISION | awk '{print $3}')"
VER_STRING=$VER_MAJ.$VER_MIN.$VER_REV.$VER_BLD

# Update Package version line
echo "MS_OCS_RM_"$VER_STRING > $PKG_FILENAME
