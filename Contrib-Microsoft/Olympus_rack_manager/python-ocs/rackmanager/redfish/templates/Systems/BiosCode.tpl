{
    "@odata.type": "#Ocs.v1_0_0.BiosCode",
    "@odata.context": "/redfish/v1/$metadata#Systems/Members/System/{{ID}}/BiosCode/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/BiosCode",
    "Id": "Post{{ID}}",
    "Name": "BIOS {{ID}} POST"
    %if defined ("Bios_Code"):
       ,"BiosCode": "{{Bios_Code}}"
    %end
}
