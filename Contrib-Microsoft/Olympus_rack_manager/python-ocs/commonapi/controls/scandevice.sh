#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

start_cmd () {
	output=$($1 2>/tmp/error)

	if [ "$?" = "0" ]; then
		echo "$output"
		echo ""
	else
		errorstr=$(cat /tmp/error)
		printf "\tError Code: $?, Error: ${errorstr##*:}\n"
	fi
}

# Return version information
printf "\n\nRack Manager Version Information:\n"
start_cmd "/etc/rmversions.sh"

# Network interfaces information
printf "\nRack Manager Network Interfaces:\n"
start_cmd "cat /etc/network/interfaces"

# Network Interfaces Configuration
printf "\nRack Manager Network Interfaces Configuration:\n"
start_cmd "ifconfig"

# Kernel Debug Messages
printf "\nRack Manager Kernel Debug Messages:\n"
start_cmd "dmesg"

# Memory Usage
printf "\nRack Manager Memory Usage:\n"
start_cmd "free -m && cat /proc/meminfo"

# CPU usage
printf "\nRack Manager CPU Usage:\n"
start_cmd "top -b -n 2 -d 2"

# QSPI usage
printf "\nRack Manager QSPI usage:\n"
start_cmd "cat /proc/mtd"

# Mounted Filesystems
printf "\nRack Manager Mounted Filesystems:\n"
start_cmd "df"

# Filesystem integrity check
printf "\nRack Manager Filesystem Integrity:\n"
start_cmd "fsck -n"

# Processes List
printf "\nRack Manager Processes List:\n"
start_cmd "ps"

# Routing Table
printf "\nRack Manager Routing Table:\n"
start_cmd "ip route"

rm /tmp/error