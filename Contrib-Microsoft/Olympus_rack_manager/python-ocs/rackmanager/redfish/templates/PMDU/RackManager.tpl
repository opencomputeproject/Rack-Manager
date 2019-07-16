<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Port_Presence", "false")
        setdefault ("Port_State", "")
        setdefault ("Boot_Strap", "")
    end
%>
{
    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/RMM/PowerControl/RackManager/$entity",
    "@odata.id": "/redfish/v1/Chassis/RMM/PowerControl/RackManager/{{ID}}",
    "Id": "PowerPort{{ID}}",
    "Name": "Power Port {{ID}}",
    "PowerPortType": "RackManager"
    %if defined ("Port_Presence"):
        ,"Presence": {{Port_Presence}}
    %end
    %if defined ("Port_State"):
        ,"PowerState": "{{Port_State}}"
    %end
    %if defined ("Boot_Strap"):
        ,"BootStrapping": "{{Boot_Strap}}"
    %end
}