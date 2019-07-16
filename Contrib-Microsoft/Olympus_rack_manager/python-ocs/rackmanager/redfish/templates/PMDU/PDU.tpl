<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Port_Presence", "false")
        setdefault ("Port_State", "")
    end
%>
{
    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/PMDU/PowerControl/PDU/$entity",
    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerControl/PDU/{{ID}}",
    "Id": "PowerPort{{ID}}",
    "Name": "Power Port {{ID}}",
    "PowerPortType": "PDU"
    % if defined ("Port_Presence"):
        ,"Presence": {{Port_Presence}}
    % end
    % if defined ("Port_State"):
        ,"PowerState": "{{Port_State}}"
    % end
}
