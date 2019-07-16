# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ipmicmd_library import *

sdr_cachefile_path = "/tmp/sdrcache/"

# Check if sdcache directory exists if not create
if not os.path.exists(sdr_cachefile_path):
    os.makedirs("/tmp/sdrcache")


def system_thermal_info(serverid):
    try:
        interface = get_ipmi_interface(serverid)

        thermalrsp = {}
        thermalrsp["Temperatures"] = {}
        thermalrsp["Fans"] = {}
        completionstate = True

        if "Failed:" in interface:
            thermalrsp["Temperatures"] = set_temparatures_default_values()
            thermalrsp["Fans"] = set_fans_default_values()
            thermalrsp[completion_code.cc_key] = completion_code.failure
            thermalrsp[completion_code.desc] = interface
            return thermalrsp

        temp_data = system_temperature_info(serverid)

        if completion_code.cc_key in temp_data.keys() \
                and temp_data[completion_code.cc_key] == completion_code.failure:
            thermalrsp["Temperatures"] = set_temparatures_default_values()
            thermalrsp["Temperatures"][
                completion_code.desc] = "Failed to get Temperature sensors data"
            completionstate &= False
        elif temp_data is None or not temp_data:  # Check empty or none
            # log.error("Redfish\System: failed to get blade details : %s" %bladeresp)
            thermalrsp["Temperatures"] = set_temparatures_default_values()
            thermalrsp["Temperatures"][
                completion_code.desc] = "Temperature sensor response is empty"
            completionstate &= False
        else:
            if completion_code.cc_key in temp_data.keys():
                temp_data.pop(completion_code.cc_key, None)
            thermalrsp["Temperatures"] = temp_data["members"]
            completionstate &= True

        fan_data = system_fan_info(serverid)

        if completion_code.cc_key in fan_data.keys() and fan_data[completion_code.cc_key] == completion_code.failure:
            thermalrsp["Fans"] = set_fans_default_values()
            thermalrsp["Fans"][
                completion_code.desc] = "Failed to get Fan sensors data"
            completionstate &= False
        elif fan_data is None or not fan_data:  # Check empty or none
            #log.error("Redfish\System: failed to get blade details : %s" %bladeresp)
            thermalrsp["Fans"] = set_fans_default_values()
            thermalrsp["Fans"][
                completion_code.desc] = "Fan sensor response is empty"
            completionstate &= False
        else:
            if completion_code.cc_key in fan_data.keys():
                fan_data.pop(completion_code.cc_key, None)
            thermalrsp["Fans"] = fan_data
            completionstate &= True

    except Exception, e:
        #Log_ERR("System info exception : ", e)
        thermalrsp["Temperatures"] = set_temparatures_default_values()
        thermalrsp["Fans"] = set_fans_default_values()
        thermalrsp[completion_code.cc_key] = completion_code.failure
        thermalrsp[completion_code.desc] = "Thermal info call exception :", e
        return thermalrsp

    if completionstate:
        thermalrsp[completion_code.cc_key] = completion_code.success
    else:
        thermalrsp[completion_code.cc_key] = completion_code.failure
    return thermalrsp


def system_temperature_info(serverid):
    try:
        interface = get_ipmi_interface(serverid)
        temp_info = {}

        if "Failed:" in interface:
            temprsp = set_temparatures_default_values()
            temprsp[completion_code.cc_key] = completion_code.failure
            temprsp[completion_code.desc] = interface
            return temprsp

        temp_cmd = get_ipmi_commands(interface, str(serverid), "temp")

        if temp_cmd is None:
            temprsp = set_temparatures_default_values()
            temprsp[completion_code.cc_key] = completion_code.failure
            temprsp[
                completion_code.desc] = "Temperature sensors ipmi command incorrect:", temp_cmd
            return temprsp

        temp_info["members"] = parse_temperature_sensor_data(temp_cmd)

        if temp_info is None:
            temprsp = set_temparatures_default_values()
            temprsp[completion_code.cc_key] = completion_code.failure
            temprsp[completion_code.desc] = "Temperature sensors data is empty"
            return temprsp

    except Exception, e:
        #Log_ERR("System info exception : ", e)
        temprsp = set_temparatures_default_values()
        temprsp[completion_code.cc_key] = completion_code.failure
        temprsp[completion_code.desc] = "Temperature sensor call exception :", e
        return temprsp

    temp_info[completion_code.cc_key] = completion_code.success
    return temp_info


