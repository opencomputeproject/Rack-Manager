{
    "@odata.type": "#Thermal.v1_1_0.Thermal",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/MgmtSwitch/Thermal/$entity",
    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Thermal",
    "Id": "Thermal",
    "Name": "Switch Thermal",
    "Temperatures": [
        {
            "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Thermal#/Temperatures/1",
            "MemberId": "1",
            "Status": {
                %if defined ("TemperatureSensorState"):
			        "Health": "{{TemperatureSensorState}}"
			    %end
            },
            %if defined ("ReadingTemp"):
		        "ReadingCelsius": {{ReadingTemp}}
		    %end
        }
    ]
}
