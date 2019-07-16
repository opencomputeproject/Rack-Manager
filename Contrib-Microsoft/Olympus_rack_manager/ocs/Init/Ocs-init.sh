#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

### BEGIN INIT INFO
# Provides:			Ocs-init.sh
# Required-Start:	syslog
# Required-Stop:
# Default-Start:	1 2 3 4 5
# Default-Stop:		0 6
# Description:		OCS core system initialization.
### END INIT INFO

get_pid() {
	pid=`ps | grep /usr/bin/$1 | grep -v grep | awk '{print $1}'`
}

stop_process() {
	get_pid $1
	if [ -n "$pid" ]; then
		echo -n "Stopping $1..."
		kill $pid
		for i in {1..10}; do
			get_pid $1
			if [ -z "$pid" ]; then
				break
			fi
				
			echo -n "."
			sleep 1
		done
			
		get_pid $1
		if [ -z "$pid" ]; then
			echo "Done"
		else
			echo "Failed"
			echo -n "Killing $1..."
			kill -9 $pid
			echo "Done"
		fi
	fi
}

do_start() {
	get_pid ocs-init
	if [ -n "$pid" ]; then
		echo "Already started"
	else
		echo -n "Creating eMMC directories..."
		mkdir -p -m 0777 /usr/srvroot/shared
		echo "Done."
		
		echo -n "Initializing shared resources..."
		mkdir -p -m 0777 /var/local/ocs_tmp
		/usr/bin/ocs-init
		if [ $? -eq 0 ]; then
			echo "Done."
		else
			echo "Failed."
		fi
		
		echo -n "Starting Logging Daemon... "
		/usr/bin/ocslog-daemon >/dev/null </dev/null 2>&1 &
		echo "Done."
	fi
}

do_stop() {
	stop_process ocs-init
	stop_process ocslog-daemon
}

do_status() {
	get_pid ocs-init
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