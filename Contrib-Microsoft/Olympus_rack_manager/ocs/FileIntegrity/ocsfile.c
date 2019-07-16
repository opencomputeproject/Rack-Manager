// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/sendfile.h>
#include <openssl/evp.h>
#include "ocsfile.h"
#include "ocslog.h"
#include "ocslock.h"


/**
 * The length of the temp file path.
 */
static const int TEMP_PATH_LEN = strlen (TEMP_PATH);

/**
 * The buffer length necessary to handle generating
 */
static const int PATH_BUF_LEN = MAX_PATH_LEN + strlen (TEMP_PATH) + 5;

#define	GET_WRITE_LOCK	\
	if (ocs_lock (OCSFILE_WRITE) != 0) { \
		log_fnc_err (-1, "Failed to acquire file write lock."); \
		return -1; \
	}


static int ocs_file_validate_file (const char *path);

/**
 * Convert a file path to a file name by replacing the '/' characters.
 *
 * @param path A pointer to the path to convert.  The conversion will modify the path buffer.
 */
static void ocs_file_convert_path_to_file (char *path)
{
	do {
		path = strchr (path, '/');
		if (path) {
			*path = '_';
			path++;
		}
	} while (path);
}

/**
 * Convert a file name to a file path by restoring the '/' characters.
 *
 * @param name A pointer to the file name to convert.  The conversion will modify the path buffer.
 */
static void ocs_file_convert_file_to_path (char *name)
{
	do {
		name = strchr (name, '_');
		if (name) {
			*name = '/';
			name++;
		}
	} while (name);
}

/**
 * Get the temporary file for a specified system file.
 *
 * @param dest The system file.
 * @param tmp_path The path to the temporary file.  This buffer must be at least PATH_BUF_LEN in
 * size.
 */
static void ocs_file_get_temp_path (const char *dest, char *tmp_path)
{
	strcpy (tmp_path, TEMP_PATH);
	strcat (tmp_path, dest);
	strcat (tmp_path, ".tmp");

	ocs_file_convert_path_to_file (tmp_path + TEMP_PATH_LEN);
}

/**
 * Get the hash file for a specified system file.
 *
 * @param dest The system file.
 * @param hash_path The path to the hash file.  This buffer must be at least PATH_BUF_LEN in size.
 */
static void ocs_file_get_hash_path (const char *dest, char *hash_path)
{
	strcpy (hash_path, TEMP_PATH);
	strcat (hash_path, dest);
	strcat (hash_path, ".md5");

	ocs_file_convert_path_to_file (hash_path + TEMP_PATH_LEN);
}

/**
 * Remove any existing file, create a new one, and open it for writing.
 *
 * @param path The path to the file that should be created.
 * @param mode The permissions to assign to the file.
 * @param uid The owner user ID for the new file.
 * @param gid The group ID for the new file.
 *
 * @return The file descriptor of the new file or a negative error code.
 */
static int ocs_file_create_file (const char *path, mode_t mode, uid_t uid, gid_t gid)
{
	int fd;
	int status;

	status = unlink (path);
	if ((status != 0) && (errno != ENOENT)) {
		status = errno;
		log_fnc_err (status, "Failed to remove old file %s.", path);
		return -status;
	}

	fd = open (path, O_WRONLY | O_CREAT);
	if (fd < 0) {
		status = errno;
		log_fnc_err (status, "Failed to create file %s.", path);
		return -status;
	}

	status = fchmod (fd, mode);
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to set permissions for new file %s.", path);
		close (fd);
		return -status;
	}

	/* We try to set the owner/group, but this may fail for unprivileged users. */
	fchown (fd, uid, gid);

	return fd;
}

/**
 * Open the temporary file for writing.  The file will be created or truncated, as necessary.
 *
 * @param dest The system file requiring a temporary version.
 * @param tmp_path An optional container to hold the path of the temporary file.  This must be at
 * least PATH_BUF_LEN in size.
 *
 * @return The temporary file descriptor or a negative error code.
 */
