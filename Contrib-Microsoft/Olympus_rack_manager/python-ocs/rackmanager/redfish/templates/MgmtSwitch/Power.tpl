{
    "@odata.type": "#Power.v1_1_0.Power",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/MgmtSwitch/Power/$entity",
    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Power",
    "Id": "Power",
    "Name": "Switch Power",
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Power#/PowerSupplies/1",
            "MemberId": "1",
            "Name": "Main Power Supply",
            "Status": {
                %if defined ("MainPowerState"):
		        	"Health": "{{MainPowerState}}"
		    	%end
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Power#/PowerSupplies/2",
            "MemberId": "2",
            "Name": "Redundant Power Supply",
            "Status": {
                %if defined ("RedundantPowerState"):
		        	"Health": "{{RedundantPowerState}}"
		    	%end
            }
        }
    ]
}