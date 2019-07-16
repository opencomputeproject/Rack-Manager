// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#define LED_OFF                        0
#define LED_ON	                       1

/* /sys/class paths for LED operation */
#define SYSPATH_LED_MAX_BRIGHTNESS      "/sys/class/leds/%s/max_brightness"
#define SYSPATH_LED_BRIGHTNESS          "/sys/class/leds/%s/brightness"

/* Limits for char array sizes */
#define BUFFER_MAX                      4
#define BUFFER_BRIGHTNESS_MAX           60
#define BUFFER_MAX_BRIGHTNESS_MAX       60

/* Public functions defined in gpio-ops.c */
int led_set_brightness(char* led_name, unsigned int value);
int led_get_brightness(char* led_name, bool_t checkpath);
int led_set_max_brightness(char* led_name, unsigned int value);
int led_get_max_brightness(char* led_name, bool_t checkpath);

