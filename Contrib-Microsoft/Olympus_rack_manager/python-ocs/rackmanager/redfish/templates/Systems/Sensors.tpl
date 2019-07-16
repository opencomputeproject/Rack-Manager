{
    "@odata.type": "#Ocs.v1_0_0.SensorService",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/System/{{ID}}/Sensors/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Sensors",
    "Id": "Sensors",
    "Name": "System Sensors"
    %if defined ("sensors"):
        ,"Sensors": [
            %sepr = ""
            %for i, sensor in enumerate (sensors):
                %idx = i + 1
                {{sepr}}{
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Sensors#/Sensors/{{idx}}",
                    "MemberId": "{{idx}}",
                    %if "Sensor_Description" in sensor:
                        "Name": "{{sensor["Sensor_Description"]}}",
                    %end
                    %if "Sensor_Number" in sensor:
                        "SensorNumber": "{{sensor["Sensor_Number"]}}",
                    %end
                    %if "Sensor_Entity_ID" in sensor:
                        "EntityID": "{{sensor["Sensor_Entity_ID"]}}",
                    %end
                    "Status": {
                        %stat_sep = ""
                        %if "State" in sensor:
                            "State": "{{sensor["State"]}}"
                            %stat_sep = ","
                        %end
                        %if "Health" in sensor:
                            {{stat_sep}}"Health": "{{sensor["Health"]}}"
                        %end
                    }
                    %if "Sensor_Reading" in sensor:
                        ,"Reading": "{{sensor["Sensor_Reading"]}}"
                    %end
                }
                %sepr = ","
            %end
        ]
    %end
}
