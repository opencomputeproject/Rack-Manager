// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef OCSPERSIST_H_
#define OCSPERSIST_H_

/* NOTE: Key and Value should not contain space */

#define PERSIST_KEY_SIZE 64
#define PERSIST_VALUE_SIZE 64

/*
* Get persist Value from provided Key
* Param1: Input Key 
* Param2: Return Value
*/
extern int get_persist(char*, char*);

/*
* Set persist key/Value 
* Param1: Input Key 
* Param2: Input Value
*/
extern int set_persist(char*, char*);

#endif // OCSPERSIST_H_