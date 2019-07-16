<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#OcsRackManager.v1_0_0.Tftp",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/Tftp/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/Tftp",
    "Id": "TFTP",
    "Name": "Tftp File Actions",
    "Files": [
        %sepr = ""
        % for  i, (k, v) in enumerate(TFTPFiles.iteritems()):
            % if isinstance(v, dict):
                % for l, (ks, vs) in enumerate(v.iteritems()):
                    % if ks == "Name":
                        {{sepr}}{
                            "Name": "{{vs}}"
                        }
                        %sepr = ","
                    %end
                %end
            %end
        %end
    ],
    "Actions": {
        "#Tftp.Delete": {
            "target": "/redfish/v1/Managers/{{config}}Manager/Tftp/Actions/Tftp.Delete"
        },
        "#Tftp.Get": {
            "target": "/redfish/v1/Managers/{{config}}Manager/Tftp/Actions/Tftp.Get"
        },
        "#Tftp.Put": {
            "target": "/redfish/v1/Managers/{{config}}Manager/Tftp/Actions/Tftp.Put",
            "Target@Redfish.AllowableValues": [
                "AuditLog",
                "DebugLog",
                "TelemetryLog",
                "RestLog",
                "FirmwareUpdateLog",
                "SystemLog",
                "KernelLog"
            ]
        }
    }
}