static int ocs_file_open_temp_file (const char *dest, char *tmp_path)
{
	char tmp_name_buf[PATH_BUF_LEN];
	char *tmp_name = tmp_name_buf;
	int fd;
	int status;
	struct stat sys_file;

	if (tmp_path != NULL) {
		tmp_name = tmp_path;
	}

	fd = open (dest, O_RDWR);
	if (fd < 0) {
		status = errno;
		log_fnc_err (status, "Failed access check for system file %s.", dest);
		return -status;
	}

	status = fstat (fd, &sys_file);
	close (fd);
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to determine permissions of system file %s.", dest);
		return -status;
	}

	status = ocs_file_validate_file (dest);
	if ((status != 0) && (status != ENOENT)) {
		log_fnc_err (status, "Failed to verify file integrity before creating a temp file for %s.",
			dest);
		return -status;
	}
	sync ();

	ocs_file_get_temp_path (dest, tmp_name);
	return ocs_file_create_file (tmp_name, sys_file.st_mode, sys_file.st_uid, sys_file.st_gid);
}

/**
 * Get the hash for the temporary file and store in the hash file.
 *
 * @param dest The system file whose temporary file is being hashed.
 * @param temp The path to the temporary file.  If this is null, the path with be derived from the
 * system file.
 *
 * @return 0 if the hash was successfully calculated and stored or an error code.
 */
static int ocs_file_write_temp_file_hash (const char *dest, const char *temp)
{
	int status;
	uint8_t *hash;
	size_t length;
	char tmp_path_buf[PATH_BUF_LEN];
	const char *tmp_path = temp;
	char hash_path[PATH_BUF_LEN];
	int fd;
	struct stat tmp_file;

	if (tmp_path == NULL) {
		ocs_file_get_temp_path (dest, tmp_path_buf);
		tmp_path = tmp_path_buf;
	}

	status = stat (tmp_path, &tmp_file);
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to get information for temp file %s.", tmp_path);
		return status;
	}

	ocs_file_get_hash_path (dest, hash_path);
	fd = ocs_file_create_file (hash_path, tmp_file.st_mode, tmp_file.st_uid, tmp_file.st_gid);
	if (fd < 0) {
		return -fd;
	}

	status = ocs_file_get_file_hash (tmp_path, &hash, &length);
	if (status != 0) {
		close (fd);
		return status;
	}

	status = ocs_file_write (fd, hash, length);
	free (hash);
	close (fd);
	if (status != 0) {
		log_fnc_err (status, "Failed to write hash file %s.", hash_path);
		return status;
	}

	return 0;
}

/**
 * Make the temp file the active system file.
 *
 * @param path The path to the system file that will be replaced with the temp file.
 * @param tmp_path The path to the temp file that will become the active system file.
 *
 * @return 0 if the temp file was successfully copied or an error code.
 */
static int ocs_file_activate_temp_file (const char *path, const char *tmp_path)
{
	int status;

	ocs_condsignal (OCSFILE_WRITE);

	status = ocs_file_write_temp_file_hash (path, tmp_path);
	if (status != 0) {
		return status;
	}
	sync ();

	return ocs_file_copy_file (tmp_path, path);
}

/**
 * Read the stored hash for a file.
 *
 * @param path The path of the of file to get the stored hash for.
 * @param mdsum A pointer to a buffer that will be dynamically allocated to hold the file hash.  The
 * caller must free this memory on successful return.
 * @param length A pointer to the length of the output hash buffer.
 *
 * @return 0 if the hash was successfully read.
 */
static int ocs_file_read_hash (const char *path, uint8_t **mdsum, size_t *length)
{
	char hash_path[PATH_BUF_LEN];
	int fd;
	int status;

	if ((path == NULL) || (mdsum == NULL) || (length == NULL)) {
		log_fnc_err (EINVAL, "Null parameter provided.");
		return EINVAL;
	}

	ocs_file_get_hash_path (path, hash_path);

	fd = open (hash_path, O_RDONLY);
	if (fd < 0) {
		fd = errno;
		log_fnc_err (fd, "Failed to open hash file for %s.", path);
		return fd;
	}

	*mdsum = malloc (EVP_MAX_MD_SIZE);
	if (*mdsum == NULL) {
		status = ENOMEM;
		log_fnc_err (status, "Failed to allocate buffer for file hash.");
		close (fd);
		return status;
	}

	status = read (fd, *mdsum, EVP_MAX_MD_SIZE);
	if (status < 0) {
		status = errno;
		log_fnc_err (status, "Failed to read hash for %s.", path);
		free (*mdsum);
		*mdsum = NULL;
	}
	else {
		*length = status;
		status = 0;
	}

	close (fd);
	return status;
}

