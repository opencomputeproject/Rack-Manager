{
    "@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
    "@odata.context": "/redfish/v1/$metadata#AccountService/Accounts/$entity",
    "@odata.id": "/redfish/v1/AccountService/ManagerAccounts",
    "Name": "Accounts Collection",
    %if defined ("accounts"):
        "Members@odata.count": {{num_accounts}},
        "Members": [
            %sepr = ""
            %for list in accounts.itervalues ():
                %for usr in list:
                    %if (usr):
                        {{sepr}}{
                            "@odata.id": "/redfish/v1/AccountService/ManagerAccount/{{usr}}"
                        }
                        %sepr = ","
                    %end
                %end
            %end
        ]
}
