<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Manufacturer", "")
        setdefault ("Server_HWVersion", "")
        setdefault ("SKU", "")
        setdefault ("SerialNumber", "")
        setdefault ("PartNumber", "")
        setdefault ("Description", "")
        setdefault ("UUID", "")
        setdefault ("HostName", "")
        setdefault ("Server_PowerState", "")
        setdefault ("BootSourceOverrideEnabled", "false")
        setdefault ("BootSourceOverrideTarget", "")
        setdefault ("BootSourceOverrideMode", "")
        setdefault ("Server_ProcessorSummary_Count", "0")
        setdefault ("Server_ProcessorSummary_Model", "")
        setdefault ("Server_ProcessorSummary_Status_State", "")
        setdefault ("Server_ProcessorSummary_Status_HealthRollUp", "")
        setdefault ("Server_ProcessorSummary_Status_Health", "")
        setdefault ("Server_MemorySummary_TotalSystemMemoryGib", "0")
        setdefault ("Server_MemorySummary_Status_State", "")
        setdefault ("Server_MemorySummary_Status_HealthRollUp", "")
        setdefault ("Server_MemorySummary_Status_Health", "")
        setdefault ("Server_Status_State", "")
        setdefault ("Server_Status_HealthRollUp", "")
        setdefault ("Server_Status_Health", "")
        setdefault ("PhysicalPresence", "false")
        setdefault ("Default_Power_State", "")
        setdefault ("Server_CpldVersion", "")
    end
%>
{
    "@odata.type": "#ComputerSystem.v1_1_0.ComputerSystem",
    "@odata.context": "/redfish/v1/$metadata#Systems/Members/$entity",
    "@odata.id": "/redfish/v1/System/{{ID}}",
    "Id": "{{ID}}",
    "Name": "Slot{{ID}}",
    "SystemType": "Physical",
    %if defined ("AssetTag"):
        "AssetTag": "{{AssetTag}}",
    %end
    %if defined ("Manufacturer"):
        "Manufacturer": "{{Manufacturer}}",
    %end
    %if defined ("Server_HWVersion"):
        "Model": "{{Server_HWVersion}}",
    %end
    %if defined ("SKU"):
        "SKU": "{{SKU}}",
    %end
    %if defined ("SerialNumber"):
        "SerialNumber": "{{SerialNumber}}",
    %end
    %if defined ("PartNumber"):
        "PartNumber": "{{PartNumber}}",
    %end
    %if defined ("Description"):
        "Description": "{{Description}}",
    %end
    %if defined ("UUID"):
	    "UUID": "{{UUID}}",
    %end
    %if defined ("HostName"):
        "HostName": "{{HostName}}",
    %end
    %if defined ("Server_PowerState"):
        "PowerState": "{{Server_PowerState}}",
    %end
    "Boot": {
        %sepr = ""
	    %if defined ("BootSourceOverrideEnabled"):
	        "BootSourceOverrideEnabled": "{{BootSourceOverrideEnabled}}"
	        %sepr = ","
	    %end
	    %if defined ("BootSourceOverrideTarget"):
	        {{sepr}}"BootSourceOverrideTarget": "{{BootSourceOverrideTarget}}",
	        "BootSourceOverrideTarget@Redfish.AllowableValues": [
	            "None",
	            "Pxe",
	            "Floppy",
	            "Hdd",
	            "BiosSetup"
	        ]
	        %sepr = ","
	    %end
	    %if defined ("BootSourceOverrideMode"):
	        {{sepr}}"BootSourceOverrideMode": "{{BootSourceOverrideMode}}"
	    %end
    },
    %if defined ("Server_BiosVersion"):
        "BiosVersion": "{{Server_BiosVersion}}",
    %end
    "ProcessorSummary": {
        %if defined ("Server_ProcessorSummary_Count"):
            "Count": {{Server_ProcessorSummary_Count}},
        %end
        %if defined ("Server_ProcessorSummary_Model"):
            "Model": "{{Server_ProcessorSummary_Model}}",
        %end
        "Status": {
            %sepr = ""
            %if defined ("Server_ProcessorSummary_Status_State"):
                "State": "{{Server_ProcessorSummary_Status_State}}"
                %sepr = ","
            %end
            %if defined ("Server_ProcessorSummary_Status_HealthRollUp"):
                {{sepr}}"HealthRollUp": "{{Server_ProcessorSummary_Status_HealthRollUp}}"
                %sepr = ","
            %end
            %if defined ("Server_ProcessorSummary_Status_Health"):
                {{sepr}}"Health": "{{Server_ProcessorSummary_Status_Health}}"
            %end
        }
    },
    "MemorySummary": {
        %if defined ("Server_MemorySummary_TotalSystemMemoryGib"):
            "TotalSystemMemoryGib": {{Server_MemorySummary_TotalSystemMemoryGib}},
        %end
        "Status": {
            %sepr = ""
            %if defined ("Server_MemorySummary_Status_State"):
                "State": "{{Server_MemorySummary_Status_State}}"
                %sepr = ","
            %end
            %if defined ("Server_MemorySummary_Status_HealthRollUp"):
                {{sepr}}"HealthRollUp": "{{Server_MemorySummary_Status_HealthRollUp}}"
                %sepr = ","
            %end
            %if defined ("Server_MemorySummary_Status_Health"):
                {{sepr}}"Health": "{{Server_MemorySummary_Status_Health}}"
            %end
        }
    },
    "Status": {
        %sepr = ""
        %if defined ("Server_Status_State"):
            "State": "{{Server_Status_State}}"
            %sepr = ","
        %end
        %if defined ("Server_Status_HealthRollUp"):
            {{sepr}}"HealthRollUp": "{{Server_Status_HealthRollUp}}"
            %sepr = ","
        %end
        %if defined ("Server_Status_Health"):
            {{sepr}}"Health": "{{Server_Status_Health}}"
        %end
    },
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.ComputerSystem",
            %if defined ("PhysicalPresence"):
                "TPMPhysicalPresence": {{PhysicalPresence}},
            %end
            %if defined ("Default_Power_State"):
                "DefaultPowerState": "{{Default_Power_State}}",
            %end
            %if defined ("Server_CpldVersion"):
                "CPLDVersion":  "{{Server_CpldVersion}}",
            %end
            "BiosConfig": {
                "@odata.id": "/redfish/v1/System/{{ID}}/BiosConfig"
            },
            "BiosCode": {
                "@odata.id": "/redfish/v1/System/{{ID}}/BiosCode"
            },
            "FPGA": {
                "@odata.id": "/redfish/v1/System/{{ID}}/FPGA"
            }
        }
    },
    "Links": {
        "Chassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/System/{{ID}}"
            }
        ],
        "ManagedBy": [
            {
                "@odata.id": "/redfish/v1/Managers/System/{{ID}}"
            }
        ]
    },
    "Actions": {
        "#ComputerSystem.Reset": {
            "target": "/redfish/v1/System/{{ID}}/Actions/ComputerSystem.Reset",
            "ResetType@Redfish.AllowableValues": [
                "On",
                "GracefulShutdown",                
                "GracefulRestart"
            ]
        },
        "Oem": {
            "Ocs.v1_0_0.#ComputerSystem.RemoteMediaMount": {
                "target": "/redfish/v1/System/{{ID}}/Actions/ComputerSystem.RemoteMediaMount"
            },
            "Ocs.v1_0_0.#ComputerSystem.RemoteMediaUnmount": {
                "target": "/redfish/v1/System/{{ID}}/Actions/ComputerSystem.RemoteMediaUnmount"
            }
        }
    }
}
