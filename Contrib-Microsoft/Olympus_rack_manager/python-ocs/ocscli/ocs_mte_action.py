# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import re
import os.path
import argparse

from ocspaths import *
from ocs_mte import *

def is_integer(s):
    try:
        int(s, 0)
        return True
    except ValueError:
        pass
 
    return False

def do_ocsgpio(args):
    command = '/usr/bin/ocs-gpio'
    params = [
                [ 'cleanupgpio', 'getmode', 'getpowergood'],
                [ 'portcontrol', 'relaycontrol', 'debugled' ],
                [ 'portbuffer', 'lrselect' ],
                [ 'portpresent', 'portstate', 'rowthstatus' ],
                [ 'throttlecontrol', 'throttlebypass' ],
                [ 'attentionled' ],
                [ 'setupgpio' ]
            ]

    actions = { 'on', 'off', 'state' }

    for i, param in enumerate(params):
        if args[0] in param:
            if i == 0:
                command += ' ' + args[0]
            elif i == 1:
                if is_integer(args[1]) and args[2] in actions:
                    for arg in args[:3]:
                        command += ' ' + arg
            elif i == 2:
                if args[1] in actions:
                    command += ' ' + args[0] + ' ' + args[1]
            elif i == 3:
                if is_integer(args[1]):
                    command += ' ' + args[0] + ' ' + args[1]
            elif i == 4:
                if is_integer(args[2]) and args[1] in actions:
                    for arg in args[:3]:
                        command += ' ' + arg
            elif i == 5:
                if args[1] in actions:
                    for arg in args[:2]:
                        command += ' ' + arg
            elif i == 6:
                command += ' ' + args[0] + ' ' + '/lib/modules/$(uname -r)/extra/gpio-mon.ko'

            return command

    return 'ERROR'

def do_ocspru(args):
    command = '/usr/bin/ocs-pru'
    params = { 'getpruversion', 'clearmaxpower', 'getmaxpower', 'getthrottlestatus', 'getpower', 'getthrottlelimit', '\-v',
               'clearphasestatus', 'getphasestatus', 'getphasecurrent', 'getphasevoltage', 'getphasepower', 'setthrottleactive', 
               'setthrottleenable', 'setthrottlelimit', 'getgain', 'getoffset', 'setoffset', 'setgain', 'getadcrawdata' }

    if args[0] in params and all(is_integer(x) for x in args[1:]):
        for arg in args:
            command += ' ' + arg
        print command
        return command
    else:
        return 'ERROR'

def do_ocshsc(args):
    params = { 'getpower', 'getinputvoltage', 'getstatus', '\-v' }
    if args[0] in params:
        return '/usr/bin/ocs-hsc %s' % args[0]
    else:
        return 'ERROR'

def do_ocshdc(args):
    params = { 'gettemperature', 'gethumidity', 'initialize', '\-v' }
    if args[0] in params:
        return '/usr/bin/ocs-hdc %s' % args[0]
    else:
        return 'ERROR'

def do_ocsfru(args):

    if all(is_integer(x) for x in args[1:]):
        if args[0] == 'read':
            return '/usr/bin/ocs-fru -c %s -s %s -r' % (args[1], args[2])
        elif args[0] == 'write':
            return '/usr/bin/ocs-fru -c %s -s %s -w %s/fruupdate.txt' % (args[1], args[2], srvroot_shared_path)
        else:
            return 'ERROR'
    else:
        return 'ERROR'

def do_ocspmic(args):
    params = { 'getstatus', 'setfseal', 'initialize', '\-v' }

    if args[0] in params:
        return '/usr/bin/ocs-pmic %s' % args[0]
    else:
        return 'ERROR'

def do_ocsadccalibration(args):

    if args[0] == 'read':
        return '/usr/bin/ocs-adccalibration -r'
    elif args[0] == 'write':
        return '/usr/bin/ocs-adccalibration -w %s/adccalibration.txt' % (srvroot_shared_path)
    elif args[0] == 'calibration':
        return '/usr/bin/ocs-adccalibration -c'
    else:
        return 'ERROR'

def do_ocsmac(args):

    if args[0] == 'read':
        return '/usr/bin/ocs-mac -r'
    elif args[0] == 'write':
        return '/usr/bin/ocs-mac -w %s/macupdate.txt' %(srvroot_shared_path)
    else:
        return 'ERROR'

def do_stream():
    return '/usr/bin/stream'

def do_sysbench():
    return '/usr/bin/sysbench --test=cpu --max-time=60 --cpu-max-prime=20000 run'

def do_memtester(args):
    command = '/usr/bin/memtester'

    if all(is_integer(x) for x in args[:2]):
        for arg in args[:2]:
            command += ' ' + arg
        return command
    else:
        return 'ERROR'

def do_ttyS0():
    return '/usr/bin/ttyS0'

def do_ttyS1():
    return '/usr/bin/ttyS1'

def do_ttyS2():
    return '/usr/bin/ttyS2'

def do_fio():
    return 'fio -filename=/dev/mmcblk0 -direct=1 -iodepth 1 -thread -rw=randrw -ioengine=psync -bs=16k -size=4G -numjobs=2 -group_reporting -name=eMMC'

def do_lmbench3(args):
    if is_integer(args[0]):
        return '/usr/bin/lmbench %s' % args[0]
    else:
        return 'ERROR'

def do_iperf(args):
    IP_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    match = IP_pattern.match(args[1])

    if match:
        if args[0] == 'tcp':
            return '/usr/bin/iperf3 -f M -c %s -b 1G -t 720' % args[1]
        elif args[0] == 'udp':
            return '/usr/bin/iperf3 -f M -c %s -b 1G -t 720 -u' % args[1]
        else:
            return 'ERROR'
    else:
        return 'ERROR'

def do_minicom():
    return '/usr/bin/minicom'

def do_reboot():
    return '/sbin/reboot'

def do_date(args):
    if is_integer(args[0]):
        return '/bin/date %s' % args[0]
    else:
        return 'ERROR'

def do_hwclock():
    return '/sbin/hwclock -w'

def do_i2cdump(args):
    command = '/usr/sbin/i2cdump -f -y'

    if all(is_integer(x) for x in args[:2]):
        for arg in args[:2]:
            command += ' ' + arg
        return command
    else:
        return 'ERROR'

def do_i2cdetect(args):
    if is_integer(args[0]):
        return '/usr/sbin/i2cdetect -r -y %s' % args[0]
    else:
        return 'ERROR'

def do_i2cget(args):
    command = '/usr/sbin/i2cget -f -y'

    if all(is_integer(x) for x in args[:3]):
        for arg in args[:3]:
            command += ' ' + arg
        return command
    else:
        return 'ERROR'

def do_i2cset(args):
    command = '/usr/sbin/i2cset -f -y'

    if all(is_integer(x) for x in args[:4]):
        for arg in args[:4]:
            command += ' ' + arg
        return command
    else:
        return 'ERROR'

def do_cpuinfo():
    return '/bin/cat /proc/cpuinfo'

def do_meminfo():
    return '/bin/cat /proc/meminfo'

def do_qspiinfo():
    return '/usr/bin/hexdump /sys/class/spi_master/spi32766/spi32766.0/of_node/spi-max-frequency'

def do_mmcinfo():
    return '/bin/cat /sys/kernel/debug/mmc0/ios'

def do_ping(args):
    IP_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    match = IP_pattern.match(args[0])

    if match:
        return '/bin/ping -c 3 %s' % args[0]
    else:
        return 'ERROR'
