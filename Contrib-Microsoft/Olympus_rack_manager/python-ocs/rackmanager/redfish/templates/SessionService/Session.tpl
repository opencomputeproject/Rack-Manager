<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("ClientIp", "")
        setdefault ("ClientPort", "")
    end
%>
{
	"@odata.type": "#Session.v1_0_2.Session",
	"@odata.context": "/redfish/v1/$metadata#SessionService/Sessions/Members/$entity",
	"@odata.id": "/redfish/v1/SessionService/Session/{{ID}}",
	"Id": "{{ID}}",
	"Name": "Manager Session",
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.Session"
            %if defined ("ClientIp"):
                ,"ClientIP": "{{ClientIp}}"
        	%end
        	%if defined ("ClientPort"):
                ,"ClientPort": {{ClientPort}}
        	%end
        }
    }    
}
