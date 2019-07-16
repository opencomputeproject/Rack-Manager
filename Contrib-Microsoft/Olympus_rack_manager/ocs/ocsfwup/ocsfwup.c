// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsfwup.h>

#define APP_VERSION_MAJOR    	1
#define APP_VERSION_MINOR    	2
#define APP_VERSION_REVISION 	0
#define APP_VERSION_BUILD    	0

const char CMD_HELP[]           = "-h";
const char CMD_UPGRADE[]        = "upgrade";
const char CMD_RECOVER[]        = "recover";
const char CMD_GETSTATUS[]      = "getstatus";

const char AppName[]            = APPNAME;

/******************************************************************************
*   Function Name: show_usage
*   Purpose: Print a 1 line guide
*******************************************************************************/
void show_usage(void)
{
    LOG_INFO("Run %s -h for help\n\n", AppName);
}

/******************************************************************************
*   Function Name: show_help
*   Purpose: Print detailed help on usage
*******************************************************************************/
void show_help(void)
{
    LOG_INFO("Usage: %s <absolute path to package name>\n", AppName);
}

/******************************************************************************
*   Function Name: strlwr
*   Purpose: Helper function to convert input string to lower case and 
*            store it in place
*   In arguments: *str - Input string pointer
*   Return value: Same as input string pointer
*   Comments/Notes:
*******************************************************************************/
static char *strlwr(char *str)
{
   unsigned char *p = (unsigned char *)str;
 
   while (*p) {
      *p = tolower(*p);
      p++;
   }
 
   return str;
}

/******************************************************************************
*   Function Name: main
*******************************************************************************/
int main(int argc, char *argv[])
{
    int retval = SUCCESS;       
    char *paramval;
	unsigned int ver;
	unsigned int i;
	const char *pkgnames[FWUP_PKGID_MAX] = FWUP_IMAGESTORE_PKGNAMES;	
	const char *statusnames[FWUP_STATUS_MAX] = FWUP_STATUS_NAMES;	

	ocs_fwup_libgetversion(&ver);
    LOG_INFO("\n%s v%d.%d, Lib v%d.%d. (C) 2016 Microsoft Corp\n", AppName, 
										APP_VERSION_MAJOR, APP_VERSION_MINOR,
										VERSION_GET_MAJOR(ver), VERSION_GET_MINOR(ver) );
    
    if (argc < 2) {
        LOG_INFO("[%s]:Insufficient argument count %d\n", AppName, argc-1);
        retval = FAILED;
        show_help();
        return retval;
    }
	
    paramval = argv[1];
    if (strlen(paramval) == 0) {
        LOG_INFO("[%s]:Invalid command name argument %d\n", AppName, 1);
        retval = FAILED;
        show_help();
    }
	else if (strncmp(CMD_UPGRADE, strlwr(paramval), strlen(CMD_UPGRADE)) == 0) {
		paramval = argv[2];
		if (strlen(paramval) == 0) {
			LOG_INFO("[%s]:Invalid package name argument\n", AppName);
			retval = FAILED;
			show_help();
		}
		else
			ocs_fwup_startupgrade(paramval);
    }
	else if (strncmp(CMD_RECOVER, strlwr(paramval), strlen(CMD_RECOVER)) == 0) {
		paramval = argv[2];
		if (strlen(paramval) > 0) {
			for (i=0; i<FWUP_PKGID_MAX; i++) {
				if (strncmp(pkgnames[i], paramval, strlen(pkgnames[i])) == 0)
					break;
			}
		}
		
		if ((strlen(paramval) == 0) || (i == FWUP_PKGID_MAX)) {
			LOG_INFO("[%s]:Invalid recovery type argument\n", AppName);
			retval = FAILED;
			show_help();
		}
		else
			ocs_fwup_startrecovery(i);
    }
	else if (strncmp(CMD_GETSTATUS, strlwr(paramval), strlen(CMD_GETSTATUS)) == 0) {
		retval = ocs_fwup_getstatus(&i);
		if (retval == SUCCESS)
			LOG_INFO("[%s]:FWUpgrade status: %s\n", AppName, statusnames[i]);
    }
    else if (strncmp(CMD_HELP, strlwr(paramval), strlen(CMD_HELP)) == 0) {
        show_help();
    }
    
    LOG_INFO("\n");   
    return retval;          
}                           
