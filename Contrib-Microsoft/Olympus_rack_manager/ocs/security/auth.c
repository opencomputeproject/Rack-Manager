// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

 /*
 * auth.c

 *
 *  Created on: Jul 7, 2016
 *      Author: admin_user
 */

#define _GNU_SOURCE

#include <crypt.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <ocslock.h>
#include <ocslog.h>
#include "auth.h"

void __attribute__((constructor)) initialize(void);

static int delete_entry(char *filename, const char *username);
static int shadow_append(struct spwd *sp);
static void generate_salt(char *salt);

int file_restore(char *filename);
int file_remove(char *filename);
int file_exists(const char *filename, int *error_code);
int file_io_op(const auth_file_op action, const char *filename, long length, char *buffer);

/******************************************************************************
*   Function Name: 	app_specific_error
*   Purpose: 		convert application error into char pointer
*   In parameters: 	err, error offset
*   Return value:  	pointer to error or default error
*   Comments/Notes:
*******************************************************************************/
char * app_specific_error(int err) {

	if (err < MAX_ERROR_SUPPORT && err > 0)
		return (char *)app_error_str[err];
	else
		return (char *)app_error_str[DEFAULT_ERR_IDX];

}

/******************************************************************************
*   Function Name: 	salt_size
*   Purpose: 		gets the size of the salt used for passwd encryption.
*   In parameters: 	salt, input array consisting of string to search
*   Return value:  	failed if something failed, salt location otherwise
*   Comments/Notes: supports salt up to maximum salt for this library
*******************************************************************************/
int salt_size(char *salt) {
	int i = 3;
	for (; i <= SALT_SIZE; i++)
		if (salt[i] == '$') {
			return i;
		}
	return -1;
}

/******************************************************************************
*   Function Name: 		current_day_count
*   Purpose: 			day count used for password aging.
*   Output parameters: 	dcnt: day count
*   Comments/Notes:
*******************************************************************************/
static void current_day_count(int *dcnt) {
	time_t date_time;

	/* get current time */
	date_time = time(NULL);

	date_time = (((date_time / 60) / 60) / 24);

	*dcnt = (int)date_time;
}

