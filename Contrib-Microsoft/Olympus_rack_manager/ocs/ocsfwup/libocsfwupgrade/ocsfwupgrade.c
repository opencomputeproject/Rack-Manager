// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/wait.h>

#include <ocsfwup.h>
#include <ocsfwupgrade.h>
 
/* Helper macros */
#define LOG_ERROR   do {                            \
        if (errno > 0 || retval < 0)                \
            LOG_FNC_ERR(errno);                     \
    } while (0);                                    \

#define GET_SIZE(fd, retsize) {						\
		fseek(fd, 0L, SEEK_END);					\
		retsize = ftell(fd);						\
		rewind(fd);									\
	}												\

#define FILEBUFSIZE 65536

const char *pkgnames[FWUP_PKGID_MAX] = FWUP_IMAGESTORE_PKGNAMES;

int copy_to_store(char *pkgfile, char *isfile)
{
	ssize_t rdsize = 0, vsize = 0;
	FILE *out_fd = NULL, *in_fd = NULL;
	void *buf, *vbuf;
	struct timespec time1 = {0, 0}, time2 = {0, 0};
	//long filesize;
	int retval = SUCCESS;
	
	buf = malloc(FILEBUFSIZE);
	vbuf = malloc(FILEBUFSIZE);
	if (!buf || !vbuf) {
		LOG_ERR(errno, "Buffer allocation failed for copy\n");
		retval = FAILED;
		goto _exit_fn;
	}

	in_fd = fopen(pkgfile, "r");
	if ( in_fd == NULL ) {
		LOG_ERR(errno, "Upgrade package file %s open failed\n", pkgfile);
		retval = FAILED;
		goto _exit_fn;
	}

	out_fd = fopen(isfile, "w");
	if ( out_fd == NULL ) {
		LOG_ERR(errno, "Failed to open file %s\n", isfile);
		retval = FAILED;
		goto _exit_fn;
	}
	
	//GET_SIZE(in_fd, filesize);

	clock_gettime(CLOCK_REALTIME, &time1);
	LOG_INFO("Copying upgrade package file.. %s\n", pkgfile);
	while (1) {
		rdsize = fread(buf, 1, FILEBUFSIZE, in_fd);
		if (!rdsize)
			break;
		if (fwrite(buf, 1, rdsize, out_fd) != rdsize) {
			retval = FAILED;
			goto _exit_fn;
		}
		LOG_TRACE("%d kB complete\n", (int)ftell(in_fd));
	}
	clock_gettime(CLOCK_REALTIME, &time2);
	LOG_TRACE("Completed in %ds\n", (int)(time2.tv_sec - time1.tv_sec));
	fclose(out_fd);
	out_fd = NULL;
	fclose(in_fd);
	in_fd = NULL;
	
	LOG_INFO("Verifying upgrade package copy.. ");
	in_fd = fopen(pkgfile, "r");
	out_fd = fopen(isfile, "r");
	retval = 0;
	while ( retval == 0 ) {
		rdsize = fread(buf, 1, FILEBUFSIZE, in_fd);
		vsize = fread(vbuf, 1, FILEBUFSIZE, out_fd);
		if (rdsize == 0 || vsize == 0)
			break;		
		retval = memcmp(buf, vbuf, rdsize);
		LOG_TRACE("%lu kB\n", ftell(in_fd));
	}
	if (retval == 0) {
		retval = SUCCESS;
		LOG_INFO("passed\n");
	}
	else
		LOG_INFO("failed\n");

	clock_gettime(CLOCK_REALTIME, &time1);
	LOG_TRACE("Verify completed in %ds\n", (int)(time1.tv_sec - time2.tv_sec));

_exit_fn:
	if (in_fd) {
		fclose(in_fd);
	}
	if (out_fd) {
		fclose(out_fd);
	}
	return retval;
}

int check_upgradeos()
{
	int c;
	FILE *file;
	int retval = SUCCESS;
	char chkfilename[256];
	const char *upgradeOSfiles[FWUP_UPGRADEOS_FILECOUNT] = FWUP_UPGRADEOS_FILELIST;

	/* Check if UpgradeOS is intact */
	for (c=0; c < FWUP_UPGRADEOS_FILECOUNT && retval == SUCCESS; c++) {
		sprintf(chkfilename, "%s%s", FWUP_UPGRADEOS_MOUNTPOINT, upgradeOSfiles[c]);
		LOG_TRACE("Checking file: %s\n", chkfilename);
		retval = (file = fopen(chkfilename, "r"))?fclose(file):FAILED;
	}
	
	if (retval != SUCCESS)
		LOG_TRACE("UpgradeOS check failed\n");
	
	return retval;
}	

