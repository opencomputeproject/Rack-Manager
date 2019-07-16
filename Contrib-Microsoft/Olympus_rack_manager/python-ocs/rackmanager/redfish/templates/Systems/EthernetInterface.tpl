{
    "@odata.type": "#EthernetInterface.v1_0_0.EthernetInterface",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/System/{{ID}}/EthernetInterfaces/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/System/{{ID}}/EthernetInterface",
    "Id": "Ethernet",
    "Name": "Ethernet",
    "Description": "Management Network Connection",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    %if defined("MACAddress"):
    	"MACAddress": "{{MACAddress}}",
	%end
    "IPv4Addresses": [
        {
	        %if defined("Address"):
		    	"Address": "{{Address}}",
			%end
			%if defined("SubnetMask"):
		    	"SubnetMask": "{{SubnetMask}}",
			%end
			%if defined("AddressOrigin"):
		    	"AddressOrigin": "{{AddressOrigin}}",
			%end
			%if defined("Gateway"):
		    	"Gateway": "{{Gateway}}"
			%end
        }
    ]
}
