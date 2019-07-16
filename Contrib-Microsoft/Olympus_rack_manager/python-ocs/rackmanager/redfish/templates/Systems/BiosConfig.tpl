<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Current_BIOS_Configuration", "")
        setdefault ("Chosen_BIOS_Configuration", "")
        AvailableConfigs = [{"Config_Name" : "", "Config_Value" : ""}]
    else:
        setdefault ("AvailableConfigs", [])
    end
%>
{
    "@odata.type": "#Ocs.v1_0_0.BiosConfig",
    "@odata.context": "/redfish/v1/$metadata#Systems/Members/System/{{ID}}/BiosConfig/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/BiosConfig",
    "Id": "Bios{{ID}}",
    "Name": "BIOS {{ID}} Configuration",
    %if defined ("Current_BIOS_Configuration"):
        "CurrentConfiguration": "{{Current_BIOS_Configuration}}",
    %end
    %if defined ("Chosen_BIOS_Configuration"):
        "ChosenConfiguration": "{{Chosen_BIOS_Configuration}}",
    %end
    "AvailableConfigurations": [
        %sepr = ""
        %for entry in AvailableConfigs:
            %int_sepr = ""
            {{sepr}}{
                %if "Config_Name" in entry:
                    "Name": "{{entry["Config_Name"]}}"
                    %int_sepr = ","
                %end
                %if "Config_Value" in entry:
                    {{int_sepr}}"Value": "{{entry["Config_Value"]}}"
                %end
            }
            %sepr = ","
        %end
    ]
}
