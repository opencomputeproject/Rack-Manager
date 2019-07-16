{
    "@odata.type": "#SessionCollection.SessionCollection",
    "@odata.context": "/redfish/v1/$metadata#SessionService/Sessions/$entity",
    "@odata.id": "/redfish/v1/SessionService/Sessions",
    "Name": "Active Sessions",
    %if defined ("sessions"):
        "Members": [
            %sepr = ""
            % for  i, (k, v) in enumerate(sessions.iteritems()):
                % if isinstance(v, dict):
                    % for l, (ks, vs) in enumerate(v.iteritems()):
                        % if ks == "ID":
                            {{sepr}}{
                                "@odata.id": "/redfish/v1/SessionService/Session/{{vs}}"
                            }
                            %sepr = ","
                        %end
                    %end
                %end
            %end
        ]
    %end
}