/**
 * Check if the file is valid.
 *
 * @param path The path of the file to check.
 *
 * @return 0 if the file is valid, -1 if the file is not valid, or an error code.
 */
static int ocs_file_check_file (const char *path)
{
	uint8_t *hash = NULL;
	size_t hash_len;
	uint8_t *file_hash = NULL;
	size_t file_hash_len;
	int status;

	if (path == NULL) {
		log_fnc_err (EINVAL, "No file path provided.");
		return EINVAL;
	}

	status = ocs_file_read_hash (path, &hash, &hash_len);
	if (status != 0) {
		return status;
	}

	status = ocs_file_get_file_hash (path, &file_hash, &file_hash_len);
	if (status != 0) {
		free (hash);
		return status;
	}

	if (hash_len != file_hash_len) {
		status = -1;
	}
	else if (memcmp (hash, file_hash, hash_len) != 0) {
		status = -1;
	}
	else {
		status = 0;
	}

	free (hash);
	free (file_hash);

	return status;
}

/**
 * Recover an invalid system file.
 *
 * @param path The path to the file that should be recovered.
 *
 * @return 0 if the recovery was successful or an error code.
 */
static int ocs_file_recover_file (const char *path)
{
	char tmp_path[PATH_BUF_LEN];

	/*
	 * If the system file is bad, that means either the hash file or the system file is corrupt.
	 * Both of these writes happen after the temp file is finished being written to, so the temp
	 * file must be good.  To recover the system file, we simply refresh the hash file, then make
	 * the temp file the active one.
	 */
	ocs_file_get_temp_path (path, tmp_path);
	return ocs_file_activate_temp_file (path, tmp_path);
}

/**
 * Validate a file to make sure it is not corrupt, and recover it if it is.
 *
 * @param path The path of the file to check.
 *
 * @return 0 if the file is known to be valid or an error code.
 */
static int ocs_file_validate_file (const char *path)
{
	int status = ocs_file_check_file (path);
	if (status > 0) {
		log_fnc_err (status, "Failed to determine if file %s was valid.", path);
		return status;
	}

	if (status != 0) {
		log_info ("Recovering corrupt file %s.", path);
		status = ocs_file_recover_file (path);
		if (status != 0) {
			log_fnc_err (status, "Failed to recover invalid file %s.", path);
			return status;
		}
	}

	log_info ("File %s is valid.", path);
	return 0;
}

/**
 * Check that ownership of the temporary files match the original file and updated it if they do
 * not.  This call may fail if not called in the context of a privileged user.
 *
 * @param path The path of the system file whose temp files should be checked.
 */
static void ocs_file_validate_ownership (const char *path)
{
	struct stat sys_file;
	char check_path[PATH_BUF_LEN];
	int status;

	status = stat (path, &sys_file);
	if (status != 0) {
		log_fnc_err (errno, "Failed to get system file information.");
		return;
	}

	ocs_file_get_temp_path (path, check_path);
	chown (check_path, sys_file.st_uid, sys_file.st_gid);

	ocs_file_get_hash_path (path, check_path);
	chown (check_path, sys_file.st_uid, sys_file.st_gid);
}

/**
 * Copy a file from one location to another.
 *
 * @param src The path of the file to copy.
 * @param dest The destination path of the copy.
 *
 * @return 0 if the file was copied successfully or an error code.
 */
int ocs_file_copy_file (const char *src, const char *dest)
{
	int src_fd = -1;
	int dest_fd = -1;
	int status;
	struct stat src_file;

	status = stat (src, &src_file);
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to determine source file size.");
		return status;
	}

	src_fd = open (src, O_RDONLY);
	if (src_fd < 0) {
		status = errno;
		log_fnc_err (status, "Failed to open source file %s.", src);
		return status;
	}

	dest_fd = open (dest, O_WRONLY | O_CREAT | O_TRUNC);
	if (dest_fd < 0) {
		status = errno;
		log_fnc_err (status, "Failed to open destination file %s.", dest);
		goto copy_exit;
	}

	status = sendfile (dest_fd, src_fd, NULL, src_file.st_size);
	if (status < 0) {
		status = errno;
		log_fnc_err (status, "Failed to copy file from %s to %s.", src, dest);
	}
	else if (status != src_file.st_size) {
		status = -1;
		log_fnc_err (status, "Incomplete file written from %s to %s.", src, dest);
	}
	else {
		status = 0;
	}

