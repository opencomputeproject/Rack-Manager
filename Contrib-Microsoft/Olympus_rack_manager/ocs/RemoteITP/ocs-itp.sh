#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

### BEGIN INIT INFO
# Provides:			ocs-itp.sh
# Required-Start:	networking rminit.sh
# Required-Stop:	networking
# Default-Start:	3 4 5
# Default-Stop:		0 1 2 6
# Description:		OCS remote ITP debugging service.
### END INIT INFO

get_pid() {
	pid=`ps | grep /usr/bin/ocs-itp | grep -v grep | awk '{print $1}'`
}

do_start() {
	get_pid
	if [ -n "$pid" ]; then
		echo "Already started"
	else
		echo -n "Starting ocs-itp..."
		/usr/bin/ocs-itp > /dev/null 2>&1 &
		echo "Done"
	fi
}

do_stop() {
	get_pid
	if [ -n "$pid" ]; then
		echo -n "Stopping ocs-itp..."
		kill $pid
		for i in {1..10}; do
			get_pid
			if [ -z "$pid" ]; then
				break
			fi
				
			echo -n "."
			sleep 1
		done
			
		get_pid
		if [ -z "$pid" ]; then
			echo "Done"
		else
			echo "Failed"
			echo -n "Killing ocs-itp..."
			kill -9 $pid
			echo "Done"
		fi
	fi
}

do_status() {
	get_pid
	if [ -n "$pid" ]; then
		echo "Running"
	else
		echo "Stopped"
	fi
}

case $1 in
	start)
		do_start
	;;
	
	stop)
		do_stop
	;;
	
	restart)
		do_stop
		do_start
	;;
	
	status)
		do_status
	;;
	
	*)
		echo "Usage: $0 {start|stop|restart|status}"
		exit 2
	;;
esac