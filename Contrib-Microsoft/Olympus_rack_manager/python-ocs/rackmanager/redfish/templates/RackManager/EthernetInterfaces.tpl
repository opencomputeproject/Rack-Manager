<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/EthernetInterfaces/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/EthernetInterfaces",
    "Name": "Ethernet Interface Collection",
	"Description": "{{config}} Manager Ethernet Interfaces",
    %if defined ("Interfaces_list"):
	    "Members@odata.count": {{len(Interfaces_list)}},
	    "Members": [
	    	% for  i, (k, v) in enumerate(Interfaces_list.iteritems()):   
	    	{      
			    <% if i != len(Interfaces_list)-1:
			            closetag = ","               
			       else: 
			            closetag = ""
			     end %>
			     "@odata.id": "/redfish/v1/Managers/{{config}}Manager/EthernetInterface/{{v}}"
		    }{{closetag}}
	 	    % end
	    ]
    %end
}