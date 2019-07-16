{
    "@odata.type": "#LogEntryCollection.LogEntryCollection",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/System/{{EntryID}}/LogServices/Members/Log/Entries/$entry",
    "@odata.id": "/redfish/v1/Managers/System/{{EntryID}}/LogServices/Log/Entries",
    "Name": "Log Entry Collection",
    % if defined ("members"):
	    "Members@odata.count": {{len(members)}},
	    "Members": [
	        % for  i, (k, v) in enumerate(members.iteritems()):   
	    	{      
			    <% if i != len(members)-1:
			            closetag = ","               
			       else: 
			            closetag = ""
			     end %>
			     % if isinstance(v, dict):
				    % for l, (ks, vs) in enumerate(v.iteritems()): 
				    	   <% if l != len(v)-1:
					            tag = ","               
					        else: 
					            tag = ""
					        end %>
				           
				    	  % if ks == "RecordId":
				    		    "@odata.id": "/redfish/v1/Managers/System/{{EntryID}}/LogServices/Log/Entry/{{vs}}",
				    		    "@odata.type": "#LogEntry.1.0.2.LogEntry",	
				    	        "Id": "{{vs}}",
	            		        "Name": "Blade SEL Log Entry {{vs}}",   
	        			  % elif ks == "EntryType":
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
	    	}{{closetag}}
		 	% end
	    ]
    % end
}