/******************************************************************************
*   Function Name: 	ocs_group_id
*   Purpose: 		check if target group name matches ocs group name
*   In parameters: 	groupname, name of target ocs group
*	Out parameters: g_id, Id of group
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes: does array lookup on group_names
*******************************************************************************/
int ocs_group_id(const char *groupname, int *g_id) {
	if (groupname == NULL) {
		log_fnc_err(FAILURE, "%s: ocs_group_id: null group name.\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	int idx = 0;
	for (; idx < MAX_GROUP_SUPPORT; idx++) {
		if (strcmp(groupname, group_names[idx]) == SUCCESS) {
			*g_id = ocs_group_ids[idx];
			return SUCCESS;
		}
	}

	return UNKNOWN_ERROR;
}

/******************************************************************************
*   Function Name: 	ocs_group_member
*   Purpose: 		check if user is a member of a given ocs group
*   In parameters: 	groupname, name of target ocs group
*					username, name of user to check
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes: ocs groups do not use linux groups in tradition sense,
*  					it just enums users with primary group id matching predefined
*  					ocs group id
*******************************************************************************/
int ocs_group_member(const char *groupname, const char *username) {

	if (username == NULL || groupname == NULL) {
		log_fnc_err(FAILURE, "%s: invalid input group or user name\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	int g_id = 0;
	int *group_ptr = &g_id;
	if (ocs_group_id(groupname, group_ptr) != 0) {
		log_fnc_err(FAILURE, "%s: non-ocs group group_member.\n", app_specific_error(UNSUPPORTED));
		return UNSUPPORTED;
	}

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t length = sizeof(buffer);

	if (getpwnam_r(username, &pw, buffer, length, &result) == SUCCESS) {
		if (result != NULL) {
			if (pw.pw_gid == g_id)
				return SUCCESS;
		}
		else {
			log_fnc_err(FAILURE, "%s: group_member() getpwnam_r returned null.\n", app_specific_error(NULL_OBJECT));
			return NULL_OBJECT;
		}
	}

	return FAILURE;
}

/******************************************************************************
*   Function Name: 	group_members
*   Purpose: 		returns all members in a given group
*   In parameters: 	groupname, name of target group
* 	Out parameters:	length, pointer to size of output char array
*					members, pointer to user name char array
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int ocs_group_members(const char *groupname, const int *length, char *members) {

	int response = 0;

	if (groupname == NULL || members == NULL) {
		log_fnc_err(FAILURE, "%s: invalid input group name\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	int gid = 0;
	int *group_ptr = &gid;
	if (ocs_group_id(groupname, group_ptr) != 0) {
		log_fnc_err(FAILURE, "%s: non-ocs group group_member.\n", app_specific_error(UNSUPPORTED));
		return UNSUPPORTED;
	}

	FILE *fhandle;

	fhandle = fopen(USER_FILE, "r");

	if (!fhandle) {
		log_fnc_err(FAILURE, "%s: read and append open passwd failed\n", app_specific_error(FILE_IO_ERROR));
		return FILE_IO_ERROR;
	}

	int idx = 0;
	int count = 0;
	struct passwd *pwd;

	while ((pwd = fgetpwent(fhandle))) {
		if (pwd->pw_gid == gid) {

			idx += (strlen(pwd->pw_name) + 1);
			if (idx > *length) {
				log_fnc_err(FAILURE, "%s: input members buffer too small for user list\n", app_specific_error(INPUT_BUFF_SIZE));
				response = INPUT_BUFF_SIZE;
				break;
			}

			if (count != 0)
				strncat(members, ", ", sizeof(char));

			strncat(members, pwd->pw_name, USERNAME_MAX_LEN);

			count++;

		}
	}

	fclose(fhandle);

	return response;

}

int ocs_change_role(const char *username, const char *groupname) {

	if (username == NULL || groupname == NULL) {
		log_fnc_err(FAILURE, "%s: invalid input group or user name\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	/* exit if not root group id */
	if (getegid() != 0) {
		log_fnc_err(FAILURE, "%s: only admin can remove user.",
			app_specific_error(FUNCTION_ERR));
		return FAILURE;
	}

	FILE *fhandle;
	int response = 0;
	int g_id = 0;
	int *group_ptr = &g_id;
	if (ocs_group_id(groupname, group_ptr) != 0) {
		log_fnc_err(FAILURE, "%s: non-ocs group group_member. \n", app_specific_error(UNSUPPORTED));
		return UNSUPPORTED;
	}

	if (strcmp(username, "root") == SUCCESS) {
		log_fnc_err(FAILURE, "%s: root can only be admin\n",
			app_specific_error(INVALID_OPERATION));
		return INVALID_OPERATION;
	}

	struct passwd pw;
	struct passwd *result;

	int lck_held = 0;

	char buffer[256];
	size_t length = sizeof(buffer);

	if ((response = getpwnam_r(username, &pw, buffer, length, &result)) == SUCCESS) {
		if (result != NULL) {
			if (pw.pw_gid == g_id) {
				return response;
			}
			else {
				pw.pw_gid = g_id;

				/* ocs lock and hold so u_id isn't stolen by concurrent add_user */
				if ((response = ocs_lock(USR_ACCNT)) != SUCCESS) {
					log_fnc_err(FAILURE, "%s: unable to obtain  ocs_lock(USR_ACCNT) error: %d",
						app_specific_error(FUNCTION_ERR), response);
					goto end_clean;
				}

				lck_held = 1;

				/* remove user record from passwd only */
				if ((response = delete_entry(USER_FILE, username)) != 0) {
					/* will auto roll back on write failure */
					log_fnc_err(FAILURE, "%s: unable to remove user from: %s\n",
						app_specific_error(response), USER_FILE);
					goto end_clean;
				}

				/* add updated user to passwd only */
				fhandle = fopen(USER_FILE, "a+");

				if (!fhandle) {
					log_fnc_err(FAILURE, "%s: read and append open passwd failed\n",
						app_specific_error(FILE_IO_ERROR));
					response = FILE_IO_ERROR;
					goto end_clean;
				}

				if ((response = putpwent(&pw, fhandle)) != 0) {
					log_fnc_err(FAILURE, "%s: unable to add user to passwd: %s error %d\n",
						app_specific_error(FUNCTION_ERR), username, response);
				}

				fflush(fhandle);
				fclose(fhandle);

				memset(buffer, 0, sizeof(buffer));
				result = NULL;

				if ((response = getpwnam_r(username, &pw, buffer, length, &result)) == SUCCESS) {
					if (result != NULL) {
						if (pw.pw_gid == g_id) {
							response = file_remove(USER_FILE);
						}
						else {
							if ((response = file_restore(USER_FILE)) == SUCCESS) {
								log_fnc_err(FAILURE, "%s: roll back user modification due to function error in ocs_change_role.\n",
									app_specific_error(FUNCTION_ERR));
								response = FUNCTION_ERR;
							}
						}
					}
					else {
						log_fnc_err(FAILURE, "%s: null error getting second getpwnam_r in ocs_change_role.\n",
							app_specific_error(FUNCTION_ERR));
						response = FUNCTION_ERR;
					}
				}
				else {
					log_fnc_err(FAILURE, "%s: error getting second getpwnam_r in ocs_change_role.\n",
						app_specific_error(FUNCTION_ERR));
					response = FUNCTION_ERR;
				}
			}
		}
		else {
			log_fnc_err(FAILURE, "%s: null error getting getpwnam_r in ocs_change_role.\n",
				app_specific_error(FUNCTION_ERR));
			response = FUNCTION_ERR;
		}
	}

end_clean:
	if (lck_held > 0)
		if (ocs_unlock(USR_ACCNT) != SUCCESS) {
			log_fnc_err(FAILURE, "ocs_change_role - ocs_unlock(USR_ACCNT) failed\n");
		}

	return response;
}

/******************************************************************************
*   Function Name: 	check_root
*   Purpose: 		checks if uid is zero
*   Return value:  	FAILED user not verified as root, SUCCESS user is root
*   Comments/Notes:
*******************************************************************************/
int check_root() {
	if (geteuid() == 0)
		return 0;
	else
		return 1;
}

/******************************************************************************
*   Function Name: 	get_username_from_id
*   Purpose: 		returns user name from user id
*   In parameters: 	user_id, id of target group
*					lenght, size of input char array
* 	Out parematers:	username, pointer to username char array
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_username_from_id(const uid_t user_id, const size_t length, char *username) {

	if (username == NULL) {
		log_fnc_err(FAILURE, "%s: provide user name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	if (user_id == 0) {
		strcpy(username, "root");
		return 0;
	}

	int response;

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t len = sizeof(buffer);
	if ((response = getpwuid_r(user_id, &pw, buffer, len, &result)) == SUCCESS) {
		if (result != NULL) {
			strncpy(username, pw.pw_name, length);
			return response;
		}
		else {
			log_fnc_err(FAILURE, "%s: getpwuid_r null object user id: %d", app_specific_error(NULL_OBJECT), user_id);
			return NULL_OBJECT;
		}
	}

	return FAILURE;
}

/******************************************************************************
*   Function Name: 	get_groupname_from_id
*   Purpose: 		returns group name from group id
*   In parameters: 	group_id, id of target group
*					length, size of input char array
* 	Out parameters:	groupname, pointer to group name array
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_groupname_from_id(const gid_t group_id, const size_t length, char *groupname) {

	int idx = 0;
	for (; idx < MAX_GROUP_SUPPORT; idx++) {
		if (group_id == ocs_group_ids[idx]) {
			strncpy(groupname, group_names[idx], length);
			return SUCCESS;
		}
	}

	return FAILURE;
}

/******************************************************************************
*   Function Name: 	get_groupid_from_name
*   Purpose: 		returns group id from group name
*   In parameters: 	username, pointer to groupname array
* 	Out parameters:	id, pointer to group id
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_groupid_from_name(const char *groupname, gid_t *id) {
	return ocs_group_id(groupname, (int*) id);
}

/******************************************************************************
*   Function Name: 	get_current_username
*   Purpose: 		returns user name of calling process
*   In parameters: 	username, pointer to username array
*					length, size of username pointer
* 	Out parameters:	username, user name of calling process
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_current_username(char *username, size_t length) {
	uid_t user_id = geteuid();
	return get_username_from_id(user_id, length, username);
}

/******************************************************************************
*   Function Name: 	get_user_id
*   Purpose: 		gets user id from user name
*   In parameters: 	username, input target username
* 	Out parameters:	userid, the pw_uid for the user
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_userid_from_name(const char *username, uid_t *userid) {

	int response;

	if (username == NULL) {
		log_fnc_err(FAILURE, "%s: username name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t length = sizeof(buffer);

	if ((response = getpwnam_r(username, &pw, buffer, length, &result)) == SUCCESS) {
		if (result != NULL) {
			*userid = pw.pw_uid;
			return response;
		}
		else {
			return NULL_OBJECT;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: getpwnam_r error: %s %d\n", app_specific_error(FUNCTION_ERR), username, response);
		return FUNCTION_ERR;
	}

	return FAILURE;

}

/******************************************************************************
*   Function 		add_user
*   Purpose: 		adds a user to the passwd, shadow and group file.
*   In parameters: 	populated spwd structure
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int add_user(const char *username, const char *groupname, const char *password) {

	FILE *fhandle;
	int response;
	int lck_held = 0;

	/* exit if not root group id */
	if (getegid() != 0) {
		log_fnc_err(FAILURE, "%s: only admin can remove user.",
			app_specific_error(FUNCTION_ERR));
		return FAILURE;
	}

	if (username == NULL || password == NULL) {
		log_fnc_err(FAILURE, "%s: provide valid username and password\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	uid_t userid;
	if (get_userid_from_name(username, &userid) == SUCCESS) {
		log_fnc_err(FAILURE, "%s: user already exists: %s Id: %d", app_specific_error(INVALID_OPERATION), username, userid);
		return INVALID_OPERATION;
	}

	int name_length = 0;
	unsigned char letter = 0x20;

	char* temp_user = (char *)username;
	/* check user name 0-9, A-Z, a-z) */
	while (*++temp_user) {
		letter = *temp_user;

		if ((letter >= 0x41 && letter <= 0x5A) ||
			(letter >= 0x30 && letter <= 0x39) ||
			(letter >= 0x61 && letter <= 0x7A)) {
		}
		else {
			log_fnc_err(FAILURE, "%s: illegal character in username\n", app_specific_error(INVALID_PARAM));
			return INVALID_PARAM;
		}

		name_length++;
	}

	if (name_length < USERNAME_MIN_LEN ||
		name_length > USERNAME_MAX_LEN) {
		log_fnc_err(FAILURE, "%s: illegal user name length: %s min length: %d max length: %d\n",
			app_specific_error(INVALID_PARAM),
			username, USERNAME_MIN_LEN, USERNAME_MAX_LEN);
		return INVALID_PARAM;
	}

	int groupid = -1;
	if ((response = ocs_group_id(groupname, &groupid)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: error: %d invalid group name: %s\n", app_specific_error(FUNCTION_ERR), response, groupname);
		return FUNCTION_ERR;
	}

	char homedir[USERNAME_MAX_LEN + 7];
	snprintf(homedir, sizeof(homedir), "/home/%s", username);

	struct passwd pw;

	pw.pw_name = (char *)username;
	pw.pw_passwd = (char*)"x"; /*x indicates etc/shadow */
	pw.pw_gid = groupid;
	pw.pw_gecos = "ocscli account";
	pw.pw_shell = USER_SHELL;
	pw.pw_dir = homedir;
	pw.pw_uid = groupid; /* pw_uid id 0, hack to make more root users */


	/* lock the pwd before getting the pid, to prevent dups*/
	if ((response = ocs_lock(USR_ACCNT)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: unable to obtain ocs_lock(USR_ACCNT) error: %d", app_specific_error(FUNCTION_ERR), response);
		goto end_clean;
	}

	lck_held = 1;

	fhandle = fopen(USER_FILE, "a+");

	if (!fhandle) {
		log_fnc_err(FAILURE, "%s: read and append open passwd failed\n", app_specific_error(FILE_IO_ERROR));
		response = FAILURE;
		goto end_clean;
	}

	/* if not admin, create user and group id */
	if (groupid != OCS_ADMIN_ID){
		struct passwd *pwd;
		pw.pw_uid = MIN_ID + 1;
		/* get avail uid */
		while ((pwd = fgetpwent(fhandle))) {
			if ((pwd->pw_uid >= pw.pw_uid) && (pwd->pw_uid < MAX_ID)) {
				pw.pw_uid = ++pwd->pw_uid;
			}
		}
	}

	if ((response = putpwent(&pw, fhandle)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: error: %d, unable to add user to passwd: %s\n",
			app_specific_error(FUNCTION_ERR), response, username);
	}

	if (fflush(fhandle) != SUCCESS || fclose(fhandle) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: error: %d, unable to flush and close passwd: %s\n",
			app_specific_error(FUNCTION_ERR), response, username);
	}

	/* update shadow */
	if (response == SUCCESS) {

		struct spwd sp;
		memset(&sp, 0, sizeof(sp));

		int daycnt = 0;
		current_day_count(&daycnt);

		/* generate a salt */
		char salt[40];
		char *saltptr = salt;
		generate_salt(saltptr);

		struct crypt_data data;
		data.initialized = 0;

		sp.sp_namp = pw.pw_name;
		sp.sp_pwdp = (char*)crypt_r((const char*)password, saltptr, &data);
		sp.sp_lstchg = daycnt;
		sp.sp_min = 0;
		sp.sp_max = 99999;
		sp.sp_warn = 7;
		sp.sp_inact = -1;
		sp.sp_expire = -1;
		sp.sp_flag = -1;

		response = shadow_append(&sp);

		if (response == SUCCESS) {
			if (mkdir(pw.pw_dir, 0755) == 0) {
				chown(pw.pw_dir, pw.pw_uid, pw.pw_gid);
				chmod(pw.pw_dir, 02755);
			}
		}

	}

end_clean:
	if (lck_held > 0)
		if (ocs_unlock(USR_ACCNT) != SUCCESS) {
			log_fnc_err(FAILURE, "add_user - ocs_unlock(USR_ACCNT) failed\n");
		}

	return response;

}


/******************************************************************************
*   Function Name: 	remove_user
*   Purpose: 		removes user from passwd, shodow, group file.
*   In parameters: 	username, target user to remove
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int remove_user(const char *username) {

	int response = 0;
	int lck_held = 0;

	if (username == NULL) {
		log_fnc_err(FAILURE, "%s: username name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	if (strcmp(username, "root") == SUCCESS) {
		log_fnc_err(FAILURE, "%s: root cannot be removed\n",
			app_specific_error(INVALID_OPERATION));
		return INVALID_OPERATION;
	}

	/* exit if not root group id */
	if (getegid() != 0) {
		log_fnc_err(FAILURE, "%s: only admin can remove user.",
			app_specific_error(FUNCTION_ERR));
		return FAILURE;
	}

	if ((response = ocs_lock(USR_ACCNT)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: unable to obtain ocs_lock(USR_ACCNT) error: %d",
			app_specific_error(FUNCTION_ERR), response);
		goto end_clean;
	}

	lck_held = 1;

	uid_t userid;
	if (get_userid_from_name(username, &userid) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: user does not exist: %s",
			app_specific_error(INVALID_OPERATION), username);
		response = INVALID_OPERATION;
		goto end_clean;
	}

	if ((response = delete_entry(USER_FILE, username)) != 0) {
		/* error reported in delete entry, just log info if needed */
		log_info("unable to remove user from: %s\n", USER_FILE);
		goto end_clean;
	}

	if ((response = delete_entry(SHADOW_FILE, username)) != 0) {
		log_info("unable to remove user from: %s\n", SHADOW_FILE);
		goto end_clean;
	}

	// remove the users home directory, but don't complain if it's not there.
	char homedir[USERNAME_MAX_LEN + 7];
	snprintf(homedir, sizeof(homedir), "/home/%s", username);
	remove(homedir);

	/* if the user doesn't exist delete the backups */
	if (get_userid_from_name(username, &userid) != SUCCESS) {
		if ((response = file_remove(USER_FILE)) != SUCCESS) {
			log_fnc_err(FAILURE, "%s: unable to remove backup file %s",
				app_specific_error(FUNCTION_ERR), USER_FILE);
			goto end_clean;
		}

		if ((response = file_remove(SHADOW_FILE)) != SUCCESS) {
			log_fnc_err(FAILURE, "%s: unable to remove backup file %s",
				app_specific_error(FUNCTION_ERR), SHADOW_FILE);
			goto end_clean;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: user still exists: %s",
			app_specific_error(FUNCTION_ERR), username);
		response = FUNCTION_ERR;
		goto end_clean;
	}


end_clean:
	if (lck_held > 0)
		if (ocs_unlock(USR_ACCNT) != SUCCESS) {
			log_fnc_err(FAILURE, "remove_user - ocs_unlock(USR_ACCNT) failed\n");
		}

	return response;
}

/******************************************************************************
*   Function Name: 	update_password
*   Purpose: 		updates user password in shadow file
*   In parameters: 	username, name of target user to update password
*					password, new unencrypted password
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int update_password(const char *username, const char *password) {

	int response = 0;
	int lck_held = 0;

	/* exit if not root group id */
	if (getegid() != 0) {
		log_fnc_err(FAILURE, "%s: only admin can remove user.",
			app_specific_error(FUNCTION_ERR));
		return FAILURE;
	}

	char buffer[256];
	struct spwd spw;
	struct spwd *result;
	getspnam_r(username, &spw, buffer, sizeof(buffer), &result);

	if (!result) {
		log_fnc_err(FAILURE, "%s: unable to locate user pwd\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	char salt[40];
	char *saltptr = salt;
	generate_salt(saltptr);

	int daycnt = 0;
	current_day_count(&daycnt);

	struct crypt_data data;
	data.initialized = 0;

	result->sp_pwdp = (char*)crypt_r((const char*)password, saltptr, &data);
	result->sp_lstchg = daycnt;
	result->sp_inact = -1;
	result->sp_expire = -1;

	/* lckpwdf isn't thread safe, using semaphore instead, and hold so uid isn't stolen by concurrent add_user */
	if ((response = ocs_lock(USR_ACCNT)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: unable to obtain ocs_lock(USR_ACCNT) error: %d", app_specific_error(FUNCTION_ERR), response);
		goto end_clean;
	}

	lck_held = 1;

	if ((response = delete_entry(SHADOW_FILE, username)) != SUCCESS) {
		/* delete entry will automatically restore if write fails */
		log_info("unable to remove user from: %s\n", SHADOW_FILE);
		goto end_clean;
	}

	response = shadow_append(result);

	if (response == SUCCESS) {
		/* verify success or restore */
		if ((response = verify_authentication(username, password)) != SUCCESS)
			file_restore(SHADOW_FILE);
		else
			file_remove(SHADOW_FILE);
	}

end_clean:
	if (lck_held > 0)
		if (ocs_unlock(USR_ACCNT) != SUCCESS) {
			log_fnc_err(FAILURE, "remove_user - ocs_unlock(USR_ACCNT) failed\n");
		}

	return response;
}

/******************************************************************************
*   Function Name: 	verify_username_permission
*   Purpose: 		returns the user primary group for permissions
*   In parameters: 	username, name of user to verify
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int verify_username_permission(const char *username, int *group_id) {

	int response;

	if (!username) {
		log_fnc_err(FAILURE, "%s: user name cannot be null\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t length = sizeof(buffer);

	if ((response = getpwnam_r(username, &pw, buffer, length, &result)) == SUCCESS) {
		if (result != NULL) {

			/* root is ocs admin by default */
			/* most uid will be admin */
			if (pw.pw_uid == 0) {
				*group_id = OCS_ADMIN_ID;
				return response;
			}

			int idx = 0;
			for (; idx < MAX_GROUP_SUPPORT; idx++) {
				if (pw.pw_gid == ocs_group_ids[idx]) {
					*group_id = pw.pw_gid;
					return response;
				}
			}

			log_fnc_err(FAILURE, "%s: user: %s not ocs group member\n",
				app_specific_error(UNSUPPORTED), username);
			response = FAILURE;

		}
		else {
			log_fnc_err(FAILURE, "%s: ocs_verify_permission getpwnam_r(%s) returned null\n",
				app_specific_error(NULL_OBJECT), username);
			response = NULL_OBJECT;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: ocs_verify_permission getpwnam_r(%s) returned: %d\n",
			app_specific_error(FUNCTION_ERR), username, response);
		return response;
	}

	return response;

}

/******************************************************************************
*   Function Name: 	verify_caller_permission
*   Purpose: 		returns the calling process primary group for permissions
*   In parameters: 	username, name of user to verify
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int verify_caller_permission(int *group_id) {

	int response;

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t length = sizeof(buffer);

	uid_t user_id;
	user_id = getuid();

	if ((response = getpwuid_r(user_id, &pw, buffer, length, &result)) == SUCCESS) {
		if (result != NULL) {

			/* check admin by default */
			if (pw.pw_uid == 0) {
				*group_id = OCS_ADMIN_ID;
				return response;
			}

			int idx = 0;
			for (; idx < MAX_GROUP_SUPPORT; idx++) {
				if (pw.pw_gid == ocs_group_ids[idx]) {
					*group_id = pw.pw_gid;
					return response;
				}
			}

			log_fnc_err(FAILURE, "%s: user id: %d not ocs group member\n",
				app_specific_error(UNSUPPORTED), user_id);
			response = FAILURE;

		}
		else {
			log_fnc_err(FAILURE, "%s: ocs_verify_permission getpwuid_r(%d) returned null\n",
				app_specific_error(NULL_OBJECT), user_id);
			response = NULL_OBJECT;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: ocs_verify_permission getpwuid_r(%d) returned: %d\n",
			app_specific_error(FUNCTION_ERR), user_id, response);
		return response;
	}

	return response;

}

