<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
        type = "AuxiliaryController"
    else:
        config = "Rack"
        type = "RackManager"
    end
    
    if defined ("TemplateDefault"):
        setdefault ("Package", "")
        setdefault ("Health", "")
        setdefault ("Rootfs", "")
        setdefault ("uboot", "")
        setdefault ("Kernel", "")
        setdefault ("DeviceTree", "")
        setdefault ("PRUFW", "")
        setdefault ("TFTPStatus", "")
        setdefault ("TFTPService", "false")
        setdefault ("NFSStatus", "")
        setdefault ("NFSService", "false")
        setdefault ("NTPState", "")
        setdefault ("NTPService", "false")
        setdefault ("NTPServer", "")
        setdefault ("ITPState", "")
        setdefault ("ITPService", "false")
        setdefault ("Local_Bypass", "false")
        setdefault ("Local_Enable", "false")
        setdefault ("Row_Bypass", "false")
        setdefault ("Row_Enable", "false")
        setdefault ("DateTime", "")
        setdefault ("Up_Time", "")
    end
%>
{
    "@odata.type": "#Manager.v1_1_0.Manager",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager",
    "Id": "{{config}}Manager",
    "Name": "{{config}} Manager",
    "ManagerType": "{{type}}",
    "Model": "M2010",
    %if defined ("DateTime"):
        "DateTime": "{{DateTime}}",
	%end
    %if defined ("Package"):
	    "FirmwareVersion": "{{Package}}",
	%end
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/{{config}}Manager/EthernetInterfaces"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices"
    },
    "Oem": {
        "Microsoft": {
            "@odata.type": "#OcsRackManager.v1_0_0.RackManager",
            %if defined ("Hostname"):
                "HostName": "{{Hostname}}",
        	%end
        	%if defined ("Up_Time"):
        	    "TimeSinceLastBoot": "{{Up_Time}}",
        	%end
            "Components": [
                {
                    "Name": "Rootfs",
                     %if defined ("Rootfs"):
                        "Version": "{{Rootfs}}"
           			 %end
                },
                {
                    "Name": "U-Boot",
                    %if defined ("uboot"):
                        "Version": "{{uboot}}"
           			%end
                },
                {
                    "Name": "Kernel",
                    %if defined ("Kernel"):
                        "Version": "{{Kernel}}"
           			%end
                },
                {
                    "Name": "Devicetree",
                    %if defined ("DeviceTree"):
                        "Version": "{{DeviceTree}}"
           			%end
                },
                {
                    "Name": "PRU",
                    %if defined ("PRUFW"):
                        "Version": "{{PRUFW}}"
                    %end
                }
            ],
            "TFTP": {
                %if defined ("TFTPStatus"):
                    "ServiceStatus": "{{TFTPStatus}}",
                %end
                %if defined ("TFTPService"):
                    "ServiceEnabled": {{TFTPService}},
                %end
               "Files": {
                    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/Tftp"
               }
            },
            "NFS": {
            	%sepr = "" 
                %if defined ("NFSStatus"):
                    "ServiceStatus": "{{NFSStatus}}"
                    %sepr = ","
       			%end
       			%if defined ("NFSService"):
                    {{sepr}}"ServiceEnabled": {{NFSService}}
       			%end
            },
            "NTP": {
            	%sepr = ""            		
            	%if defined ("NTPState"):
                    "ServiceStatus": "{{NTPState}}"
                    %sepr = ","
       			%end
       			%if defined ("NTPService"):
                    {{sepr}}"ServiceEnabled": {{NTPService}}
                    %sepr = ","
       			%end
       			%if defined ("NTPServer"):
       			    {{sepr}}"TimeServer": "{{NTPServer}}"
       			%end
            },
            %if (config == "Rack"):
                "RemoteITP": {
                    %sepr = ""
                    %if defined ("ITPState"):
                        "ServiceStatus": "{{ITPState}}"
                        %sepr = ","
                    %end
                    %if defined ("ITPService"):
                        {{sepr}}"ServiceEnabled": {{ITPService}}
                    %end
                },
            %end
            "ThrottleControl": {
                %sepr = ""
                %if defined ("Local_Bypass"):
                    "LocalBypass": {{Local_Bypass}}
                    %sepr = ","
                %end
                %if defined ("Local_Enable"):
                    {{sepr}}"LocalEnable": {{Local_Enable}}
                    %sepr = ","
                %end
                %if (config == "Row"):
                    %if defined ("Row_Bypass"):
                        {{sepr}}"RowBypass": {{Row_Bypass}}
                        %sepr = ","
                    %end
                    %if defined ("Row_Enable"):
                        {{sepr}}"RowEnable": {{Row_Enable}}
                    %end
                %end
            }
        }
    },
    "Links": {
        "ManagerForChassis": [
            %if (config == "Rack"):
                {
                    "@odata.id": "/redfish/v1/Chassis/Rack"
                }
                %if (not RackManagerConfig == rm_mode_enum.standalone_rackmanager):
                    ,{
                        "@odata.id": "/redfish/v1/Chassis/PMDU"
                    }
                %end
            %else:
                {
                    "@odata.id": "/redfish/v1/Chassis/RMM"
                }
            %end
        ]
    },
    "Actions": {
        "Oem": {
            "OcsRackManager.v1_0_0.#Manager.FirmwareUpdate": {
                "target": "/redfish/v1/Managers/{{config}}Manager/Actions/Manager.FirmwareUpdate"
            }
        }
    }
}
