// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

/*
* auth.h
*
*  Created on: Sep 7, 2016
*      Author: root
*/

#include <sys/types.h>
#include <stdlib.h>
#include <string.h>
#include <grp.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <shadow.h>
#include <crypt.h>
#include <pwd.h>
#include <time.h>
#include <sys/time.h>

/* random integer buffer */
#define RANDOM_BUFF			64

/* 3 encryption algorithm + 16 seed */
#define SALT_SIZE			19

/* user name length */
#define USERNAME_MIN_LEN	5
#define USERNAME_MAX_LEN	20

/* maximum group members */
#define MAX_GROUP_MEMBER	10

/* ocs group array size */
#define MAX_GROUP_SUPPORT	3
#define MAX_GROUP_LENGTH	13

/* custom error array size */
#define MAX_ERROR_SUPPORT	10
#define MAX_ERROR_LENGTH	20

/* default error index */
#define DEFAULT_ERR_IDX		2

#define UINT_MAX_VALUE 0xffffffff

/* user database files */
#define SHADOW_FILE		"/etc/shadow"
#define USER_FILE		"/etc/passwd"

#define SHADOW_BAK		"/tmp/shadow"
#define USER_BAK		"/tmp/passwd"

/* default user shell */
#define USER_SHELL		"/bin/sh"

/* ocs groups ids derived from /etc/group */
#define OCS_ADMIN_ID	0   /* group-> root */
#define OCS_OPERATOR_ID	37	/* group-> operator */
#define OCS_USER_ID		100	/* group-> user */

/* maximum show or passwd file size */
#define MAX_FILE_BUFFER		6144

/* user id range */
#define MIN_ID 1000
#define MAX_ID 65000

/* custom errors */
#define INVALID_PARAM	  3
#define UNSUPPORTED		  4
#define NULL_OBJECT		  5
#define FUNCTION_ERR	  6
#define FILE_IO_ERROR	  7
#define INPUT_BUFF_SIZE	  8
#define INVALID_OPERATION 9

/* library specific error strings */
static const char app_error_str[MAX_ERROR_SUPPORT][MAX_ERROR_LENGTH] = {
	"SUCCESS",			/* 0 */
	"FAILURE",			/* 1 */
	"UNKNOWN_ERROR",	/* 2 */
	"INVALID_PARAM",	/* 3 */
	"UNSUPPORTED",		/* 4 */
	"NULL_OBJECT",		/* 5 */
	"FUNCTION_ERR",		/* 6 */
	"FILE_IO_ERROR",	/* 7 */
	"INPUT_BUFF_SIZE",	/* 8 */
	"INVALID_OPERATION" /* 9 */
};

/* ocs defined roles id */
static const int ocs_group_ids[MAX_GROUP_SUPPORT] = {
	OCS_ADMIN_ID,	/* admin */
	OCS_OPERATOR_ID,/* operator */
	OCS_USER_ID		/* user */
};

/* ocs defined roles */
static const char group_names[MAX_GROUP_SUPPORT][MAX_GROUP_LENGTH] = {
	"admin",    /* gid_t: 0 - all read, execute, user and configure */
	"operator",	/* gid_t: 27 - all read and execute  */
	"user" 		/* gid_t: 100 - all read operations  */
};

typedef enum AUTH_FILE_OP {
	AUTH_BACKUP = 0,
	AUTH_RESTORE = 1,
}auth_file_op;

/* string pointer to application specific error */
extern char * app_specific_error(int err);

/* reference to crypt library for pw encryption */
extern char *crypt(const char *key, const char *salt);

/* get ocs group id from group name */
extern int ocs_group_id(const char *groupname, int *g_id);

/* verify user is a member of the ocs group */
extern int ocs_group_member(const char *groupname, const char *username);

/* list ocs group members in comma separated string */
extern int ocs_group_members(const char *groupname, const int *length, char *members);

/* change ocs user role */
extern int ocs_change_role(const char *username, const char *groupname);

/* verfiy the current user is root */
extern int check_root();

/* get user name from uid */
extern int get_username_from_id(const uid_t user_id, const size_t length, char *username);

/* get group name from gid */
extern int get_groupname_from_id(const gid_t group_id, const size_t length, char *groupname);

/* get gid from group name */
extern int get_groupid_from_name(const char *groupname, gid_t *id);

/* get current user name from id */
extern int get_current_username(char *username, size_t length);

/* get uid from name */
extern int get_userid_from_name(const char *username, uid_t *userid);

/* add a user */
extern int add_user(const char *username, const char *groupname, const char *password);

/* remove a user */
extern int remove_user(const char *username);

/* update user password */
extern int update_password(const char *username, const char *password);

/* verify ocs user permissions by uid */
extern int verify_caller_permission(int *group_id);

/* verify ocs user permissions by name */
extern int verify_username_permission(const char *username, int *group_id);

/* verify user authentication given name and password */
extern int verify_authentication(const char *username, const char *password);

/* returns group id assocaited with the user name */
extern int get_user_group_id(const char *username, int *group_id);

/* returns group name assocaited with the user name */
extern int get_user_group_name(const char *username, int length, char *groupname);
