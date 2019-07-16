// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#define GPIO_DIR_OUT                    0
#define GPIO_DIR_IN                     1

#define GPIO_LOW                        0
#define GPIO_HIGH                       1

/* /sys/class paths for GPIO operation */
#define SYSPATH_EXPORT                  "/sys/class/gpio/export"
#define SYSPATH_UNEXPORT                "/sys/class/gpio/unexport"
#define SYSPATH_GPIOVALUE               "/sys/class/gpio/gpio%d/value"
#define SYSPATH_DIRECTION               "/sys/class/gpio/gpio%d/direction"
#define SYSPATH_ACTIVELOW               "/sys/class/gpio/gpio%d/active_low"

/* Limits for char array sizes */
#define BUFFER_MAX                      4
#define BUFFER_VALUE_MAX                30
#define BUFFER_DIRECTION_MAX            35
#define BUFFER_ACTIVELOW_MAX            36

/* Public functions defined in gpio-ops.c */
int gpio_setup(int pin, int dir, int is_al);
int gpio_write(int pin, unsigned int value);
int gpio_read(int pin, bool_t checkpath);
int gpio_direction(int pin, int dir);
int gpio_activelow(int pin, int is_al);
int gpio_unexport(int pin);
int gpio_export(int pin);

