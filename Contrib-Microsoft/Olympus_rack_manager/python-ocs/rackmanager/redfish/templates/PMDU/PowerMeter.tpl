<%
    if defined ("TemplateDefault"):
        setdefault ("FirmwareVersion", "")
        setdefault ("IsDcThrottleEnabled", "false")
        setdefault ("IsDcThrottleActive", "false")
        setdefault ("AlertLimitInWatts", "0")
        setdefault ("IsAlertEnabled", "false")
        setdefault ("IsAlertActive", "false")
        setdefault ("MaxPowerInWatts", "0")
        setdefault ("PowerDrawnInWatts", "0")
        setdefault ("Feed1Phase1PowerInWatts", "0")
        setdefault ("Feed1Phase2PowerInWatts", "0")
        setdefault ("Feed1Phase3PowerInWatts", "0")
        setdefault ("Feed1PowerStatus", "")
        setdefault ("Feed2Phase1PowerInWatts", "0")
        setdefault ("Feed2Phase2PowerInWatts", "0")
        setdefault ("Feed2Phase3PowerInWatts", "0")
        setdefault ("Feed2PowerStatus", "")
    end
%>
{
    "@odata.type": "#OcsPowerMeter.v1_0_0.PowerMeter",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/PMDU/PowerMeter/$entity",
    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerMeter",
    "Id": "PowerMeter",
    "Name": "Rack Power Meter"
    % if defined ("FirmwareVersion"):
        ,"FirmwareVersion": "{{FirmwareVersion}}"
    % end
    % if defined ("IsDcThrottleEnabled"):
        ,"DatacenterThrottleEnabled": {{IsDcThrottleEnabled}}
    % end 
    % if defined ("IsDcThrottleActive"):
        ,"DatacenterThrottleActive": {{IsDcThrottleActive}}
    % end
    % if defined ("AlertLimitInWatts"):
        ,"AlertLimitWatts": {{AlertLimitInWatts}}
    % end
    % if defined ("IsAlertEnabled"):
        ,"AlertEnabled": {{IsAlertEnabled}}
    % end
    % if defined ("IsAlertActive"):
        ,"AlertActive": {{IsAlertActive}}
    % end
    % if defined ("MaxPowerInWatts"):
        ,"MaxPowerWatts": {{MaxPowerInWatts}}
    % end
    % if defined ("PowerDrawnInWatts"):
        ,"PowerDrawnWatts": {{PowerDrawnInWatts}}
    % end
    ,"Feed1": {
        % sepr = ""
        % if defined ("Feed1Phase1PowerInWatts"):
            "Phase1PowerWatts": {{Feed1Phase1PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed1Phase2PowerInWatts"):
            {{sepr}}"Phase2PowerWatts": {{Feed1Phase2PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed1Phase3PowerInWatts"):
            {{sepr}}"Phase3PowerWatts": {{Feed1Phase3PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed1PowerStatus"):
            {{sepr}}"Faults": "{{Feed1PowerStatus}}"
        % end
    },
    "Feed2": {
        % sepr = ""
        % if defined ("Feed2Phase1PowerInWatts"):
            "Phase1PowerWatts": {{Feed2Phase1PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed2Phase2PowerInWatts"):
            {{sepr}}"Phase2PowerWatts": {{Feed2Phase2PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed2Phase3PowerInWatts"):
            {{sepr}}"Phase3PowerWatts": {{Feed2Phase3PowerInWatts}}
            % sepr = ","
        % end
        % if defined ("Feed2PowerStatus"):
            {{sepr}}"Faults": "{{Feed2PowerStatus}}"
        % end
    },
    "Actions": {
       "#PowerMeter.ClearMaxPower": {
           "target": "/redfish/v1/Chassis/PMDU/PowerMeter/Actions/PowerMeter.ClearMaxPower"
       },
       "#PowerMeter.ClearFaults": {
           "target": "/redfish/v1/Chassis/PMDU/PowerMeter/Actions/PowerMeter.ClearFaults"
       }
    }
}
