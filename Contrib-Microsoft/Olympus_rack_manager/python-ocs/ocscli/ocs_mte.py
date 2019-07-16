# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import sys
import time
import os.path
import argparse
import datetime
import subprocess

from utils_print import *
from ocsaudit_log import *
from controls.utils import *
from ocs_mte_action import *

avail_cmd = {
    'ocs-gpio': do_ocsgpio, 
    'ocs-pru': do_ocspru, 
    'ocs-hsc': do_ocshsc, 
    'ocs-hdc': do_ocshdc, 
    'ocs-fru': do_ocsfru, 
    'ocs-pmic': do_ocspmic, 
    'ocs-adccalibration': do_ocsadccalibration,
    'ocs-mac': do_ocsmac,
    'stream': do_stream, 
    'sysbench': do_sysbench, 
    'memtester': do_memtester,
    'ttys0': do_ttyS0,
    'ttys1': do_ttyS1, 
    'ttys2': do_ttyS2, 
    'fio': do_fio, 
    'lmbench3': do_lmbench3, 
    'iperf': do_iperf, 
    'minicom': do_minicom,
    'reboot': do_reboot, 
    'date': do_date, 
    'hwclock': do_hwclock,  
    'i2cdump': do_i2cdump, 
    'i2cdetect': do_i2cdetect, 
    'i2cset': do_i2cset, 
    'i2cget': do_i2cget,
    'cpuinfo': do_cpuinfo,
    'meminfo': do_meminfo,
    'qspiinfo': do_qspiinfo,
    'mmcinfo': do_mmcinfo,
    'ping': do_ping,
}

def mte_getutilityname(parser):
    parser.add_argument('-u', dest = 'util', required = True, help = 'Utility to run')

def mte_getutilityparams(parser):
    parser.add_argument('-p', dest = 'params', type = str, nargs = "*", required = False, help = 'Utility parameters')

def mte_gettimes(parser):
    parser.add_argument('-t', dest = 'times', type = int, required=False, help = 'Run times')

def mte_getduration(parser):
    parser.add_argument('-d', dest = 'duration', type = int, required = False, help = 'Run duration')

def mte_run(cmd):
    if cmd == 'ERROR':
        print_response(set_failure_dict("Command error", completion_code.failure))
    else:
        process = subprocess.Popen([cmd], stderr = subprocess.PIPE, shell = True)
        output, errorMsg = process.communicate() 
                               
    return errorMsg

def find_all_running_mte(output):
    mte_list = []
    for cmd in avail_cmd:
        if cmd in output:
            mte_list.append(cmd)
    return mte_list

def start_ipmitool(args):
    try:
        command = '/usr/bin/ipmitool'

        count = len(args)
        for param in args:
            if ';' in param or '&' in param or '|' in param or '>' in param:
                print_response(set_failure_dict("Access denied", completion_code.failure))
                return
            else:                
                if param == '-i':
                    param ='-I'
                elif count > 1 and param == '-h':
                    param = '-H'
                elif param == '-u':
                    param = '-U'
                elif param == '-p':
                    param = '-P'
                    
                command += ' '+ param        

        mte_run(command)
        
    except Exception, e:
        print_response(set_failure_dict("start_ipmitool - Exception: {0}".format(e), completion_code.failure))
        return
    
def secure_copy(args):
    try:
        command = 'scp'

        for param in args:
            if ';' in param or '&' in param or '|' in param or '>' in param:
                print_response(set_failure_dict("Access denied", completion_code.failure))
                return
            else:                
                command += ' ' + param        

        errorMsg = mte_run(command)
        
        if errorMsg:
            print_response(set_failure_dict("Failed to run command scp: {0}".format(errorMsg.strip().split(":")[-1]), 
                                        completion_code.failure)) 
        
    except Exception,e:
        print_response(set_failure_dict("secure_copy - Exception: {0}".format(e), completion_code.failure))
        return
    
