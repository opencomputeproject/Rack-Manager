<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
    
    if defined ("TemplateDefault"):
        setdefault ("Intf", "")
        setdefault ("Description", "")
        setdefault ("InterfaceHealth", "")
        setdefault ("InterfaceState", "")
        setdefault ("InterfaceStatus", "false")
        setdefault ("MacAddress", "")
        setdefault ("IPAddress", "")
        setdefault ("SubnetMask", "")
        setdefault ("AddressOrigin", "")
        if (Intf == "eth0"):
            setdefault ("Gateway", "")
        else:
            setdefault ("Management_Gateway", "")
            setdefault ("Management_Network", "")
        end
    end
%>
{
    "@odata.type": "#EthernetInterface.v1_0_0.EthernetInterface",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/EthernetInterfaces/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/EthernetInterface/{{Intf}}",
    "Id": "{{Intf}}",
    "Name": "{{Intf}}",
    "Description": "{{Description}}",
    "Status": {
    	<% if defined ("InterfaceHealth"):
    		tag = ","
		else:
			tag = ""
		end %>
    
        %if defined ("InterfaceState"):        	
        	"State": "{{InterfaceState}}"{{tag}}
		%end
        %if defined ("InterfaceHealth"):    
        	"Health": "{{InterfaceHealth}}"
        %end
    },
    %if defined ("InterfaceStatus"):
        "InterfaceEnabled": {{InterfaceStatus}},
    %end
    %if defined ("MacAddress"):    
    	"PermanentMACAddress": "{{MacAddress}}",
	%end
    "IPv4Addresses": [
        {
            %sepr = ""
	        %if defined ("IPAddress"):    
		    	"Address": "{{IPAddress}}"
		    	%sepr = ","
			%end
			%if defined ("SubnetMask"):    
		    	{{sepr}}"SubnetMask": "{{SubnetMask}}"
		    	%sepr = ","
			%end
			%if defined ("AddressOrigin"):    
		    	{{sepr}}"AddressOrigin": "{{AddressOrigin}}"
		    	%sepr = ","
			%end
			%if defined ("Gateway"):    
		    	{{sepr}}"Gateway": "{{Gateway}}"
			%end
        }
    ]
    %if (Intf == "eth1"):
        ,"Oem": {
            "Microsoft": {
                "@odata.type": "#OcsRackManager.v1_0_0.EthernetInterface"
                %if defined ("Management_Gateway"):
                    ,"MgmtGateway": "{{Management_Gateway}}"
                %end
                %if defined ("Management_Network"):
                    ,"MgmtNetmask": "{{Management_Network}}"
                %end
            }
        }
    %end
}