/******************************************************************************
*   Function Name: 	verify_authentication
*   Purpose: 		authenticates user login
*   In parameters: 	username and password to verify
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int verify_authentication(const char *username, const char *password) {
	char buffer[256];
	struct spwd spw;
	struct spwd *result;

	/* salt size and termination */
	char salt[SALT_SIZE + 1];
	char *saltprt;
	saltprt = salt;

	getspnam_r(username, &spw, buffer, sizeof(buffer), &result);

	if (!result) {
		log_fnc_err(FAILURE, "%s: unable to locate user pwd\n", app_specific_error(NULL_OBJECT));
		return NULL_OBJECT;
	}

	int salt_length = 0;
	salt_length = salt_size(result->sp_pwdp);

	if (salt_length < 0 || salt_length > SALT_SIZE) {
		salt_length = SALT_SIZE;
	}

	/* just get the salt from pw string */
	strncpy(saltprt, result->sp_pwdp, salt_length);
	salt[salt_length] = '\0';

	struct crypt_data data;
	data.initialized = 0;

	if (strcmp(crypt_r(password, saltprt, &data), result->sp_pwdp) == SUCCESS) {
		return SUCCESS;
	}

	return FAILURE;
}

/******************************************************************************
*   Function 		Name: shadow_append
*   Purpose: 		appends an entry to the shodow file.
*   In parameters: 	populated spwd structure
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
static int shadow_append(struct spwd *sp) {

	int response = 0;
	FILE *fhandle;

	if (!sp) {
		log_fnc_err(FAILURE, "%s: password encryption failed\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	fhandle = fopen(SHADOW_FILE, "a+");

	if (!fhandle) {
		log_fnc_err(FAILURE, "%s: unable to open shadow\n", app_specific_error(FILE_IO_ERROR));
		return FILE_IO_ERROR;
	}

	if ((response = putspent(sp, fhandle)) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: failed to add user pw to shadow: %d\n", app_specific_error(FILE_IO_ERROR), response);
	}

	fflush(fhandle);

	fclose(fhandle);

	return response;
}

/******************************************************************************
*   Function Name:	delete_entry
*   Purpose: 		Removes an entry from a file, /etc/passwd, /etc/shadow,
*					etc/group
*   In parameters: 	filename, name of the target file.
*				   	username, user name of line to remove/locate.
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes: i don't know of another way to do this,
*					delete a line, read it into a buffer, remove the line
*					and write back.
*******************************************************************************/
static int delete_entry(char *filename, const char *username) {

	int response = 1;
	long length = 0;
	int recovery_req = 0;
	int file = -1;

	char *buffer = NULL;
	FILE *handle = NULL;

	handle = fopen(filename, "r");
	if (!handle) {
		log_fnc_err(FAILURE, "%s: file open error: %s\n", app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
		goto end_clean;
	}

	if (fseek(handle, 0L, SEEK_END) == SUCCESS) {
		if ((length = ftell(handle)) == -1) {
			log_fnc_err(FAILURE, "%s: unable to determine size of file: %s\n",
				app_specific_error(FILE_IO_ERROR), filename);
			response = FAILURE;
			goto end_clean;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: unable to seek on file: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FAILURE;
		goto end_clean;
	}

	if (length > 0 && length < MAX_FILE_BUFFER)
		buffer = (char *)malloc((length + 1) * sizeof(char));

	if (!buffer) {
		log_fnc_err(FAILURE, "%s: unable to allocate buffer for file: %s length: %ld\n",
			app_specific_error(INVALID_OPERATION), filename, length);
		response = INVALID_OPERATION;
		goto end_clean;
	}

	if (fseek(handle, 0L, SEEK_SET) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: io error seeking file: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
		goto end_clean;
	}
	
	fread(buffer, length, sizeof(char), handle);
	if (ferror(handle) != 0) {
		log_fnc_err(FAILURE, "%s: io error reading file: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
		goto end_clean;
	}

	fclose(handle);
	handle = NULL;

	// append : to name name
	char srchname[USERNAME_MAX_LEN + 2];
	snprintf(srchname, USERNAME_MAX_LEN, "\n%s:", username);

	char *skip_start;
	char *skip_end;
	int start_idx, end_idx;

	if (strncmp(buffer, &srchname[1], strlen(srchname) - 1) == SUCCESS)
		skip_start = strstr(buffer, &srchname[1]);
	else
		skip_start = strstr(buffer, srchname);


	if (!skip_start) {
		log_fnc_err(FAILURE, "%s: unable to find name entry: %s\n",
			app_specific_error(FILE_IO_ERROR), username);
		response = INVALID_OPERATION;
		goto end_clean;
	}

	skip_start++;
	skip_end = strchr(skip_start, '\n');

	if (!skip_end) {
		log_fnc_err(FAILURE, "%s: unable to find name termination: %s\n",
			app_specific_error(INVALID_OPERATION), username);
		response = INVALID_OPERATION;
		goto end_clean;
	}

	/* pointer subtraction to get index */
	start_idx = (skip_start - buffer);
	end_idx = (skip_end - buffer) + 1;

	response = FAILURE;

	/* create backup file */
	if ((response = file_io_op(AUTH_BACKUP, filename, length, buffer)) == SUCCESS) {

		file = open(filename, O_WRONLY | O_CREAT | O_TRUNC);

		if (file < SUCCESS) {
			log_fnc_err(FAILURE, "%s: io error opening file: %s\n",
				app_specific_error(FILE_IO_ERROR), filename);
			response = FILE_IO_ERROR;
			recovery_req = 1;
			goto end_clean;
		}

		if (lseek(file, 0L, SEEK_SET) == -1) {
			log_fnc_err(FAILURE, "%s: unable to seek to filename of file: %s\n",
				app_specific_error(FILE_IO_ERROR), filename);
			response = FILE_IO_ERROR;
			goto end_clean;
		}

		if (write(file, buffer, start_idx) != start_idx) {
			log_fnc_err(FAILURE, "%s: unable to write length to file: %s\n",
				app_specific_error(FILE_IO_ERROR), filename);
			response = FILE_IO_ERROR;
			recovery_req = 1;
			goto end_clean;
		}

		if (write(file, &buffer[end_idx], (length - end_idx)) != (length - end_idx)) {
			log_fnc_err(FAILURE, "%s: unable to write length to file: %s\n",
				app_specific_error(FILE_IO_ERROR), filename);
			response = FILE_IO_ERROR;
			recovery_req = 1;
			goto end_clean;
		}

		/* flag clean exit */
		response = close(file);
		file = -1;
	}
	else {
		log_fnc_err(FAILURE, "%s: unable to cteate backup to file: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
	}

end_clean:
	if (buffer)
		free(buffer);

	if (handle)
		fclose(handle);

	if (file > 0) {
		close(file);
	}

	if (recovery_req == 1) {
		file_restore(filename);
	}

	return response;
}

/******************************************************************************
*   Function Name: 	generate_salt
*   Purpose: 		creates the salt for password encryption.
*   In parameters: 	salt, input array which is modified by the void
*   Out parameters: salt, modified contents of input array
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
static void generate_salt(char *salt) {

	char state_buffer[RANDOM_BUFF];
	struct random_data data;
	memset(&data, 0, sizeof(struct random_data));

	int seed = (int)(getpid() + clock());

	initstate_r(seed, state_buffer, RANDOM_BUFF, &data);

	strcpy(salt, "$6$"); /* SHA-512 */
	int result;

	while (1) {
		random_r(&data, &result);
		strcat(salt, l64a(result));

		if (strlen(salt) >= SALT_SIZE) {
			salt[SALT_SIZE] = '\0';
			break;
		}
	}
}

/******************************************************************************
*   Function Name: 	file_io_op
*   Purpose: 		performs file backup and restore operation.
*   In parameters: 	action, backup or restore original
*   				filename, original file name
*   				length, length of input buffer
*   				buffer, file contents.
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int file_io_op(const auth_file_op action, const char *filename, long length, char *buffer) {
	struct stat sb;
	int response = SUCCESS;
	mode_t perms;
	int handle = -1;
	char *target;

	if (stat(filename, &sb) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: unable to gather file stat: %s\n",
			app_specific_error(INVALID_OPERATION), filename);
		response = INVALID_OPERATION;
		goto end_fnc;
	}

	perms = sb.st_mode;

	if (strcmp(filename, SHADOW_FILE) == SUCCESS) {
		if (action == AUTH_BACKUP)
			target = SHADOW_BAK;
		else
			target = SHADOW_FILE;
	}
	else if (strcmp(filename, USER_FILE) == SUCCESS) {
		if (action == AUTH_BACKUP)
			target = USER_BAK;
		else
			target = USER_FILE;
	}
	else {
		log_fnc_err(FAILURE, "%s: io error opening file: %s\n",
			app_specific_error(FILE_IO_ERROR), USER_BAK);
		response = FILE_IO_ERROR;
		goto end_fnc;
	}

	if (target != NULL) {
		handle = open(target, O_WRONLY | O_CREAT | O_TRUNC, perms);

		if (handle < SUCCESS) {
			log_fnc_err(FAILURE, "%s: io error opening file: %s\n",
				app_specific_error(FILE_IO_ERROR), target);
			response = FILE_IO_ERROR;
			goto end_fnc;
		}

		if (lseek(handle, 0L, SEEK_SET) == -1) {
			log_fnc_err(FAILURE, "%s: unable to seek to beginning of file: %s\n",
				app_specific_error(FILE_IO_ERROR), target);
			response = FILE_IO_ERROR;
			goto end_fnc;
		}

		if (write(handle, buffer, length) != length) {
			log_fnc_err(FAILURE, "%s: unable to write length to file: %s\n",
				app_specific_error(FILE_IO_ERROR), target);
			response = FILE_IO_ERROR;
			goto end_fnc;
		}

	}

end_fnc:
	if (handle >= SUCCESS) {
		close(handle);
	}

	return response;
}

/******************************************************************************
*   Function Name: 	file_remove
*   Purpose: 		removes back-up of original file. does not remove original.
*   In parameters: 	filename, original file name (not backup)
*   Return value:  	FAILURE code if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int file_remove(char *filename) {
	int response;
	char *target;
	int err_no = 0;

	if (strcmp(filename, SHADOW_FILE) == SUCCESS) {
		target = SHADOW_BAK;
	}
	else if (strcmp(filename, USER_FILE) == SUCCESS) {
		target = USER_BAK;
	}
	else {
		target = filename;
	}

	if (target != NULL) {
		/* check exists */
		response = file_exists(target, &err_no);
		if (response == SUCCESS) {
			if ((response = remove(target)) != SUCCESS) {
				log_fnc_err(FAILURE, "%s: could not remove file: %s\n",
					strerror(errno), target);
				response = FILE_IO_ERROR;
			}
		}
		else {
			/* file does not exist */
			if (err_no == ENOENT)
				response = SUCCESS;
			/* exists but access denied */
			else if (err_no == EACCES) {
				log_fnc_err(FAILURE, "%s: access denied when removing file: %s\n",
					app_specific_error(INVALID_OPERATION), target);
				response = INVALID_OPERATION;
			}
			else {
				log_fnc_err(FAILURE, "%s: access(%s) to file failed\n",
					app_specific_error(INVALID_OPERATION), target);
				response = INVALID_OPERATION;
			}
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: filename cannot be null\n",
			app_specific_error(INVALID_PARAM));
		response = INVALID_PARAM;
	}

	return response;
}

/******************************************************************************
*   Function Name: 	file_restore
*   Purpose: 		performs file restore using file_io_op
*   In parameters: 	filename, original file name
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int file_restore(char *filename) {
	int response = SUCCESS;
	long length = 0;
	char *buffer = NULL;
	FILE *handle = NULL;
	char *source;

	if (strcmp(filename, SHADOW_FILE) == SUCCESS) {
		source = SHADOW_BAK;
	}
	else if (strcmp(filename, USER_FILE) == SUCCESS) {
		source = USER_BAK;
	}
	else {
		log_fnc_err(FAILURE, "%s: io error opening file: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
		goto end_clean;
	}


	handle = fopen(source, "r");
	if (!handle) {
		log_fnc_err(FAILURE, "%s: file open error: %s\n", app_specific_error(FILE_IO_ERROR), source);
		response = FILE_IO_ERROR;
		goto end_clean;
	}

	if (fseek(handle, 0L, SEEK_END) == SUCCESS) {
		if ((length = ftell(handle)) == -1) {
			log_fnc_err(FAILURE, "%s: unable to determine size of file: %s\n",
				app_specific_error(FILE_IO_ERROR), source);
			response = -1;
			goto end_clean;
		}
	}

	if (length > 0 && length < MAX_FILE_BUFFER)
		buffer = (char *)malloc((length + 1) * sizeof(char));

	if (!buffer) {
		log_fnc_err(FAILURE, "%s: unable to allocate buffer for file: %s\n",
			app_specific_error(INVALID_OPERATION), source);
		response = INVALID_OPERATION;
		goto end_clean;
	}

	if (fseek(handle, 0L, SEEK_SET) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: io error seeking file: %s\n",
			app_specific_error(FILE_IO_ERROR), source);
		response = FILE_IO_ERROR;
		goto end_clean;
	}

	fread(buffer, length, sizeof(char), handle);
	if (ferror(handle) != 0) {
		log_fnc_err(FAILURE, "%s: io error reading file: %s\n",
			app_specific_error(FILE_IO_ERROR), source);
		response = FILE_IO_ERROR;
		goto end_clean;
	}

	fclose(handle);
	handle = NULL;

	if (file_io_op(AUTH_RESTORE, filename, length, buffer) != SUCCESS) {
		log_fnc_err(FAILURE, "%s: file restore failed: %s\n",
			app_specific_error(FILE_IO_ERROR), filename);
		response = FILE_IO_ERROR;
		goto end_clean;
	}
	else {
		response = file_remove(filename);
	}

end_clean:
	if (buffer)
		free(buffer);

	if (handle)
		fclose(handle);

	return response;
}

/******************************************************************************
*   Function Name: 	file_exists
*   Purpose: 		checks if a file exists
*   In parameters: 	filename; name of file to check
*   out paraeters:	error_code: errno on failure.
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int file_exists(const char *filename, int *error_code) {
	int response = access(filename, F_OK);
	*error_code = 0;

	if (response != SUCCESS) {
		*error_code = errno;
		/* file does not exist */
		if (errno == ENOENT)
			response = SUCCESS;
		/* exists but access denied */
		else if (errno == EACCES) {
			log_fnc_err(FAILURE, "%s: access denied when removing file: %s\n",
				app_specific_error(INVALID_OPERATION), filename);
			response = INVALID_OPERATION;
		}
		else {
			log_fnc_err(FAILURE, "%s: access(%s) to file failed\n",
				app_specific_error(INVALID_OPERATION), filename);
			response = INVALID_OPERATION;
		}
	}
	else {
		return SUCCESS;
	}

	return response;
}

