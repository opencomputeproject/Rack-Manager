<%
    if defined ("TemplateDefault"):
        setdefault ("Account", "")
        setdefault ("groupname", "")
    end
%>
{
   "@odata.type": "#ManagerAccount.v1_0_2.ManagerAccount",
   "@odata.context": "/redfish/v1/$metadata#AccountService/Accounts/Members/$entity",
   "@odata.id": "/redfish/v1/AccountService/ManagerAccount/{{Account}}",
   "Id": "{{Account}}",
   "Name": "User Account",
   "Enabled": true,
   "UserName": "{{Account}}",
   %if defined ("TemplateDefault"):
       "Password": "",
   %end
   %if defined ("groupname"):
       "RoleId": "{{groupname}}",
       "Links": { 
           "Role": {
               "@odata.id": "/redfish/v1/AccountService/Role/{{groupname}}"
           }
       }
   %end
}
