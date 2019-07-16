<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#LogEntryCollection.LogEntryCollection",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/LogServices/Members/Log/Entries/$entry",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log/Entries",
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
				    		    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log/Entry/{{vs}}",
				    		    "@odata.type": "#LogEntry.1.0.2.LogEntry",	
				    	        "Id": "{{vs}}",
	            		        "Name": "Log Entry {{vs}}",
	        			  % elif ks == "Severity":
	        			        "Severity": "{{vs}}"{{tag}}
	        			  % elif ks == "Created":
	        			        "Created": "{{vs}}"{{tag}}
	        			  % elif ks == "Message":
	        			        "Message": "{{vs}}"{{tag}}
				          % elif ks == "Oem":
				          		 "Oem": {
					                "Microsoft": {
					                    "@odata.type": "#OcsRackManager.v1_0_0.LogEntry",
					                    % if isinstance(vs, dict):
										    % for j, (koem, voem) in enumerate(vs.iteritems()):
										    	  <% if j != len(vs)-1:
											            eol = ","               
											       else: 
											            eol = ""
											      end %>
										            
										    	  % if koem == "Component":
									                    "Component": "{{voem}}"{{eol}}	        
							        			  % elif koem == "PortId":
							        			        "PortId": "{{voem}}"{{eol}}
						        			      % elif koem == "DeviceId":
							        			        "DeviceId": "{{voem}}"{{eol}}		
					        			          % elif koem == "FanId":
							        			        "FanId": "{{voem}}"{{eol}}	
						        			      % elif koem == "SensorType":
	        			        						"SensorType": "{{voem}}"{{eol}}		        			      		
						        			      % end
				        			      	% end
			        			      	% end
					                }
					             }{{tag}}
				    	  % end
		    		% end
		        % end
	    	}{{closetag}}
		 	% end
	    ]
    %end
}