def start_mte(command):
    try:
        parser = argparse.ArgumentParser(description='Execute MTE utility')
        mte_getutilityname(parser)
        mte_getutilityparams(parser)
        mte_gettimes(parser)
        mte_getduration(parser)
        
        ocsaudit_log_command("", cmd_type.type_start, cmd_interface.interface_ocscli, 
                             "mte", " ".join(command))
    
        args = parse_args_retain_case(parser, command)
    
        if args.util not in avail_cmd:
            print_response(set_failure_dict("{0} not available".format(args.util), completion_code.failure))
            return
    
        if args.params:
            for param in args.params:
                if ';' in param or '&' in param or '|' in param or '>' in param:
                    print_response(set_failure_dict("Access denied", completion_code.failure))
                    return
    
        if args.times and args.duration:
            print_response(set_failure_dict("Only one of (-t, -d) can be used at a time", completion_code.failure))
            return

        if args.times:
            times_file = '/tmp/times'
            if os.path.isfile(times_file):
                os.remove(times_file)

            open(times_file, 'a').close()

            while args.times > 0:
                if os.path.isfile(times_file) == False:
                    break
                print args.times
                args.times -= 1

                if args.params:
                    errorMsg = mte_run(avail_cmd[args.util](args.params))
                else:
                    errorMsg = mte_run(avail_cmd[args.util]())
                if errorMsg:    
                    print_response(set_failure_dict("Failed to run command {0}: {1}".format(args.util, errorMsg.strip().split(":")[-1]), 
                                                    completion_code.failure))

        elif args.duration:
            duration_file = '/tmp/duration'
            if os.path.isfile(duration_file):
                os.remove(duration_file)

            open(duration_file, 'a').close()

            duration = args.duration * 60
            while duration > 0:
                if os.path.isfile(duration_file) == False:
                    break

                start = time.time()

                if args.params:
                    errorMsg = mte_run(avail_cmd[args.util](args.params))
                else:
                    errorMsg = mte_run(avail_cmd[args.util]())
                    
                if errorMsg:    
                    print_response(set_failure_dict("Failed to run command {0}: {1}".format(args.util, errorMsg.strip().split(":")[-1]), 
                                                    completion_code.failure))

                stop = time.time()
                diff = int(stop - start)
                duration -= diff

        else:
            if args.params:
                errorMsg = mte_run(avail_cmd[args.util](args.params))
            else:
                errorMsg = mte_run(avail_cmd[args.util]())
            
            if errorMsg:    
                print_response(set_failure_dict("Failed to run command {0}: {1}".format(args.util, errorMsg.strip().split(":")[-1]), 
                                                completion_code.failure))  

    except Exception, e:
        print_response(set_failure_dict("start_mte - Exception: {0}".format(e), completion_code.failure))

def stop_mte():
    curprocess = ""
    try:
        if os.path.isfile('/tmp/times'):
            os.remove('/tmp/times')
        if os.path.isfile('/tmp/duration'):
            os.remove('/tmp/duration')
    
        ocsaudit_log_command("", cmd_type.type_stop, cmd_interface.interface_ocscli, 
                             "mte", "")
        
        ps_output = subprocess.check_output('ps', shell=True)
        list = find_all_running_mte(ps_output)
    
        for kill in list:
            for line in ps_output.splitlines(True):
                if kill in line:
                    strList = line.split()
                    killString = "kill -9 %s" % strList[0]
                    curprocess = kill
                    subprocess.check_output(killString, shell=True, stderr = subprocess.STDOUT)
                    print "%s killed" % kill
                    break
                
    except subprocess.CalledProcessError as e:
        print_response(set_failure_dict("Failed to kill process: {0}".format(curprocess), completion_code.failure))
                
    except Exception, e:
        print_response(set_failure_dict("stop_mte - Exception: {0}".format(e), completion_code.failure))

def show_mte():
    ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                         "mte", "")
        
    ps_output = subprocess.check_output('ps', shell=True)
    list = find_all_running_mte(ps_output)
    print 'Running MTE utilities:'
    for running in list:
        print running
