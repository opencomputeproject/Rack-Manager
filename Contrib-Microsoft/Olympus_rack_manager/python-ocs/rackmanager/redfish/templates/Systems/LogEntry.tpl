{
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/System/{{ID}}/LogServices/Members/Log/Entries/Members/$entry",
    "@odata.id": "/redfish/v1/Managers/System/{{ID}}/LogServices/Log/Entry/{{EntryID}}",
    "@odata.type": "#LogEntry.1.0.2.LogEntry",	
    "Id": "{{EntryID}}",
    "Name": "Blade SEL Log Entry {{EntryID}}",   
    % if defined ("members"):    
	    % for l, (ks, vs) in enumerate(members.iteritems()): 
	    	   <% if l != len(members)-1:
		            tag = ","               
		        else: 
		            tag = ""
		        end %>
	           
	    	  % if ks == "EntryType":
			        "EntryType": "{{vs}}"{{tag}}
			  % elif ks == "EntryCode":
			        "EntryCode": "{{vs}}"{{tag}}
			  % elif ks == "Created":
			        "Created": "{{vs}}"{{tag}}
			  % elif ks == "MessageId":
			        "MessageId": "{{vs}}"{{tag}}
	          % elif ks == "Message":
			        "Message": "{{vs}}"{{tag}}
	    	  % end
		% end
	% end 
}
