<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    %if defined ("members"):
	    % for  i, (k, v) in enumerate(members.iteritems()):   
		     % if isinstance(v, dict):
			    % for l, (ks, vs) in enumerate(v.iteritems()): 
			    	   <% if l != len(v)-1:
				            tag = ","               
				        else: 
				            tag = ""
				        end %>
			           
			    	  % if ks == "RecordId":
							"@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log/Entry/{{Entry}}",
							"@odata.type": "#LogEntry.v1_0_2.LogEntry",
							"@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/LogServices/Members/Log/Entries/Members/$entry",
			    	        "Id": "{{Entry}}",
							"Name": "Log Entry {{Entry}}",
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
	 	% end 
 	% end       
}
