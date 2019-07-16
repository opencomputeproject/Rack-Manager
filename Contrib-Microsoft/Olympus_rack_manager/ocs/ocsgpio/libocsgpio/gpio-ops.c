// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsgpio-common.h>
#include <gpio-ops.h>

/******************************************************************************
*   Function Name: gpio_export
*   Purpose: Open the gpio syspath and export a specific gpio
*   In parameters: pin number
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int gpio_export(int pin)
{
    char buffer[BUFFER_MAX];
    ssize_t bytes_written;
    int fd = 0;
    errno = 0;
 
    fd = open(SYSPATH_EXPORT, O_WRONLY | O_SYNC);
    
    if (fd == FAILED) {
        LOG_ERR(errno, "Failed to export GPIO number %d\n", pin);
        return(FAILED);
    }
    
    bytes_written = snprintf(buffer, BUFFER_MAX, "%d", pin);
    write(fd, buffer, bytes_written);
    close(fd);
    return(SUCCESS);
}

/******************************************************************************
*   Function Name: gpio_unexport
*   Purpose: Open the gpio syspath and unexport a specific gpio
*   In parameters: pin number
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int gpio_unexport(int pin)
{
    char buffer[BUFFER_MAX];
    ssize_t bytes_written;
    int fd;
    errno = 0;  
 
    fd = open(SYSPATH_UNEXPORT, O_WRONLY | O_SYNC);
    if (fd == FAILED) {
        LOG_ERR(errno, "Failed to unexport GPIO number %d\n", pin);
        return(FAILED);
    }
 
    bytes_written = snprintf(buffer, BUFFER_MAX, "%d", pin);
    write(fd, buffer, bytes_written);
    close(fd);
    return(SUCCESS);
}

/******************************************************************************
*   Function Name: gpio_direction
*   Purpose: Set gpio direction 
*   In parameters: pin number and direction to set. 
*   Return value: Int type. 0 is nothing failed.
*   Comments/Notes:
*******************************************************************************/
int gpio_direction(int pin, int dir)
{
    static const char s_directions_str[]  = "in\0out";
 
    char path[BUFFER_DIRECTION_MAX];
    int fd;
    errno = 0;  
 
    snprintf(path, BUFFER_DIRECTION_MAX, SYSPATH_DIRECTION, pin);
    fd = open(path, O_WRONLY | O_SYNC);
    if (fd == FAILED) {
        LOG_ERR(errno, "Failed to open for GPIO %d direction\n", pin);
        return(FAILED);
    }
 
    if (FAILED == write(fd, &s_directions_str[GPIO_DIR_IN == dir ? 0 : 3], 
                                          GPIO_DIR_IN == dir ? 2 : 3))
    {
        LOG_ERR(errno, "Failed to set direction for GPIO %d\n", pin);
        close(fd);      
        return(FAILED);
    }
 
    close(fd);
    return(SUCCESS);
}

/******************************************************************************
*   Function Name: gpio_activelow
*   Purpose: Set gpio activelow 
*   In parameters: pin number and activelow to set. 
*   Return value: Int type. 0 is nothing failed.
*   Comments/Notes:
*******************************************************************************/
int gpio_activelow(int pin, int is_al)
{
    char path[BUFFER_ACTIVELOW_MAX];
	static const char s_values_str[] = "01";
    int fd;
    errno = 0;  
 
    snprintf(path, BUFFER_ACTIVELOW_MAX, SYSPATH_ACTIVELOW, pin);
    fd = open(path, O_WRONLY | O_SYNC);
    if (fd == FAILED) {
        LOG_ERR(errno, "Failed to open for GPIO %d activelow\n", pin);
        return(FAILED);
    }
 
    if (FAILED == write(fd, &s_values_str[(is_al != 0)?1:0], 1))
    {
        LOG_ERR(errno, "Failed to set activelow for GPIO %d\n", pin);
        close(fd);      
        return(FAILED);
    }
 
    close(fd);
    return(SUCCESS);
}

/******************************************************************************
*   Function Name: gpio_setup
*   Purpose: Export and set a gpio direction 
*   In parameters: pin number, direction, active_low to set. 
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/
int gpio_setup(int pin, int dir, int is_al)
{
    int retval = SUCCESS;

    if ( gpio_read(pin, TRUE) == FAILED )
    {
        retval = gpio_export( pin );
        if ( retval != 0 )
            return retval;
            
        retval = gpio_direction( pin, dir);
        if ( retval != 0 )
            return retval;
        
		retval = gpio_activelow( pin, is_al);
        if ( retval != 0 )
            return retval;		
    }
    
    return retval;
}

/******************************************************************************
*   Function Name: gpio_read
*   Purpose: Read a value from a gpio pin
*   In parameters: pin number, checkpath - presenece check of the path
*   Return value: An int value >= 0 read from GPIO. FAILED if something failed.
*   Comments/Notes:
*******************************************************************************/
int gpio_read(int pin, bool_t checkpath)
{
    char path[BUFFER_VALUE_MAX];
    int fd;
    char value_str[3];
    int retval = SUCCESS;
    errno = 0;  

    snprintf(path, BUFFER_VALUE_MAX, SYSPATH_GPIOVALUE, pin);
    fd = open(path, O_RDONLY | O_SYNC);
    if (fd == FAILED) 
    {
        if (checkpath == FALSE)
        {
            LOG_ERR(errno, "Failed to open for GPIO %d value read\n", pin);
        }
        return(FAILED);
    }
 
    if (checkpath == FALSE)
    {
        if ( read(fd, value_str, 3) == FAILED) 
        {
            LOG_ERR(errno, "Failed to read value for GPIO %d\n", pin);  
            close(fd);          
            return(FAILED);
        }
        retval = (value_str[0] == '0')?GPIO_LOW:GPIO_HIGH;
    }
    
    close(fd);
 
    return(retval);
}

/******************************************************************************
*   Function Name: gpio_write
*   Purpose: Write a value to a gpio
*   In parameters: pin number and value to write
*   Return value:  FAILED if something failed, SUCCESS otherwise
*   Comments/Notes:
*******************************************************************************/ 
int gpio_write(int pin, unsigned int value)
{
    static const char s_values_str[] = "01";
 
    char path[BUFFER_VALUE_MAX];
    int fd;
    errno = 0;  

    snprintf(path, BUFFER_VALUE_MAX, SYSPATH_GPIOVALUE, pin);
    fd = open(path, O_WRONLY | O_SYNC);
    if (fd == FAILED) 
    {
        LOG_ERR(errno, "Failed to open for GPIO %d value write\n", pin);
        return(FAILED);
    }
 
    if (1 != write(fd, &s_values_str[(value == TRUE)?1:0], 1)) 
    {
        LOG_ERR(errno, "Failed to write value for GPIO %d\n", pin);     
        close(fd);      
        return(FAILED);
    }
 
    close(fd);
    return(SUCCESS);
}