int setup_upgradeos(bool_t mountrw)
{
	//const char* opts = "mode=0700,uid=65534";   /* 65534 is the uid of nobody */
	int retval = SUCCESS;
	unsigned long mountflags;
	
	errno = 0;
	retval = mkdir(FWUP_MOUNTPOINT, S_IRWXU);
	if ( (retval != SUCCESS) && (errno != EEXIST) ) {
		LOG_ERR(errno, "Directory error %s\n", FWUP_MOUNTPOINT);
		goto _exit_fn;
	}	
	
	errno = 0;
	retval = mkdir(FWUP_UPGRADEOS_MOUNTPOINT, S_IRWXU);
	if ( (retval != SUCCESS) && (errno != EEXIST) ) {
		LOG_ERR(errno, "Directory error %s\n", FWUP_UPGRADEOS_MOUNTPOINT);
		goto _exit_fn;
	}
	
	errno = 0;
	/* Mount EMMC UpgradeOS partiition */
	mountflags =  MS_SYNCHRONOUS | mountrw?0:MS_RDONLY;
	retval = mount(FWUP_UPGRADEOS_DEVICE, FWUP_UPGRADEOS_MOUNTPOINT, FWUP_UPGRADEOS_FSTYPE, mountflags, NULL);
	if (retval != SUCCESS) {
		LOG_ERR(errno, "UpgradeOS drive mount error\n");
		goto _exit_fn;
	}

	LOG_TRACE("UpgradeOS drive mounted.\n");
	
	retval = check_upgradeos();
		 
_exit_fn:
	return retval;
}

int setup_imagestore()
{
	//const char* opts = "mode=0700,uid=65534";   /* 65534 is the uid of nobody */
	int retval = SUCCESS;

	errno = 0;
	
	retval = mkdir(FWUP_MOUNTPOINT, S_IRWXU);
	if ( (retval != SUCCESS) && (errno != EEXIST) ) {
		LOG_ERR(errno, "Directory error %s\n", FWUP_MOUNTPOINT);
		goto _exit_fn;
	}	
		
	retval = mkdir(FWUP_IMAGESTORE_MOUNTPOINT, S_IRWXU);
	if ( (retval != SUCCESS) && (errno != EEXIST) ) {
		LOG_ERR(errno, "Directory error %s\n", FWUP_IMAGESTORE_MOUNTPOINT);
		goto _exit_fn;
	}

	/* Mount EMMC Imagestore */
	retval = mount(FWUP_IMAGESTORE_DEVICE, FWUP_IMAGESTORE_MOUNTPOINT, FWUP_IMAGESTORE_FSTYPE, MS_SYNCHRONOUS, NULL);
	if (retval != SUCCESS) {
		LOG_ERR(errno, "Imagestore mount error\n");
		goto _exit_fn;
	}
	
_exit_fn:
	return retval;
}

#if 0
int uboot_invalidate(bool_t invbackup)
{
	int retval = SUCCESS;
	FILE *out_fd;
	unsigned char *vbuf;
	int sectorcount;

	vbuf = malloc(UBOOT_SECTOR_SIZE);
	if (!vbuf) {
		LOG_ERR(errno, "Buffer allocation failed for uboot invalidation\n");
		retval = FAILED;
		goto _exit_fn;
	}	

	memset(vbuf, 0xFF, UBOOT_SECTOR_SIZE);	
	out_fd = fopen(FWUP_RUNTIMEOS_UBOOT_BLKDEV1, "r+");
	if (out_fd == NULL) {
		LOG_ERROR;
		retval = FAILED;
		goto _exit_fn;
	}		
	for (sectorcount = 0; sectorcount < MAX_UBOOT_SECTORS; sectorcount++) {
		if (fwrite(vbuf, 1, UBOOT_SECTOR_SIZE, out_fd) != UBOOT_SECTOR_SIZE) {
			if (feof(out_fd) || (errno == ENOSPC)) {
				retval = SUCCESS;
				break;
			}

			LOG_ERROR;
			retval = FAILED;
			goto _exit_fn;
		}
	}
	fclose(out_fd);

	if (invbackup) {
		out_fd = fopen(FWUP_RUNTIMEOS_UBOOT_BLKDEV2, "r+");
		if (out_fd == NULL) {
			LOG_ERROR;
			retval = FAILED;
			goto _exit_fn;
		}		
		for (sectorcount = 0; sectorcount < MAX_UBOOT_SECTORS; sectorcount++) {
			if (fwrite(vbuf, 1, UBOOT_SECTOR_SIZE, out_fd) != UBOOT_SECTOR_SIZE) {
				if (feof(out_fd) || (errno == ENOSPC)) {
					retval = SUCCESS;
					break;
				}

				LOG_ERROR;
				retval = FAILED;
				goto _exit_fn;
			}
		}
		fclose(out_fd);
	}
	
_exit_fn:
	return retval;
}
#endif

