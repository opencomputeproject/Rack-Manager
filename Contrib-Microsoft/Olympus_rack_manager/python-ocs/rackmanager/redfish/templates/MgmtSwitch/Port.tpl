{
    "@odata.type": "#OcsMgmtSwitch.v1_0_0.Port",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/MgmtSwitch/Port/{{ID}}/$entity",
    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/{{ID}}",
    "Id": "Port{{ID}}",
    "Name": "Switch Port {{ID}}",   
	%if defined ("MACAddress"):
    	"MACAddress": "{{MACAddress}}",
	%end    
	%if defined ("LinkState"):
    	"LinkState": "{{LinkState}}",
	%end    
	%if defined ("AdminState"):
    	"AdminState": "{{AdminState}}",
	%end    
	%if defined ("DHCPAddress"):
    	"DHCPAddress": "{{DHCPAddress}}",
	%end
    %if defined ("DHCPLeaseState"):
    	"DHCPLeaseState": "{{DHCPLeaseState}}"
	%end
}
