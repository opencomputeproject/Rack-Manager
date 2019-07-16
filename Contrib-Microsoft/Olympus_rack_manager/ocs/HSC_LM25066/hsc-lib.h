// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "util.h"

#define DEVICE_NAME 		"Hot Swap Controller (LM25066)"

PACK(typedef struct
{
        byte_t    noFaults :1;
        byte_t    cml_fault:1;
        byte_t    temperature_fault:1;
        byte_t    vin_uv_fault:1;
        byte_t    iout_oc_fault:1;
        byte_t    vout_ov_fault:1;
        byte_t    unit_off:1;
        byte_t    unit_busy:1;
        byte_t    unknown_fault:1;
        byte_t    other_fault:1;
        byte_t    fan_fault:1;
        byte_t    power_good:1;
        byte_t    mfr_fault:1;
        byte_t    input_fault:1;
        byte_t    iout_pout_fault:1;
        byte_t    vout_fault:1;
})hsc_status_t;

/* HSC shared library methods */
int hsc_get_power(double*);
int hsc_get_inputvoltage(double*);
int hsc_get_status(hsc_status_t*);
int hsc_clear_faults();