int remove_mounts()
{
	umount(FWUP_UPGRADEOS_MOUNTPOINT);
	umount(FWUP_IMAGESTORE_MOUNTPOINT);
	return SUCCESS;	
}

int run_script(const char *method, char *name) 
{
	int retval = FAILED;
	int status = SUCCESS;
	pid_t chpid = 0;

	errno = 0;
	chpid = fork();
	if ( chpid ) {
		wait(&status);
		if (WIFEXITED(status))
			return (WEXITSTATUS(status));
		else
			retval = FAILED;
	}
	else {
		/* Child here - execute script and exit */
		retval = execl("/etc/init_fwupgrade.sh", "init_fwupgrade.sh", method, name, (char *)NULL);
		LOG_ERR(errno, "Failed to run init script.\n");
		exit(retval);
	}
	LOG_ERROR
	return FAILED;
}

/******************************************************************************
*   Function Name: ocs_fwup_startupgrade
*   Purpose: Exports appropriate GPIOs and sets direction.
*   Comments/Notes:
*******************************************************************************/
int ocs_fwup_startupgrade(char *pkg_path)
{
	int retval = FAILED;
	
	remove_mounts();
		
	if ( strstr(pkg_path, FWUP_FILEEXT_BINTGZ) != NULL ) {
		retval = setup_upgradeos(TRUE);
		if (retval != SUCCESS) {
			LOG_ERROR
			goto _exit;
		}
		
		/* Use Method U(pdate) to start upgrade*/
		retval = run_script("upgrade", (char *)pkg_path);
		if (retval != SUCCESS) {
			LOG_ERROR;
			goto _exit;
		}		
		
		retval = copy_to_store(FWUP_MOUNTPOINT_FACTORYFILE, FWUP_UPGRADEOS_FACTORYFILE);
		if (retval != SUCCESS) {
			LOG_ERROR;
			goto _exit;
		}

		umount(FWUP_UPGRADEOS_MOUNTPOINT);
		
		//retval = uboot_invalidate(FALSE);
	}
	else if ( strstr(pkg_path, FWUP_FILEEXT_BIN) != NULL ) {
		/* Use Method F(actory) to start upgrade*/
		retval = setup_upgradeos(TRUE);
		if (retval != SUCCESS) {
			LOG_ERROR
			goto _exit;
		}	

		LOG_TRACE("Copy package %s to %s\n", pkg_path, FWUP_UPGRADEOS_FACTORYFILE);
		retval = copy_to_store(pkg_path, FWUP_UPGRADEOS_FACTORYFILE);
		if (retval != SUCCESS) {
			LOG_ERROR;
			goto _exit;
		}
		umount(FWUP_UPGRADEOS_MOUNTPOINT);
		
		retval = run_script("recovery", (char *)pkgnames[FWUP_PKGID_EMMCPROV]);
		if (retval != SUCCESS) {
			LOG_ERROR;
			goto _exit;
		}

		//retval = uboot_invalidate(TRUE);
	}
	else if ( strstr(pkg_path, FWUP_FILEEXT_TGZ) != NULL ) {
		retval = setup_upgradeos(FALSE);
		if (retval != SUCCESS) {
			LOG_ERROR
			goto _exit;
		}
		umount(FWUP_UPGRADEOS_MOUNTPOINT);

		/* Use Method U(pdate) to start upgrade*/
		retval = run_script("upgrade", (char *)pkg_path);
		if (retval != SUCCESS) {
			LOG_ERROR;
			goto _exit;
		}
		
		//retval = uboot_invalidate(FALSE);
	}
	else {
		LOG_INFO("Unsupported upgrade file %s\n", pkg_path);
	}
	
	if (retval != SUCCESS) {
		LOG_ERROR
		goto _exit;
	}
	
	retval = system("( sleep 10; /sbin/reboot ) &");
	LOG_INFO("FW Upgrade operation started, system will reboot in 10s...\n\n");

_exit:
	LOG_TRACE("Lib return: %d", retval);
	remove_mounts();
	return retval?FAILED:SUCCESS;
}

