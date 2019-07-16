// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef OCSFILE_H_
#define OCSFILE_H_

#include <stddef.h>
#include <stdint.h>
#include <dirent.h>


/**
 * The path to temporary files and file hashes.
 */
#define	TEMP_PATH	"/var/local/ocs_tmp/"

/**
 * The maximum path length supported.
 */
#define MAX_PATH_LEN	NAME_MAX


int ocs_file_copy_file (const char *src, const char *dest);
int ocs_file_get_file_hash (const char *path, uint8_t **mdsum, size_t *length);
int ocs_file_ensure_valid (const char *path);
int ocs_file_validate_all ();
int ocs_file_write_complete_file (const char *dest, const uint8_t *data, size_t length);
int ocs_file_open_temp (const char *dest, int *temp);
int ocs_file_write (int fd, const uint8_t *data, size_t length);
int ocs_file_commit (const char *dest, int temp);


#endif /* OCSFILE_H_ */