def system_fan_info(serverid):
    try:
        interface = get_ipmi_interface(serverid)

        if "Failed:" in interface:
            fanrsp = set_fans_default_values()
            fanrsp[completion_code.cc_key] = completion_code.failure
            fanrsp[completion_code.desc] = interface
            return fanrsp

        fan_cmd = get_ipmi_commands(interface, str(serverid), "fan")

        if fan_cmd is None:
            fanrsp = set_fans_default_values()
            fanrsp[completion_code.cc_key] = completion_code.failure
            fanrsp[
                completion_code.desc] = "Fan sensors ipmi command incorrect :", fan_cmd
            return fanrsp

        fan_info = parse_fan_sensor_data(serverid)

        if fan_info is None:
            fanrsp = set_temparatures_default_values()
            fanrsp[completion_code.cc_key] = completion_code.failure
            fanrsp[completion_code.desc] = "Temperature sensors data is empty"
            return fanrsp

    except Exception, e:
        #Log_ERR("System info exception : ", e)
        fanrsp = set_fans_default_values()
        fanrsp[completion_code.cc_key] = completion_code.failure
        fanrsp[completion_code.desc] = "Fan sensor call exception :", e
        return fanrsp

    return fan_info


def get_ipmi_commands(cmdinterface, bladeId, sensortype):
    # Verify sdr cache file exists
    filename = 'blade' + bladeId + ".sdr"
    filepath = sdr_cachefile_path + filename
    iscache = verify_cachefile_exists(filepath, filename, cmdinterface)
    sensor_cmd = ""

    if iscache:
        #log.info("BladeLog: %s cache file exists.Running commands through cache file" %filename)
        # commands for getting temperatures and fans data from cache file
        if sensortype == "temp":
            tempcmd = '-S' + ' ' + filepath + ' ' + 'sdr type temperature -v'
            sensor_cmd = cmdinterface + ' ' + tempcmd
        elif sensortype == "fan":
            fancmd = '-S' + ' ' + filepath + ' ' + 'ocsoem redfish fan'
            sensor_cmd = cmdinterface + ' ' + fancmd
        else:
            return None
    else:
        #log.info("BladeLog: %s cache file does not exists.Running direct commands" %filename)
        if sensortype == "temp":
            tempcmd = 'sdr type temperature -v'  # IPMI Command to get temperatures data
            sensor_cmd = cmdinterface + ' ' + tempcmd
        elif sensortype == "fan":
            fancmd = 'ocsoem redfish fan'  # IPMI Command to get fans data
            sensor_cmd = cmdinterface + ' ' + fancmd
        else:
            return None

    return sensor_cmd

# setting default value as NA as some of the keys may not be present in
# the sdr output for temparatures


def set_temparatures_default_values():

    temparature = {}

    temparature["SensorNumber"] = "na"
    temparature["Name"] = "na"
    temparature["MemberId"] = "na"
    temparature["Status"] = {}
    temparature["Status"]["State"] = "na"
    temparature["Status"]["Health"] = "na"
    temparature["PhysicalContext"] = "na"
    temparature["ReadingCelsius"] = "na"
    temparature["UpperThresholdNonCritical"] = "na"
    temparature["UpperThresholdCritical"] = "na"
    temparature["UpperThresholdFatal"] = "na"
    temparature["LowerThresholdNonCritical"] = "na"
    temparature["LowerThresholdCritical"] = "na"
    temparature["LowerThresholdFatal"] = "na"
    temparature["MinReadingRange"] = "na"
    temparature["MaxReadingRange"] = "na"

    return temparature

# setting default value as NA as some of the keys may not be present in
# the sdr output for fans


def set_fans_default_values():

    fans = {}

    fans["MemberId"] = "na"
    fans["FanName"] = "na"
    fans["Status"] = {}
    fans["Status"]["State"] = "na"
    fans["Status"]["Health"] = "na"
    fans["ReadingRPM"] = "na"
    fans["UpperThresholdNonCritical"] = "na"
    fans["UpperThresholdCritical"] = "na"
    fans["UpperThresholdFatal"] = "na"
    fans["LowerThresholdNonCritical"] = "na"
    fans["LowerThresholdCritical"] = "na"
    fans["LowerThresholdFatal"] = "na"
    fans["MinReadingRange"] = "na"
    fans["MaxReadingRange"] = "na"

    return fans


