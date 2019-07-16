// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsgpio-common.h>
#include <led-ops.h>


/******************************************************************************
*   Function Name: led_get_brightness
*   Purpose: Reads brightness of an LED 
*   In parameters: LED name, checkpath - presenece check of the path
*   Return value: An int value >= 0 read from LED. FAILED if something failed.
*   Comments/Notes:
*******************************************************************************/
int led_get_brightness(char* led_name, bool_t checkpath)
{
    char path[BUFFER_BRIGHTNESS_MAX];
    int fd;
    char value_str[3];
    int retval = SUCCESS;
    errno = 0;  

    snprintf(path, BUFFER_BRIGHTNESS_MAX, SYSPATH_LED_BRIGHTNESS, led_name);
    fd = open(path, O_RDONLY | O_SYNC);

    if (fd == FAILED) 
    {
        if (checkpath == FALSE)
        {
            LOG_ERR(errno, "Failed to open for LED %s brightness read\n", led_name);
        }
        return(FAILED);
    }
 
    if (checkpath == FALSE)
    {
        if ( read(fd, value_str, 3) == FAILED) 
        {
            LOG_ERR(errno, "Failed to read brightness for LED %s\n", led_name);
            close(fd);          
            return(FAILED);
        }
        retval = (value_str[0] == '0')?LED_OFF:LED_ON;
    }
    
    close(fd);
 
    return(retval);
}

/******************************************************************************
*   Function Name: led_set_brightness
*   Purpose: Write brightness to LED
*   In parameters: LED name and value to write
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/ 
int led_set_brightness(char* led_name, unsigned int value)
{
    static const char s_values_str[] = "01";
 
    char path[BUFFER_BRIGHTNESS_MAX];
    int fd;
    errno = 0;  

    snprintf(path, BUFFER_BRIGHTNESS_MAX, SYSPATH_LED_BRIGHTNESS, led_name);
    fd = open(path, O_WRONLY | O_SYNC);

    if (fd == FAILED) 
    {
        LOG_ERR(errno, "Failed to open for LED %s brightness write\n", led_name);
        return(FAILED);
    }
 
    if (1 != write(fd, &s_values_str[(value == TRUE)?1:0], 1)) 
    {
        LOG_ERR(errno, "Failed to write brightness for LED %s\n", led_name);     
        close(fd);      
        return(FAILED);
    }
 
    close(fd);
    return(SUCCESS);
}

/******************************************************************************
*   Function Name: led_get_max_brightness
*   Purpose: Reads max brightness of an LED
*   In parameters: LED name, checkpath - presenece check of the path
*   Return value: An int value >= 0. FAILED if something failed.
*   Comments/Notes:
*******************************************************************************/
int led_get_max_brightness(char* led_name, bool_t checkpath)
{
	char path[BUFFER_BRIGHTNESS_MAX];
	int fd;
	char value_str[3];
	int retval = SUCCESS;
	errno = 0;

	snprintf(path, BUFFER_BRIGHTNESS_MAX, SYSPATH_LED_BRIGHTNESS, led_name);
	fd = open(path, O_RDONLY | O_SYNC);

	if (fd == FAILED)
	{
		if (checkpath == FALSE)
		{
			LOG_ERR(errno, "Failed to open for LED %s brightness read\n", led_name);
		}
		return(FAILED);
	}

	if (checkpath == FALSE)
	{
		if (read(fd, value_str, 3) == FAILED)
		{
			LOG_ERR(errno, "Failed to read brightness for LED %s\n", led_name);
			close(fd);
			return(FAILED);
		}
		retval = (value_str[0] == '0') ? LED_OFF : LED_ON;
	}

	close(fd);

	return(retval);
}

/******************************************************************************
*   Function Name: led_set_max_brightness
*   Purpose: Write max brightness to LED config
*   In parameters: LED name and value to write
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int led_set_max_brightness(char* led_name, unsigned int value)
{
	static const char s_values_str[] = "01";

	char path[BUFFER_BRIGHTNESS_MAX];
	int fd;
	errno = 0;

	snprintf(path, BUFFER_BRIGHTNESS_MAX, SYSPATH_LED_BRIGHTNESS, led_name);
	fd = open(path, O_WRONLY | O_SYNC);

	if (fd == FAILED)
	{
		LOG_ERR(errno, "Failed to open for LED %s brightness write\n", led_name);
		return(FAILED);
	}

	if (1 != write(fd, &s_values_str[(value == TRUE) ? 1 : 0], 1))
	{
		LOG_ERR(errno, "Failed to write brightness for LED %s\n", led_name);
		close(fd);
		return(FAILED);
	}

	close(fd);
	return(SUCCESS);
}
