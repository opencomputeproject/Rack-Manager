/*
// Copyright (c) 2018 Intel Corporation
// Copyright (c) 2018 Ampere Computing LLC
/
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
#include "sensors.hpp"
#include "logging.h"
#include <libevdev-1.0/libevdev/libevdev.h>

namespace redfish
{

class Power : public Node
{
  public:
    Power(CrowApp& app) :
        Node((app), "/redfish/v1/Chassis/<str>/Power/", std::string())
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::put, {{"ConfigureManager"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureManager"}}},
            {boost::beast::http::verb::post, {{"ConfigureManager"}}}};
    }

  private:
    std::vector<const char*> typeList = {"/xyz/openbmc_project/sensors/voltage",
                                         "/xyz/openbmc_project/sensors/power"};
    void setPowerCapOverride(
        std::shared_ptr<SensorsAsyncResp> asyncResp,
        std::vector<nlohmann::json>& powerControlCollections)
    {
        auto getChassisPath =
            [asyncResp, powerControlCollections](
                const std::optional<std::string>& chassisPath) mutable {
                if (!chassisPath)
                {
                    BMCWEB_LOG_ERROR << "Don't find valid chassis path ";
                    messages::resourceNotFound(asyncResp->res, "Chassis",
                                               asyncResp->chassisId);
                    return;
                }

                if (powerControlCollections.size() != 1)
                {
                    BMCWEB_LOG_ERROR
                        << "Don't support multiple hosts at present ";
                    messages::resourceNotFound(asyncResp->res, "Power",
                                               "PowerControl");
                    return;
                }

                auto& item = powerControlCollections[0];

                std::optional<nlohmann::json> powerLimit;
                if (!json_util::readJson(item, asyncResp->res, "PowerLimit",
                                         powerLimit))
                {
                    return;
                }
                if (!powerLimit)
                {
                    return;
                }
                std::optional<uint32_t> value;
                if (!json_util::readJson(*powerLimit, asyncResp->res,
                                         "LimitInWatts", value))
                {
                    return;
                }
                if (!value)
                {
                    return;
                }
                auto valueHandler = [value, asyncResp](
                                        const boost::system::error_code ec,
                                        const SensorVariant& powerCapEnable) {
                    if (ec)
                    {
                        messages::internalError(asyncResp->res);
                        BMCWEB_LOG_ERROR
                            << "powerCapEnable Get handler: Dbus error " << ec;
                        return;
                    }
                    // Check PowerCapEnable
                    const bool* b =
                        sdbusplus::message::variant_ns::get_if<bool>(
                            &powerCapEnable);
                    if (b == nullptr)
                    {
                        messages::internalError(asyncResp->res);
                        BMCWEB_LOG_ERROR
                            << "Fail to get PowerCapEnable status ";
                        return;
                    }
                    if (!(*b))
                    {
                        messages::actionNotSupported(
                            asyncResp->res,
                            "Setting LimitInWatts when PowerLimit "
                            "feature is disabled");
                        BMCWEB_LOG_ERROR << "PowerLimit feature is disabled ";
                        return;
                    }

                    crow::connections::systemBus->async_method_call(
                        [asyncResp](const boost::system::error_code ec) {
                            if (ec)
                            {
                                BMCWEB_LOG_DEBUG
                                    << "Power Limit Set: Dbus error: " << ec;
                                messages::internalError(asyncResp->res);
                                return;
                            }
                            asyncResp->res.result(
                                boost::beast::http::status::no_content);
                        },
                        "xyz.openbmc_project.Settings",
                        "/xyz/openbmc_project/control/host0/power_cap",
                        "org.freedesktop.DBus.Properties", "Set",
                        "xyz.openbmc_project.Control.Power.Cap", "PowerCap",
                        sdbusplus::message::variant<uint32_t>(*value));
                };
                crow::connections::systemBus->async_method_call(
                    std::move(valueHandler), "xyz.openbmc_project.Settings",
                    "/xyz/openbmc_project/control/host0/power_cap",
                    "org.freedesktop.DBus.Properties", "Get",
                    "xyz.openbmc_project.Control.Power.Cap", "PowerCapEnable");
            };
        getValidChassisPath(asyncResp, std::move(getChassisPath));
    }
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    void doGet(crow::Response& res, const crow::Request& req,
               const std::vector<std::string>& params) override
    {
        if (params.size() != 1)
        {
            res.result(boost::beast::http::status::internal_server_error);
            res.end();
            return;
        }
        const std::string& chassis_name = params[0];

        res.jsonValue["PowerControl"] = nlohmann::json::array();

        auto sensorAsyncResp = std::make_shared<SensorsAsyncResp>(
            res, chassis_name, typeList, "Power");

        getChassisData(sensorAsyncResp);

        // This callback verifies that the power limit is only provided for the
        // chassis that implements the Chassis inventory item. This prevents
        // things like power supplies providing the chassis power limit
        auto chassisHandler = [sensorAsyncResp](
                                  const boost::system::error_code e,
                                  const std::vector<std::string>&
                                      chassisPaths) {
            if (e)
            {
                BMCWEB_LOG_ERROR
                    << "Power Limit GetSubTreePaths handler Dbus error " << e;
                return;
            }

            bool found = false;
            for (const std::string& chassis : chassisPaths)
            {
                size_t len = std::string::npos;
                size_t lastPos = chassis.rfind("/");
                if (lastPos == std::string::npos)
                {
                    continue;
                }

                if (lastPos == chassis.size() - 1)
                {
                    size_t end = lastPos;
                    lastPos = chassis.rfind("/", lastPos - 1);
                    if (lastPos == std::string::npos)
                    {
                        continue;
                    }

                    len = end - (lastPos + 1);
                }

                std::string interfaceChassisName =
                    chassis.substr(lastPos + 1, len);
                if (!interfaceChassisName.compare(sensorAsyncResp->chassisId))
                {
                    found = true;
                    break;
                }
            }

            if (!found)
            {
                BMCWEB_LOG_DEBUG << "Power Limit not present for "
                                 << sensorAsyncResp->chassisId;
                return;
            }

            auto valueHandler =
                [sensorAsyncResp](
                    const boost::system::error_code ec,
                    const std::vector<std::pair<std::string, SensorVariant>>&
                        properties) {
                    if (ec)
                    {
                        messages::internalError(sensorAsyncResp->res);
                        BMCWEB_LOG_ERROR
                            << "Power Limit GetAll handler: Dbus error " << ec;
                        return;
                    }

                    nlohmann::json& tempArray =
                        sensorAsyncResp->res.jsonValue["PowerControl"];

                    // Put multiple "sensors" into a single PowerControl, 0, so
                    // only create the first one
                    if (tempArray.empty())
                    {
                        // Mandatory properties odata.id and MemberId
                        // A warning without a odata.type
                        tempArray.push_back(
                            {{"@odata.type", "#Power.v1_0_0.PowerControl"},
                             {"@odata.id", "/redfish/v1/Chassis/" +
                                               sensorAsyncResp->chassisId +
                                               "/Power#/PowerControl/0"},
                             {"Name", "Chassis Power Control"},
                             {"MemberId", "0"}});
                    }

                    nlohmann::json& sensorJson = tempArray.back();
                    bool enabled = false;
                    double powerCap = 0.0;
                    int64_t scale = 0;

                    for (const std::pair<std::string, SensorVariant>& property :
                         properties)
                    {
                        if (!property.first.compare("Scale"))
                        {
                            const int64_t* i =
                                sdbusplus::message::variant_ns::get_if<int64_t>(
                                    &property.second);

                            if (i)
                            {
                                scale = *i;
                            }
                        }
                        else if (!property.first.compare("PowerCap"))
                        {
                            const double* d =
                                sdbusplus::message::variant_ns::get_if<double>(
                                    &property.second);
                            const int64_t* i =
                                sdbusplus::message::variant_ns::get_if<int64_t>(
                                    &property.second);
                            const uint32_t* u =
                                sdbusplus::message::variant_ns::get_if<
                                    uint32_t>(&property.second);

                            if (d)
                            {
                                powerCap = *d;
                            }
                            else if (i)
                            {
                                powerCap = static_cast<double>(*i);
                            }
                            else if (u)
                            {
                                powerCap = *u;
                            }
                        }
                        else if (!property.first.compare("PowerCapEnable"))
                        {
                            const bool* b =
                                sdbusplus::message::variant_ns::get_if<bool>(
                                    &property.second);

                            if (b)
                            {
                                enabled = *b;
                            }
                        }
                    }

                    nlohmann::json& value =
                        sensorJson["PowerLimit"]["LimitInWatts"];

                    if (enabled)
                    {
                        // Redfish specification indicates PowerLimit should be
                        // null if the limit is not enabled.
                        value = powerCap * std::pow(10, scale);
                    }
                };

            crow::connections::systemBus->async_method_call(
                std::move(valueHandler), "xyz.openbmc_project.Settings",
                "/xyz/openbmc_project/control/host0/power_cap",
                "org.freedesktop.DBus.Properties", "GetAll",
                "xyz.openbmc_project.Control.Power.Cap");
        };

        crow::connections::systemBus->async_method_call(
            std::move(chassisHandler), "xyz.openbmc_project.ObjectMapper",
            "/xyz/openbmc_project/object_mapper",
            "xyz.openbmc_project.ObjectMapper", "GetSubTreePaths",
            "/xyz/openbmc_project/inventory", 0,
            std::array<const char*, 1>{
                "xyz.openbmc_project.Inventory.Item.Chassis"});
    }
#else
    void getPowerControlInfo(const std::string& chassis_name,
                             std::shared_ptr<AsyncResp> asyncResp)
    {
        nlohmann::json& item = asyncResp->res.jsonValue["PowerControl"][0];
        item["@odata.id"] =
            "/redfish/v1/Chassis/" + chassis_name + "/Power#/PowerControl/0";
        item["MemberId"] = 0;
        item["Name"] = "System Power Control";
        item["PowerConsumedWatts"] = 8000;
        item["PowerRequestedWatts"] = 8500;
        item["PowerAvailableWatts"] = 8500;
        item["PowerCapacityWatts"] = 10000;
        item["PowerAllocatedWatts"] = 8500;
        item["PowerMetrics"]["IntervalInMin"] = {};
        item["PowerMetrics"]["MinConsumedWatts"] = {};
        item["PowerMetrics"]["MaxConsumedWatts"] = {};
        item["PowerMetrics"]["AverageConsumedWatts"] = {};
        item["PowerLimit"]["LimitInWatts"] = {};
        item["PowerLimit"]["LimitException"] = {};
        item["PowerLimit"]["CorrectionInMs"] = {};
        item["RelatedItem"][0] = {{"@odata.id", "/redfish/v1/Chassis/node1"}};
        item["Status"]["State"] = "Enabled";
        item["Status"]["Health"] = "OK";
        item["Status"]["HealthRollup"] = "OK";
    }
    void getVoltagesInfo(const std::string& chassis_name,
                         std::shared_ptr<AsyncResp> asyncResp, unsigned int id,
                         const std::string& sensor_name, int sensor_number,
                         double value)
    {
        nlohmann::json& item = asyncResp->res.jsonValue["Voltages"][id];
        item["@odata.id"] = "/redfish/v1/Chassis/" + chassis_name +
                            "/Power#/Voltages/" + std::to_string(id);
        item["MemberId"] = id;
        item["Name"] = sensor_name;
        item["SensorNumber"] = sensor_number;
        item["Status"]["State"] = "Enabled";
        item["Status"]["Health"] = "OK";
        item["ReadingVolts"] = value;
        item["UpperThresholdNonCritical"] = {};
        item["UpperThresholdCritical"] = {};
        item["UpperThresholdFatal"] = {};
        item["LowerThresholdNonCritical"] = {};
        item["LowerThresholdCritical"] = {};
        item["LowerThresholdFatal"] = {};
        item["MinReadingRange"] = {};
        item["MaxReadingRange"] = {};
        item["PhysicalContext"] = "VoltageRegulator";
        item["RelatedItem"][0] = {{"@odata.id", "/redfish/v1/Chassis/node1"}};
    }

    // struct FreeEvDev
    // {
    //     void operator()(struct libevdev* device) const
    //     {
    //         libevdev_free(device);
    //     }
    // };

    // std::unique_ptr<libevdev, FreeEvDev> evdevOpen(int fd)
    // {
    //     libevdev* gpioDev = nullptr;

    //     auto rc = libevdev_new_from_fd(fd, &gpioDev);
    //     if (!rc)
    //     {
    //         std::cout<<"readGpio:gpioDev is not null"<<std::endl;
    //         return decltype(evdevOpen(0))(gpioDev);
    //     }
    //     //BMCWEB_LOG_ERROR << "Failed to get libevdev from file descriptor ";
    //     std::cout<<"readGpio:gpioDev is null"<<std::endl;
    //     return decltype(evdevOpen(0))(nullptr);
    // }

    std::string readGpio(const std::string& gpioPath, unsigned int keycode)
    {
        std::cout<<"readGpio:begin"<<std::endl;
        std::string strRet = "enable";
        try
        {
            int fd = ::open(gpioPath.c_str(), O_RDONLY);
            if (-1 == fd)
            {
                //BMCWEB_LOG_ERROR << "Failed to open file device";
                std::cout<<"readGpio:Failed to open file device"<<std::endl;
                return strRet;
            }
            std::cout<<"readGpio:open file device fd="<<fd<<std::endl;

            libevdev* gpioDev = nullptr;
            auto rc = libevdev_new_from_fd(fd, &gpioDev);
            if(nullptr == gpioDev)
            {
                std::cout<<"readGpio:gpioDev is null rc:"<<rc<<std::endl;
                return strRet;
            }

            int value = 0;
            auto fetch_rc = libevdev_fetch_event_value(gpioDev, EV_KEY,
                                                       keycode, &value);

            if (-1 != fd)
            {
                close(fd);
            }
            libevdev_free(gpioDev);
            if (0 == fetch_rc)
            {
                //BMCWEB_LOG_ERROR << "Device does not support event type KEYCODE";
                std::cout<<"readGpio:Device does not support event type KEYCODE="<<keycode<<std::endl;
                return strRet;
            }
            if (value > 0)
            {
                strRet = "disable";
            }
        }
        catch(...)
        {
            //BMCWEB_LOG_ERROR << "catch...";
            std::cout<<"readGpio:catch..."<<std::endl;
        }
        
        std::cout<<"readGpio:ret"<<strRet<<std::endl;
        return strRet;
    }

    void getPowerSuppliesInfo(const std::string& chassis_name,
                              std::shared_ptr<AsyncResp> asyncResp)
    {
        std::string szSerialNumber[] = {"JCA190900202", "JCA190900009", "JCA190900182",
        "JCA190900189", "JCA190900520", "JCA190900008"};
        size_t nszSerialNumber = sizeof(szSerialNumber) / sizeof(std::string);
        size_t nGpioPsu = 356;
        std::string gpioPath = "/dev/gpiochip0";
        for(size_t i = 0; i < nszSerialNumber; i++)
        { 
            nlohmann::json& item = asyncResp->res.jsonValue["PowerSupplies"][i];
            item["@odata.id"] = "/redfish/v1/Chassis/" + chassis_name +
                                "/Power#/PowerSupplies/" + std::to_string(i);
            //item["@odata.id"] += std::to_string(i);
            item["MemberId"] = i;
            item["Name"] = "Power Supply";
            std::string strState = readGpio(gpioPath, nGpioPsu+i);
            item["Status"]["State"] = strState;
            //item["Status"]["State"] = "enable";
            item["Status"]["Health"] = "OK";
            item["PowerSupplyType"] = "DC";
            item["LineInputVoltageType"] = "DCNeg48V";
            item["LineInputVoltage"] = 48;
            item["PowerCapacityWatts"] = 400;
            item["LastPowerOutputWatts"] = 192;
            item["Model"] = "DPST-3030BBA";
            item["Manufacturer"] = "Delta";
            item["FirmwareVersion"] = "2.75";
            item["SerialNumber"] = szSerialNumber[i];
            item["PartNumber"] = szSerialNumber[i] + "W0";
            item["SparePartNumber"] = {};
            item["InputRanges"] = nlohmann::json::array();
            item["IndicatorLED"] = "Off";

            item["RelatedItem"][0] = {
                {"@odata.id", "/redfish/v1/Chassis/node1"}};
        }

        
    }

    void getPowerInfo(const std::string& chassis_name,
                      std::shared_ptr<AsyncResp> asyncResp)
    {
        getPowerControlInfo(chassis_name, asyncResp);
        getPowerSuppliesInfo(chassis_name, asyncResp);
        getVoltagesInfo(chassis_name, asyncResp, 0, "VRM1", 11, 12);
        getVoltagesInfo(chassis_name, asyncResp, 1, "P5V", 12, 5);
        getVoltagesInfo(chassis_name, asyncResp, 2, "P3.3V", 13, 3.3);
        getVoltagesInfo(chassis_name, asyncResp, 3, "P1.5V", 14, 1.5);
        getVoltagesInfo(chassis_name, asyncResp, 4, "P3.3V_STBY", 15, 3.3);
    }

    void doGet(crow::Response& res, const crow::Request& req,
               const std::vector<std::string>& params) override
    {
        if (params.size() != 1)
        {
            res.result(boost::beast::http::status::internal_server_error);
            res.end();
            return;
        }
        const std::string& chassis_name = params[0];

        res.jsonValue["@odata.id"] =
            "/redfish/v1/Chassis/" + chassis_name + "/Power";
        res.jsonValue["@odata.type"] = "#Power.v1_2_1.Power";
        res.jsonValue["@odata.context"] = "/redfish/v1/$metadata#Power.Power";
        res.jsonValue["Id"] = "Power";
        res.jsonValue["Name"] = "Power";
        auto asyncResp = std::make_shared<AsyncResp>(res);

        getPowerInfo(chassis_name, asyncResp);
    }
#endif // !BMCWEB_ENABLE_REDFISH_RMC
    void doPatch(crow::Response& res, const crow::Request& req,
                 const std::vector<std::string>& params) override
    {
        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }

        const std::string& chassisName = params[0];
        auto asyncResp = std::make_shared<SensorsAsyncResp>(res, chassisName,
                                                            typeList, "Power");

        std::optional<std::vector<nlohmann::json>> voltageCollections;
        std::optional<std::vector<nlohmann::json>> powerCtlCollections;

        if (!json_util::readJson(req, asyncResp->res, "PowerControl",
                                 powerCtlCollections, "Voltages",
                                 voltageCollections))
        {
            return;
        }

        if (powerCtlCollections)
        {
            setPowerCapOverride(asyncResp, *powerCtlCollections);
        }
        if (voltageCollections)
        {
            std::unordered_map<std::string, std::vector<nlohmann::json>>
                allCollections;
            allCollections.emplace("Voltages", *std::move(voltageCollections));
            setSensorOverride(asyncResp, allCollections, chassisName, typeList);
        }
    }
};

} // namespace redfish
