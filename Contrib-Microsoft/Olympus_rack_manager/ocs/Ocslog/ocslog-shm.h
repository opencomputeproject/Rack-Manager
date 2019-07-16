// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef __ocsshmlog_h
#define __ocsshmlog_h

#define UNKNOWN_ERROR	-1
#define FAILURE			-2
#define SUCCESS			0

int shm_init();
int shm_enqueue(const char*);
int shm_dequeue(char**);

/* Called only by the log daemon */
int shm_create();
void shm_close();

#endif
