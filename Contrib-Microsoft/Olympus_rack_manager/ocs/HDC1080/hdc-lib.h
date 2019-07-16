// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.



#define DEVICE_NAME	"Humidity Temperature Sensor (HDC1080)"

/* Humidity/Temperature sensor shared library methods */
int hdc_get_temperature(double*);
int hdc_get_humidity(double*);
int hdc_initialize();
