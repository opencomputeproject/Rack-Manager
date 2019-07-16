<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("I2C_Version", "")
        setdefault ("Temperature_in_Celsius", "0")
        setdefault ("Bypass_Mode", "")
        setdefault ("User_Logic_Network","")
        setdefault ("PCIe_HIP_0_Up", "")
        setdefault ("_40G_Link_0_Up", "")
        setdefault ("_40G_Link_0_Tx_Activity", "false")
        setdefault ("_40G_Link_0_Rx_Activity", "false")
        setdefault ("PCIe_HIP_1_Up", "")
        setdefault ("_40G_Link_1_Up", "")
        setdefault ("_40G_Link_1 Tx_Activity", "false")
        setdefault ("_40G_Link_1_Rx_Activity", "false")
        setdefault ("Product_Manufacturer", "")
        setdefault ("Product_Name", "")
        setdefault ("Product_Model_Number", "")
        setdefault ("Product_Version", "")
        setdefault ("Product_Serial_Number", "")
        setdefault ("Product_FRU_File_ID", "")
        setdefault ("Product_Custom_Field_1", "")
        setdefault ("Product_Custom_Field_2", "")
    end
%>
{
    "@odata.type": "#Ocs.v1_0_0.FPGA",
    "@odata.context": "/redfish/v1/$metadata#Systems/Members/System/{{ID}}/FPGA/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/FPGA",
    "Id": "FPGA{{ID}}",
    "Name": "40G FPGA {{ID}}",
    %if defined ("I2C_Version"):
        "FirmwareVersion": "{{I2C_Version}}",
    %end
    %if defined ("Temperature_in_Celsius"):
        "ReadingCelsius": {{Temperature_in_Celsius}},
    %end
    %if defined ("Bypass_Mode"):
        "BypassMode": "{{Bypass_Mode}}",
    %end
    %if defined ("User_Logic_Network"):
        "UserLogic": "{{User_Logic_Network}}",
    %end
    %if defined ("Product_Manufacturer"):
        "ProductManufacturer": "{{Product_Manufacturer}}",
    %end
    %if defined ("Product_Name"):
        "ProductName": "{{Product_Name}}",
    %end
    %if defined ("Product_Model_Number"):
        "ModelNumber": "{{Product_Model_Number}}",
    %end
    %if defined ("Product_Version"):
        "Version": "{{Product_Version}}",
    %end
    %if defined ("Product_Serial_Number"):
        "SerialNumber": "{{Product_Serial_Number}}",
    %end
    %if defined ("Product_FRU_File_ID"):
        "FRUFileID": "{{Product_FRU_File_ID}}",
    %end
    %if defined ("Product_Custom_Field_1"):
        "Manufacturer": "{{Product_Custom_Field_1}}",
    %end
    %if defined ("Product_Custom_Field_2"):
        "UUID": "{{Product_Custom_Field_2}}",
    %end
    "NICPort": {
        %sepr = ""
        %if defined ("PCIe_HIP_0_Up"):
            "PcieHIP": "{{PCIe_HIP_0_Up}}"
            %sepr = ","
        %end
        %if defined ("_40G_Link_0_Up"):
            {{sepr}}"LinkState": "{{_40G_Link_0_Up}}"
            %sepr = ","
        %end
        %if defined ("_40G_Link_0_Tx_Activity"):
            {{sepr}}"RxActivity": {{_40G_Link_0_Tx_Activity}}
            %sepr = ","
        %end
        %if defined ("_40G_Link_0_Rx_Activity"):
            {{sepr}}"TxActivity": {{_40G_Link_0_Rx_Activity}}
        %end
    },
    "TORPort": {
        %sepr = ""
        %if defined ("PCIe_HIP_1_Up"):
            "PcieHIP": "{{PCIe_HIP_1_Up}}"
            %sepr = ","
        %end
        %if defined ("_40G_Link_1_Up"):
            {{sepr}}"LinkState": "{{_40G_Link_1_Up}}"
            %sepr = ","
        %end
        %if defined ("_40G_Link_1_Tx_Activity"):
            {{sepr}}"RxActivity": {{_40G_Link_1_Tx_Activity}}
            %sepr = ","
        %end
        %if defined ("_40G_Link_1_Rx_Activity"):
            {{sepr}}"TxActivity": {{_40G_Link_1_Rx_Activity}}
        %end
    }
}