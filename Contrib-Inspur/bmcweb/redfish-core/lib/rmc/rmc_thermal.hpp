/*
// Copyright (c) 2018 Intel Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
*/
#pragma once

#include "node.hpp"

namespace redfish
{
class Thermal : public Node
{
  public:
    Thermal(CrowApp& app) :
        Node((app), "/redfish/v1/Chassis/<str>/Thermal/", std::string())
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureManager"}}},
            {boost::beast::http::verb::put, {{"ConfigureManager"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureManager"}}},
            {boost::beast::http::verb::post, {{"ConfigureManager"}}}};
    }

  private:
    void getTemperatures(const std::string& chassis_name,
                         std::shared_ptr<AsyncResp> asyncResp, unsigned int id,
                         const std::string sensor_name, int sensor_number,
                         int value)
    {
        nlohmann::json& item = asyncResp->res.jsonValue["Temperatures"][id];
        item["@odata.id"] = "/redfish/v1/Chassis/" + chassis_name +
                            "/Thermal#/Temperatures/" + std::to_string(id);
        item["MemberId"] = id;
        item["Name"] = sensor_name;
        item["SensorNumber"] = sensor_number;
        item["Status"]["State"] = "Enabled";
        item["Status"]["Health"] = "OK";
        item["ReadingCelsius"] = value;
        item["UpperThresholdNonCritical"] = {};
        item["UpperThresholdCritical"] = {};
        item["UpperThresholdFatal"] = {};
        item["LowerThresholdNonCritical"] = {};
        item["LowerThresholdCritical"] = {};
        item["LowerThresholdFatal"] = {};
        item["MinReadingRangeTemp"] = {};
        item["MaxReadingRangeTemp"] = {};
        item["MinReadingRange"] = {};
        item["MaxReadingRange"] = {};
        item["PhysicalContext"] = "Intake";
        item["RelatedItem"][0] = {{"@odata.id", "/redfish/v1/Chassis/node1"}};
    }

    void getFans(const std::string& chassis_name,
                 std::shared_ptr<AsyncResp> asyncResp, unsigned int id,
                 const std::string sensor_name, int sensor_number, int value)
    {
        nlohmann::json& item = asyncResp->res.jsonValue["Fans"][id];
        item["@odata.id"] = "/redfish/v1/Chassis/" + chassis_name +
                            "/Thermal#/Fans/" + std::to_string(id);
        item["MemberId"] = id;
        item["Name"] = sensor_name;
        item["SensorNumber"] = sensor_number;
        item["Status"]["State"] = "Enabled";
        item["Status"]["Health"] = "OK";
        item["Reading"] = value;
        item["ReadingUnits"] = "RPM";
        item["UpperThresholdNonCritical"] = {};
        item["UpperThresholdCritical"] = {};
        item["UpperThresholdFatal"] = {};
        item["LowerThresholdNonCritical"] = {};
        item["LowerThresholdCritical"] = {};
        item["LowerThresholdFatal"] = {};
        item["MinReadingRange"] = {};
        item["MaxReadingRange"] = {};
        item["MinReadingRangeTemp"] = {};
        item["MaxReadingRangeTemp"] = {};
        item["RelatedItem"][0] = {{"@odata.id", "/redfish/v1/Chassis/node1"}};
    }

    void getThermalInfo(const std::string& chassisName,
                        std::shared_ptr<AsyncResp> asyncResp)
    {
        getFans(chassisName, asyncResp, 0, "BaseBoard System Fan 0", 1, 3505);
        getFans(chassisName, asyncResp, 1, "BaseBoard System Fan 1", 2, 3682);
        getFans(chassisName, asyncResp, 2, "BaseBoard System Fan 2", 3, 3728);
        getFans(chassisName, asyncResp, 3, "BaseBoard System Fan 3", 4, 3342);
        getTemperatures(chassisName, asyncResp, 0, "Inlet Temp 0", 5, 27);
        getTemperatures(chassisName, asyncResp, 1, "Inlet Temp 1", 6, 26);
        getTemperatures(chassisName, asyncResp, 2, "Outlet Temp 2", 7, 32);
        getTemperatures(chassisName, asyncResp, 3, "Outlet Temp 3", 8, 31);
    }
    void doGet(crow::Response& res, const crow::Request& req,
               const std::vector<std::string>& params) override
    {
        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        const std::string& chassisName = params[0];
        res.jsonValue["@odata.type"] = "#Thermal.v1_4_0.Thermal";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#Thermal.Thermal";
        res.jsonValue["Id"] = "Thermal";
        res.jsonValue["Name"] = "Thermal";

        res.jsonValue["@odata.id"] =
            "/redfish/v1/Chassis/" + chassisName + "/Thermal";

        auto asyncResp = std::make_shared<AsyncResp>(res);
        getThermalInfo(chassisName, asyncResp);
    }
};

} // namespace redfish