int ocs_fwup_startrecovery(int recovery_type)
{
	int retval = SUCCESS;
	
	if ( recovery_type >= FWUP_PKGID_MAX ) {
		LOG_INFO("Unsupported recovery type %d\n", recovery_type);
		goto _exit;
	}
	
	retval = run_script("recovery", (char *)pkgnames[recovery_type]);
	if (retval != SUCCESS) {
		LOG_ERROR
		goto _exit;
	}
	
	//retval = uboot_invalidate(FALSE);
	//if (retval != SUCCESS) {
	//	LOG_ERROR;
	//	goto _exit;
	//}
	
	retval = system("( sleep 10; /sbin/reboot ) &");
	LOG_INFO("FW Recover operation started, system will reboot in 10s...\n\n");
	
_exit:
	LOG_TRACE("Lib return: %d", retval);
	return retval?FAILED:SUCCESS;
}

int ocs_fwup_getstatus(int *status)
{
	const char *statusnames[FWUP_STATUS_MAX] = FWUP_STATUS_NAMES;
	char txtline[64];
	int retval = SUCCESS;
	FILE *in_fd;
	int i = 0;

	if (status == NULL) {
		LOG_ERR(errno, "Status parameter is NULL, nothing to do\n");
		return FAILED;
	}
	
	remove_mounts();
	retval = setup_imagestore();
	if (retval == SUCCESS) {
		in_fd = fopen(FWUP_IMAGESTORE_CFGFILE, "r");
		if ( in_fd == NULL ) {
			LOG_ERR(errno, "Failed to open fwupgrade config file\n");
			retval = FAILED;
			goto _exit_fn;
		}
		
		while (!feof(in_fd)) {
			if (fgets(txtline, 64, in_fd) != NULL) {
				LOG_TRACE("Read line: %s\n", txtline);
				if (strncmp(txtline, "UPGRADE_STATUS", 14) != 0)
					continue;		
			}
			
			LOG_TRACE("FWUpgrade status: %s\n", strstr(txtline, "=")+1);
			for (i = 0; i < FWUP_STATUS_MAX; i++) {
				if (strncmp(statusnames[i], strstr(txtline, "=")+1, strlen(statusnames[i])) == 0) {
					*status = i;
					break;
				}
			}
			break;
		}
		fclose(in_fd);
		remove_mounts();
	}

_exit_fn:	
	return retval;
}

int ocs_fwup_getlist(char *list)
{
	char txtline[64];
	int retval = SUCCESS;
	FILE *in_fd;
	int i = 0;

	if (list == NULL) {
		LOG_ERR(errno, "List parameter is NULL, nothing to do\n");
		return FAILED;
	}
	list[0] = 0;
	
	remove_mounts();
	retval = setup_imagestore();
	if (retval != SUCCESS)
		return FAILED;
	
	for (i=FWUP_PKGID_ROLLBACK; i<=FWUP_PKGID_UPGRADE; i++) {
		snprintf(txtline, 63, "%s/%s/pkg.manifest", FWUP_IMAGESTORE_MOUNTPOINT, pkgnames[i]);
		in_fd = fopen(txtline, "r");
		if ( in_fd == NULL ) {
			LOG_TRACE(errno, "Failed to open manifest file\n");
			strcat(list, "none,");
		}
		else {		
			while (!feof(in_fd)) {
				if (fgets(txtline, 64, in_fd) != NULL) {
					LOG_TRACE("Read line: %s\n", txtline);
					if (strncmp(txtline, "PACKAGE_VERSION", 15) != 0)
						continue;
				}
				txtline[strlen(txtline)-1] = ',';
				LOG_TRACE("Package version: %s\n", strstr(txtline, "=")+2);
				strcat(list, strstr(txtline, "=")+2);
				break;
			}
			fclose(in_fd);
		}
	}
	remove_mounts();
	return retval;
}

/******************************************************************************
*   Function Name: lib_getversion
*   Purpose:  Return library version
*   Comments/Notes:
*******************************************************************************/
int ocs_fwup_libgetversion(u_int32_t *ver)
{
    *ver = VERSION_MAKEWORD(SOLIB_VERSION_MAJOR, 
                            SOLIB_VERSION_MINOR, 
                            SOLIB_VERSION_REVISION, 
                            SOLIB_VERSION_BUILD);
    
    return (SUCCESS);
}
