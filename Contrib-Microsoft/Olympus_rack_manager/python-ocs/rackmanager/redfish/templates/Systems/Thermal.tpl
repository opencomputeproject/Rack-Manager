{
    "@odata.type": "#Thermal.v1_1_0.Thermal",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/System/{{ID}}/Thermal/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Thermal",
    "Id": "Thermal",
    "Name": "System Thermal"
    %if defined ("temps"):
        ,"Temperatures": [
            %sepr = ""
            %for i, temp in enumerate (temps):
                %temp_idx = i + 1
                {{sepr}}{
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Thermal#/Temperatures/{{temp_idx}}",
                    "MemberId": "{{temp_idx}}",
                    %if "Sensor_Description" in temp:
                        "Name": "{{temp["Sensor_Description"]}}",
                    %end
                    %if "Sensor_Number" in temp:
                        "SensorNumber": {{temp["Sensor_Number"]}},
                    %end
                    "Status": {
                        %stat_sep = ""
                        %if "State" in temp:
                            "State": "{{temp["State"]}}"
                            %stat_sep = ","
                        %end
                        %if "Health" in temp:
                            {{stat_sep}}"Health": "{{temp["Health"]}}"
                        %end
                    }
                    %if "Sensor_Reading" in temp:
                        ,"ReadingCelsius": {{temp["Sensor_Reading"]}}
                    %end
                }
                %sepr = ","
            %end
        ]
    %end
    %if defined ("fans"):
        ,"Fans": [
            %sepr = ""
            %for i, fan in enumerate (fans):
                %fan_idx = i + 1
                {{sepr}}{
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Thermal#/Fans/{{fan_idx}}",
                    "MemberId": "{{fan_idx}}"
                    %if "Fan_Name" in fan:
                        ,"Name": "{{fan["Fan_Name"]}}"
                    %end
                    %if "Health" in fan:
                        ,"Status": {
                            "Health": "{{fan["Health"]}}"
                        }
                    %end
                    %if "Fan_Reading" in fan:
                        ,"Reading": {{fan["Fan_Reading"]}}
                        ,"ReadingUnits": "RPM"
                    %end
                }
                %sepr = ","
            %end
        ]
    %end
}
