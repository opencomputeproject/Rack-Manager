<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Relay", "")
    end
%>
{
    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/PMDU/PowerControl/Relay/$entity",
    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerControl/Relay/{{ID}}",
    "Id": "PowerRelay{{ID}}",
    "Name": "Power Relay {{ID}}",
    "PowerPortType": "Relay"
    % if defined ("Relay"):
        ,"PowerState": "{{Relay}}"
    % end
}
