// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <sys/stat.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <time.h>
#include <logging.h>

#define APPNAME                         "ocs-fwup"

#define VERSION_MAKEWORD(maj, min, rev, bld) ( ((maj & 0xFF) << 24) | \
                                                ((min & 0x0F) << 20) | \
                                                ((rev & 0x0F) << 16) | \
                                                (bld & 0xFFFF) )

#define VERSION_GET_MAJOR(ver) 			( (ver >> 24) & 0xFF )
#define VERSION_GET_MINOR(ver) 			( (ver >> 20) & 0x0F )
#define VERSION_GET_REVISION(ver) 		( (ver >> 16) & 0x0F )
#define VERSION_GET_BUILD(ver) 			( ver & 0xFFFF )

typedef enum { 
    FALSE                               = 0,
    TRUE                                = 1
} bool_t;

#define FWUP_MOUNTPOINT					"/tmp/~ocsfwup"

#define FWUP_UPGRADEOS_DEVICE			"/dev/mmcblk0p1"
#define FWUP_UPGRADEOS_MOUNTPOINT		FWUP_MOUNTPOINT "/upos/"
#define FWUP_UPGRADEOS_FSTYPE			"vfat"
#define FWUP_UPGRADEOS_FILELIST			{"MLO", "u-boot.img", "boot/am437x-msocs.dtb", "boot/zImage-initflasher.bin"}
#define FWUP_UPGRADEOS_FILECOUNT		4

#define FWUP_IMAGESTORE_DEVICE			"/dev/mmcblk0p2"
#define FWUP_IMAGESTORE_MOUNTPOINT		FWUP_MOUNTPOINT "/pkgstore/"
#define FWUP_IMAGESTORE_FSTYPE			"vfat"

enum { 
	FWUP_PKGID_ROLLBACK					= 0,
	FWUP_PKGID_ACTIVE,
	FWUP_PKGID_UPGRADE,
	FWUP_PKGID_FACTORY,
	FWUP_PKGID_EMMCPROV,
	FWUP_PKGID_MAX
};
#define FWUP_IMAGESTORE_PKGNAMES		{"rollback", "active", "upgrade", "factory", "emmcprov"}

enum { 
	FWUP_STATUS_COMPLETE				= 0,
	FWUP_STATUS_PENDING,
	FWUP_STATUS_ACTIVE,
	FWUP_STATUS_FAILED,
	FWUP_STATUS_HALT,
	FWUP_STATUS_MAX
};
#define FWUP_STATUS_NAMES				{"complete", "pending", "active", "failed", "halt"}

#define FWUP_IMAGESTORE_ROLLBACKFILE	FWUP_IMAGESTORE_MOUNTPOINT "rollback.tar"
#define FWUP_IMAGESTORE_CURRENTFILE		FWUP_IMAGESTORE_MOUNTPOINT "current.tar"
#define FWUP_IMAGESTORE_UPGRADEFILE		FWUP_IMAGESTORE_MOUNTPOINT "M2010upgradepkg.tar"
#define FWUP_IMAGESTORE_CFGFILE			FWUP_IMAGESTORE_MOUNTPOINT "fwup.config"
#define FWUP_FACTORYFILENAME			"zImage-initflasher.bin"
#define FWUP_FILEEXT_BIN				".bin"
#define FWUP_FILEEXT_TGZ				".tgz"
#define FWUP_FILEEXT_BINTGZ				".bin.tgz"
#define FWUP_MOUNTPOINT_FACTORYFILE		FWUP_MOUNTPOINT "/"FWUP_FACTORYFILENAME
#define FWUP_UPGRADEOS_FACTORYFILE		FWUP_UPGRADEOS_MOUNTPOINT "boot/"FWUP_FACTORYFILENAME

#define FWUP_RUNTIMEOS_UBOOT_BLKDEV1	"/dev/mtdblock0"
#define FWUP_RUNTIMEOS_UBOOT_BLKDEV2	"/dev/mtdblock1"
#define UBOOT_SECTOR_SIZE 				65536
#define MAX_UBOOT_SECTORS				16