copy_exit:
	close (src_fd);
	close (dest_fd);
	return status;
}

/**
 * Get the MD5 hash for a file.
 *
 * @param path The path to the file that should be hashed.
 * @param mdsum A pointer to a buffer that will be dynamically allocated to hold the file hash.  The
 * caller must free this memory on successful return.
 * @param length A pointer to the length of the output hash buffer.
 *
 * @return 0 if the file was successfully hashed or an error code.
 */
int ocs_file_get_file_hash (const char *path, uint8_t **mdsum, size_t *length)
{
	int fd;
	char block[1024];
	int bytes;
	EVP_MD_CTX hash;
	unsigned int hash_len;
	int status;

	if ((path == NULL) || (mdsum == NULL) || (length == NULL)) {
		log_fnc_err (EINVAL, "Null parameter supplied for file hashing.");
		return EINVAL;
	}

	fd = open (path, O_RDONLY);
	if (fd < 0) {
		status = errno;
		log_fnc_err (status, "Failed to open file %s for hashing.", path);
		return status;
	}

	EVP_MD_CTX_init (&hash);
	if (EVP_DigestInit_ex (&hash, EVP_md5 (), NULL) == 0) {
		status = -1;
		log_fnc_err (status, "Failed to initialize hash algorithm.");
		goto hash_cleanup;
	}

	do {
		bytes = read (fd, block, sizeof (block));
		if (bytes > 0) {
			if (EVP_DigestUpdate (&hash, block, bytes) == 0) {
				status = -1;
				log_fnc_err (status, "Failed to update hash for %d bytes of data.", bytes);
				goto hash_cleanup;
			}
		}
	} while (bytes > 0);

	if (bytes < 0) {
		status = errno;
		log_fnc_err (status, "Failed to read from file %s.", path);
		goto hash_cleanup;
	}

	*mdsum = malloc (EVP_MAX_MD_SIZE);
	if (*mdsum == NULL) {
		status = ENOMEM;
		log_fnc_err (status, "Failed to allocate buffer for file hash.");
		goto hash_cleanup;
	}

	if (EVP_DigestFinal_ex (&hash, *mdsum, &hash_len) == 0) {
		status = -1;
		free (*mdsum);
		*mdsum = NULL;
		log_fnc_err (status, "Failed to finalize hash for file %s.", path);
	}
	else {
		*length = hash_len;
		status = 0;
	}

hash_cleanup:
	close (fd);
	EVP_MD_CTX_cleanup (&hash);

	return status;
}

/**
 * Verify that a file is good and restore the file if it is not.
 *
 * @param path The path to the file to validate.
 *
 * @return 0 if the file is known be valid or an error code.
 */
int ocs_file_ensure_valid (const char *path)
{
	int status;

	if (strlen (path) > MAX_PATH_LEN) {
		return ENAMETOOLONG;
	}

	GET_WRITE_LOCK;
	status = ocs_file_validate_file (path);
	ocs_unlock (OCSFILE_WRITE);

	return status;
}

/**
 * Ensure that all safely written files are good and recover any that are not.
 *
 * @return 0 if all files are now known to be valid or an error code.
 */
int ocs_file_validate_all ()
{
	int status;
	DIR *temp_dir;
	struct dirent *entry;
	char path[NAME_MAX + 1];
	char *pos;
	int failed = 0;

	GET_WRITE_LOCK;

	temp_dir = opendir (TEMP_PATH);
	if (temp_dir == NULL) {
		failed = errno;
		log_fnc_err (failed, "Failed to open temp directory to discover files to check.");
		goto validate_exit;
	}

	entry = readdir (temp_dir);
	while (entry != NULL) {
		// We will try to validate any file that has a hash file present.
		int len = strlen (entry->d_name);
		if (len >= 4) {
			pos = entry->d_name + len - 4;
		}
		else {
			pos = entry->d_name;
		}

		if (strcmp (".md5", pos) == 0) {
			strcpy (path, entry->d_name);
			path[len - 4] = '\0';
			ocs_file_convert_file_to_path (path);

			status = ocs_file_validate_file (path);
			if (status != 0) {
				log_fnc_err (status, "Failed to validate file %s.", path);
				failed = -1;
			}
			else {
				ocs_file_validate_ownership (path);
			}
		}

		entry = readdir (temp_dir);
	}

	closedir (temp_dir);

validate_exit:
	ocs_unlock (OCSFILE_WRITE);
	return failed;
}