/******************************************************************************
*   Function Name: 	roll_back_recovery
*   Purpose: 		performs file restore of passwd and shadow file. function
*   				only called by EOWNERDEAD on mutex.  if process dies during
*   				manipulation (write back) of passwd or shadow file, corruption
*   				can occur.
*   In parameters: 	none
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes: should not be called outside of mutex holder.  designed for
*   				mutex EOWNERDEAD
*******************************************************************************/
int roll_back_recovery(void) {
	int response = SUCCESS;
	int error_code = 0;

	if (file_exists(SHADOW_BAK, &error_code) == SUCCESS)
		response = file_restore(SHADOW_FILE);

	if (response == SUCCESS) {
		if (file_exists(USER_BAK, &error_code) == SUCCESS)
			response = file_restore(USER_FILE);
	}

	return response;
}

/******************************************************************************
*   Function Name: 	initialize
*   Purpose: 		called by constructor to set the EOWNERDEAD recovery function
*   In parameters: 	none
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes: 
*******************************************************************************/
void initialize(void) {
	config_mutex_rec(USR_ACCNT, roll_back_recovery);
}

/******************************************************************************
*   Function Name: 	get_user_group_id
*   Purpose: 		returns primary group Id associated with user name
*   In parameters: 	username, char array of username.
* 	Out parematers:	group_id, primary group Id for user name.
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_user_group_id(const char *username, int *group_id) {
	int response;

	if (username == NULL) {
		log_fnc_err(FAILURE, "%s: username name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t length = sizeof(buffer);

	if ((response = getpwnam_r(username, &pw, buffer, length, &result)) == SUCCESS) {
		if (result != NULL) {
			*group_id = pw.pw_gid;
			return response;
		}
		else {
			return NULL_OBJECT;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: getpwnam_r error: %s %d\n", app_specific_error(FUNCTION_ERR), username, response);
		return FUNCTION_ERR;
	}

	return FAILURE;
}

/******************************************************************************
*   Function Name: 	get_user_group_name
*   Purpose: 		returns primary group name associated with user name
*   In parameters: 	username, char array of username.
* 	Out parematers:	groupname, primary group name for user name.
*   Return value:  	FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int get_user_group_name(const char *username, int length, char *groupname) {
	int response;

	if (username == NULL) {
		log_fnc_err(FAILURE, "%s: username name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	if (groupname == NULL) {
		log_fnc_err(FAILURE, "%s: group name parameter\n", app_specific_error(INVALID_PARAM));
		return INVALID_PARAM;
	}

	if (length > MAX_GROUP_LENGTH)
		length = MAX_GROUP_LENGTH;

	struct passwd pw;
	struct passwd *result;

	char buffer[256];
	size_t buf_len = sizeof(buffer);

	if ((response = getpwnam_r(username, &pw, buffer, buf_len, &result)) == SUCCESS) {
		if (result != NULL) {
			/* lookup the group name from the header file */
			int idx = 0;
			for (; idx < MAX_GROUP_SUPPORT; idx++) {
				if (pw.pw_gid == ocs_group_ids[idx]){
					strncpy(groupname, group_names[idx],length);
					return SUCCESS;
				}
			}

			return UNKNOWN_ERROR;
		}
		else {
			return NULL_OBJECT;
		}
	}
	else {
		log_fnc_err(FAILURE, "%s: getpwnam_r error: %s %d\n", app_specific_error(FUNCTION_ERR), username, response);
		return FUNCTION_ERR;
	}

	return FAILURE;
}