def parse_temperature_sensor_data(cmd):
    try:
        output = call_ipmi(cmd, "Temperature Sensors")
        temprsp = {}

        if "ErrorCode" in output:
            temprsp = set_temparatures_default_values()
            temprsp[completion_code.cc_key] = completion_code.failure
            temprsp[completion_code.desc] = "get temperature sensor ipmi call error "
            return temprsp

        if(output['status_code'] == 0):
            # Populating temperatures data
            temperatures = output['stdout'].split('\n\n')

            temperaturesdata = filter(None, temperatures)  # Remove empty data

            if len(temperaturesdata) == 0:
                temprsp = set_temparatures_default_values()
                temprsp[completion_code.cc_key] = completion_code.failure
                temprsp[completion_code.desc] = "Temperatures list is empty"
                return temprsp
                #log.error("Temperatures data list is empty: %s" %temperaturesdata)
            else:
                tempid = 1
                for value in temperaturesdata:
                    strtemp = str(tempid)
                    tdata = value.split('\n')
                    # Skipping empty lists if any
                    if len(tdata) == 0:
                        break
                    temprsp[strtemp] = set_temparatures_default_values()

                    for tempVal in tdata:
                        if "Sensor ID" in tempVal:
                            sensorDetails = tempVal.split(":")[-1]
                            sensor = sensorDetails.split(" ")
                            temprsp[strtemp]["SensorNumber"] = sensor[2]
                            temprsp[strtemp]["Name"] = sensor[1]
                        elif "Entity ID " in tempVal:
                            entityId = tempVal.split(":")[-1].strip()
                            memberId = entityId.split(" ")
                            temprsp[strtemp]["MemberId"] = memberId[1]

                        elif "Status" in tempVal:
                            temprsp[strtemp]["Status"][
                                "State"] = tempVal.split(":")[-1].strip()
                            temprsp[strtemp]["Status"][
                                "Health"] = tempVal.split(":")[-1].strip()
                            temprsp[strtemp]["PhysicalContext"] = tempVal.split(
                                ":")[-1].strip()

                        elif "Sensor Reading" in tempVal:
                            temprsp[strtemp]["ReadingCelsius"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Upper non-critical" in tempVal:
                            temprsp[strtemp]["UpperThresholdNonCritical"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Upper critical" in tempVal:
                            temprsp[strtemp]["UpperThresholdCritical"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Upper non-recoverable" in tempVal:
                            temprsp[strtemp]["UpperThresholdFatal"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Lower non-critical" in tempVal:
                            temprsp[strtemp]["LowerThresholdNonCritical"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Lower critical" in tempVal:
                            temprsp[strtemp]["LowerThresholdCritical"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Lower non-recoverable" in tempVal:
                            temprsp[strtemp]["LowerThresholdFatal"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Normal Minimum" in tempVal:
                            temprsp[strtemp]["MinReadingRange"] = tempVal.split(
                                ":")[-1].strip()
                        elif "Normal Maximum" in tempVal:
                            temprsp[strtemp]["MaxReadingRange"] = tempVal.split(
                                ":")[-1].strip()
                    tempid = tempid + 1

                return temprsp
        else:

            tmperrdata = set_temparatures_default_values()

            errorData = output['stderr'].split('\n')

            errorData = filter(None, errorData)

            tmperrdata[completion_code.cc_key] = completion_code.failure

            for data in errorData:
                if "Error" in data:
                    tmperrdata[completion_code.desc] = data.split(
                        ":")[-1].strip()
                elif completion_code.cc_key in data:
                    tmperrdata[completion_code.ipmi_code] = data.split(
                        ":")[-1].strip()
                else:
                    tmperrdata[completion_code.desc] = data.strip()
                    break

            if tmperrdata[completion_code.desc] == "":
                tmperrdata[completion_code.desc] = errorData.strip()

            return tmperrdata

    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        tempexception = set_temparatures_default_values()
        tempexception[completion_code.cc_key] = completion_code.failure
        tempexception[completion_code.desc] = "temprature sensor parse results() Exception: ", e
        return tempexception


def parse_fan_sensor_data(cmd):
    try:
        output = call_ipmi(cmd, "Fan Sensors")
        fanrsp = {}

        if "ErrorCode" in output:
            fanrsp = set_fans_default_values()
            fanrsp[completion_code.cc_key] = completion_code.failure
            fanrsp[completion_code.desc] = "get fan sensor ipmi call error "
            return fanrsp

        if(output['status_code'] == 0):
            # Populating fans data
            fans = output['stdout'].split('\n\n')

            fansdata = filter(None, fans)  # Remove empty data

            fanrsp = fan_sub_parser(fansdata)
            return fanrsp

        else:

            fanerrdata = set_fans_default_values()

            errorData = output['stderr'].split('\n')

            errorData = filter(None, errorData)

            fanerrdata[completion_code.cc_key] = completion_code.failure

            for data in errorData:
                if "Error" in data:
                    fanerrdata[completion_code.desc] = data.split(
                        ":")[-1].strip()
                elif completion_code.cc_key in data:
                    fanerrdata[completion_code.ipmi_code] = data.split(
                        ":")[-1].strip()
                else:
                    fanerrdata[completion_code.desc] = data.strip()
                    break

            if fanerrdata[completion_code.desc] == "":
                fanerrdata[completion_code.desc] = errorData.strip()

            return fanerrdata

    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        fanexception = set_fans_default_values()
        fanexception[completion_code.cc_key] = completion_code.failure
        fanexception[completion_code.desc] = "Fan sensor parse results() Exception: ", e
        return fanexception


def fan_sub_parser(fansdata):
    try:
        fanrsp = {}
        if len(fansdata) == 0:
            fanrsp = set_fans_default_values()
            fanrsp[completion_code.cc_key] = completion_code.failure
            fanrsp[completion_code.desc] = "Fan sensor list is empty"
            return fanrsp
        else:
            fanid = 0
            for value in fansdata:
                strFan = str(fanid)
                fandata = value.split('\n')
                # Skipping empty lists if any
                if len(fandata) == 0:
                    break
                fanrsp[strFan] = set_fans_default_values()

                for fanVal in fandata:
                    if "Sensor ID" in fanVal:
                        sensorDetails = fanVal.split(":")[-1]
                        sensor = sensorDetails.split(" ")
                        fanrsp[strFan]["FanName"] = sensor[1]
                    elif "Entity ID " in fanVal:
                        entityId = fanVal.split(":")[-1]
                        memberId = entityId.split(" ")
                        fanrsp[strFan]["MemberId"] = memberId[1]
                    elif "Status" in fanVal:
                        fanrsp[strFan]["Status"]["State"] = fanVal.split(":")[-1]
                        fanrsp[strFan]["Status"]["Health"] = fanVal.split(":")[-1]
                    elif "Sensor Reading" in fanVal:
                        fanrsp[strFan]["ReadingRPM"] = fanVal.split(":")[-1]
                    elif "Upper non-critical" in fanVal:
                        fanrsp[strFan][
                            "UpperThresholdNonCritical"] = fanVal.split(":")[-1]
                    elif "Upper critical" in fanVal:
                        fanrsp[strFan][
                            "UpperThresholdCritical"] = fanVal.split(":")[-1]
                    elif "Upper non-recoverable" in fanVal:
                        fanrsp[strFan][
                            "UpperThresholdFatal"] = fanVal.split(":")[-1]
                    elif "Lower non-critical" in fanVal:
                        fanrsp[strFan][
                            "LowerThresholdNonCritical"] = fanVal.split(":")[-1]
                    elif "Lower critical" in fanVal:
                        fanrsp[strFan][
                            "LowerThresholdCritical"] = fanVal.split(":")[-1]
                    elif "Lower non-recoverable" in fanVal:
                        fanrsp[strFan][
                            "LowerThresholdFatal"] = fanVal.split(":")[-1]
                    elif "Normal Minimum" in fanVal:
                        fanrsp[strFan][
                            "MinReadingRange"] = fanVal.split(":")[-1]
                    elif "Normal Maximum" in fanVal:
                        fanrsp[strFan][
                            "MaxReadingRange"] = fanVal.split(":")[-1]
                fanid = fanid + 1
                if fanid == 6:
                    break   # Remove last empty data

            fanrsp[completion_code.cc_key] = completion_code.success
            return fanrsp
    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        fanexception = set_fans_default_values()
        fanexception[completion_code.cc_key] = completion_code.failure
        fanexception[completion_code.desc] = "Fan sensor sub parser results() Exception: ", e
        return fanexception