/**
 * Safely write data to a file to ensure file corruption can be detected.  A temporary file will be
 * written, hashed, and copied to the destination as an atomic operation.  Partial file writes or
 * appending data to a file cannot be achieved with this function.
 *
 * @param dest The path to the system file to write.
 * @param data The data to write to the file.
 * @param length The length of the data to be written.
 *
 * @return 0 if the operation completed successfully or an error code.
 */
int ocs_file_write_complete_file (const char *dest, const uint8_t *data, size_t length)
{
	int tmp_file;
	char tmp_path[PATH_BUF_LEN];
	int status;

	if ((dest == NULL) || (data == NULL)) {
		log_fnc_err (EINVAL, "Null parameter provided.");
		return EINVAL;
	}

	if (strlen (dest) > MAX_PATH_LEN) {
		return ENAMETOOLONG;
	}

	GET_WRITE_LOCK;

	tmp_file = ocs_file_open_temp_file (dest, tmp_path);
	if (tmp_file < 0) {
		status = -tmp_file;
		goto write_exit;
	}

	status = ocs_file_write (tmp_file, data, length);
	close (tmp_file);
	if (status != 0) {
		log_fnc_err (status, "Failed to write temporary file %s.", tmp_path);
		goto write_exit;
	}
	sync ();

	status = ocs_file_activate_temp_file (dest, tmp_path);

write_exit:
	ocs_unlock (OCSFILE_WRITE);
	return status;
}

/**
 * Open the temporary file to be written to by the calling application.
 *
 * @param dest The path to the system file that a temporary file is needed for.
 * @param temp The file descriptor for the temporary file that was opened.  This will be an empty
 * file.
 *
 * @return 0 if the file was opened successfully or an error code.
 */
int ocs_file_open_temp (const char *dest, int *temp)
{
	if ((dest == NULL) || (temp == NULL)) {
		log_fnc_err (EINVAL, "Null parameter provided.");
		return EINVAL;
	}

	if (strlen (dest) > MAX_PATH_LEN) {
		return ENAMETOOLONG;
	}

	GET_WRITE_LOCK;
	*temp = ocs_file_open_temp_file (dest, NULL);
	ocs_unlock (OCSFILE_WRITE);

	if (*temp < 0) {
		return -*temp;
	}

	return 0;
}

/**
 * Write a block of data to a file at the current file position.
 *
 * @param fd The file descriptor to write to.
 * @param data The data to write to the file.
 * @param length The amount of data to write.
 *
 * @return 0 if the data was completely written to the file or an error code.
 */
int ocs_file_write (int fd, const uint8_t *data, size_t length)
{
	const uint8_t *pos = data;
	int remaining = length;
	while (remaining > 0) {
		int bytes = write (fd, pos, remaining);
		if (bytes > 0) {
			remaining -= bytes;
			pos += bytes;
		}
		else if (bytes < 0) {
			remaining = -errno;
		}
	}

	return -remaining;
}

/**
 * Commit the data written to the temporary file to the destination system file.  The commit will
 * happen as an atomic operation and the temporary file will be closed.
 *
 * @param dest The path to the system file to commit.
 * @param temp The file descriptor for the temporary file to commit as the new file.
 *
 * @return 0 if the operation completed successfully or an error code.
 */
int ocs_file_commit (const char *dest, int temp)
{
	char tmp_path[PATH_BUF_LEN];
	int status;

	if (dest == NULL) {
		log_fnc_err (EINVAL, "No destination file provided.");
		return EINVAL;
	}

	if (strlen (dest) > MAX_PATH_LEN) {
		return ENAMETOOLONG;
	}

	GET_WRITE_LOCK;

	close (temp);
	sync ();

	ocs_file_get_temp_path (dest, tmp_path);
	status = ocs_file_activate_temp_file (dest, tmp_path);

	ocs_unlock (OCSFILE_WRITE);
	return status;
}
