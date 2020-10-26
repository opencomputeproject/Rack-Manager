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

#include <boost/container/flat_map.hpp>
#include <node.hpp>
#include <utils/json_utils.hpp>

namespace redfish
{

using InterfacesProperties = boost::container::flat_map<
    std::string,
    boost::container::flat_map<std::string, dbus::utility::DbusVariantType>>;

void getResourceList(std::shared_ptr<AsyncResp> aResp,
                     const std::string &subclass,
                     const std::vector<const char *> &collectionName)
{
    BMCWEB_LOG_DEBUG << "Get available system cpu/mem resources.";
    crow::connections::systemBus->async_method_call(
        [subclass, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const boost::container::flat_map<
                std::string, boost::container::flat_map<
                                 std::string, std::vector<std::string>>>
                &subtree) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);
                return;
            }
            nlohmann::json &members = aResp->res.jsonValue["Members"];
            members = nlohmann::json::array();

            for (const auto &object : subtree)
            {
                auto iter = object.first.rfind("/");
                if ((iter != std::string::npos) && (iter < object.first.size()))
                {
                    members.push_back(
                        {{"@odata.id", "/redfish/v1/Systems/system/" +
                                           subclass + "/" +
                                           object.first.substr(iter + 1)}});
                }
            }
            aResp->res.jsonValue["Members@odata.count"] = members.size();
        },
        "xyz.openbmc_project.ObjectMapper",
        "/xyz/openbmc_project/object_mapper",
        "xyz.openbmc_project.ObjectMapper", "GetSubTree",
        "/xyz/openbmc_project/inventory", 0, collectionName);
}

void getCpuDataByInterface(std::shared_ptr<AsyncResp> aResp,
                           const InterfacesProperties &cpuInterfacesProperties)
{
    BMCWEB_LOG_DEBUG << "Get CPU resources by interface.";

    const bool *present = nullptr;
    const bool *functional = nullptr;
    for (const auto &interface : cpuInterfacesProperties)
    {
        for (const auto &property : interface.second)
        {
            if (property.first == "ProcessorCoreCount")
            {
                const uint16_t *coresCount =
                    std::get_if<uint16_t>(&property.second);
                if (coresCount == nullptr)
                {
                    // Important property not in desired type
                    messages::internalError(aResp->res);
                    return;
                }
                if (*coresCount == 0)
                {
                    // Slot is not populated, set status end return
                    aResp->res.jsonValue["Status"]["State"] = "Absent";
                    aResp->res.jsonValue["Status"]["Health"] = "OK";
                    // HTTP Code will be set up automatically, just return
                    return;
                }

                aResp->res.jsonValue["TotalCores"] = *coresCount;
            }
            else if (property.first == "ProcessorType")
            {
                aResp->res.jsonValue["Name"] = property.second;
            }
            else if (property.first == "Manufacturer")
            {
                const std::string *value =
                    std::get_if<std::string>(&property.second);
                if (value != nullptr)
                {
                    aResp->res.jsonValue["Manufacturer"] = property.second;
                    // Otherwise would be unexpected.
                    if (value->find("Intel") != std::string::npos)
                    {
                        aResp->res.jsonValue["ProcessorArchitecture"] = "x86";
                        aResp->res.jsonValue["InstructionSet"] = "x86-64";
                    }
                    else if (value->find("IBM") != std::string::npos)
                    {
                        aResp->res.jsonValue["ProcessorArchitecture"] = "Power";
                        aResp->res.jsonValue["InstructionSet"] = "PowerISA";
                    }
                }
            }
            else if (property.first == "ProcessorMaxSpeed")
            {
                aResp->res.jsonValue["MaxSpeedMHz"] = property.second;
            }
            else if (property.first == "ProcessorThreadCount")
            {
                aResp->res.jsonValue["TotalThreads"] = property.second;
            }
            else if (property.first == "Model")
            {
                const std::string *value =
                    std::get_if<std::string>(&property.second);
                if (value != nullptr)
                {
                    aResp->res.jsonValue["Model"] = *value;
                }
            }
            else if (property.first == "Present")
            {
                present = std::get_if<bool>(&property.second);
            }
            else if (property.first == "Functional")
            {
                functional = std::get_if<bool>(&property.second);
            }
        }
    }

    if ((present == nullptr) || (functional == nullptr))
    {
        // Important property not in desired type
        messages::internalError(aResp->res);
        return;
    }

    if (*present == false)
    {
        aResp->res.jsonValue["Status"]["State"] = "Absent";
        aResp->res.jsonValue["Status"]["Health"] = "OK";
    }
    else
    {
        aResp->res.jsonValue["Status"]["State"] = "Enabled";
        if (*functional == true)
        {
            aResp->res.jsonValue["Status"]["Health"] = "OK";
        }
        else
        {
            aResp->res.jsonValue["Status"]["Health"] = "Critical";
        }
    }

    return;
}

void getCpuDataByService(std::shared_ptr<AsyncResp> aResp,
                         const std::string &cpuId, const std::string &service,
                         const std::string &objPath)
{
    BMCWEB_LOG_DEBUG << "Get available system cpu resources by service.";

    crow::connections::systemBus->async_method_call(
        [cpuId, service, objPath, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const dbus::utility::ManagedObjectType &dbusData) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);
                return;
            }
            aResp->res.jsonValue["Id"] = cpuId;
            aResp->res.jsonValue["Name"] = "Processor";
            aResp->res.jsonValue["ProcessorType"] = "CPU";

            std::string corePath = objPath + "/core";
            size_t totalCores = 0;
            for (const auto &object : dbusData)
            {
                if (object.first.str == objPath)
                {
                    getCpuDataByInterface(aResp, object.second);
                }
                else if (boost::starts_with(object.first.str, corePath))
                {
                    for (const auto &interface : object.second)
                    {
                        if (interface.first ==
                            "xyz.openbmc_project.Inventory.Item")
                        {
                            for (const auto &property : interface.second)
                            {
                                if (property.first == "Present")
                                {
                                    const bool *present =
                                        std::get_if<bool>(&property.second);
                                    if (present != nullptr)
                                    {
                                        if (*present == true)
                                        {
                                            totalCores++;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            // In getCpuDataByInterface(), state and health are set
            // based on the present and functional status. If core
            // count is zero, then it has a higher precedence.
            if (totalCores == 0)
            {
                // Slot is not populated, set status end return
                aResp->res.jsonValue["Status"]["State"] = "Absent";
                aResp->res.jsonValue["Status"]["Health"] = "OK";
            }
            aResp->res.jsonValue["TotalCores"] = totalCores;
            return;
        },
        service, "/xyz/openbmc_project/inventory",
        "org.freedesktop.DBus.ObjectManager", "GetManagedObjects");
}

void getAcceleratorDataByService(std::shared_ptr<AsyncResp> aResp,
                                 const std::string &acclrtrId,
                                 const std::string &service,
                                 const std::string &objPath)
{
    BMCWEB_LOG_DEBUG
        << "Get available system Accelerator resources by service.";
    crow::connections::systemBus->async_method_call(
        [acclrtrId, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const boost::container::flat_map<
                std::string, std::variant<std::string, uint32_t, uint16_t,
                                          bool>> &properties) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);
                return;
            }
            aResp->res.jsonValue["Id"] = acclrtrId;
            aResp->res.jsonValue["Name"] = "Processor";
            const bool *accPresent = nullptr;
            const bool *accFunctional = nullptr;
            std::string state = "";

            for (const auto &property : properties)
            {
                if (property.first == "Functional")
                {
                    accFunctional = std::get_if<bool>(&property.second);
                }
                else if (property.first == "Present")
                {
                    accPresent = std::get_if<bool>(&property.second);
                }
            }

            if (!accPresent || !accFunctional)
            {
                BMCWEB_LOG_DEBUG << "Required properties missing in DBUS "
                                    "response";
                messages::internalError(aResp->res);
                return;
            }

            if (*accPresent && *accFunctional)
            {
                state = "Enabled";
            }
            else if (*accPresent)
            {
                state = "UnavailableOffline";
            }
            else
            {
                state = "Absent";
            }
            aResp->res.jsonValue["Status"]["State"] = state;
            aResp->res.jsonValue["Status"]["Health"] = "OK";
            aResp->res.jsonValue["ProcessorType"] = "Accelerator";
        },
        service, objPath, "org.freedesktop.DBus.Properties", "GetAll", "");
}

void getCpuData(std::shared_ptr<AsyncResp> aResp, const std::string &cpuId,
                const std::vector<const char *> inventoryItems)
{
    BMCWEB_LOG_DEBUG << "Get available system cpu resources.";

    crow::connections::systemBus->async_method_call(
        [cpuId, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const boost::container::flat_map<
                std::string, boost::container::flat_map<
                                 std::string, std::vector<std::string>>>
                &subtree) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);
                return;
            }
            for (const auto &object : subtree)
            {
                if (boost::ends_with(object.first, cpuId))
                {
                    for (const auto &service : object.second)
                    {
                        for (const auto &inventory : service.second)
                            if (inventory ==
                                "xyz.openbmc_project.Inventory.Item.Cpu")
                            {
                                getCpuDataByService(aResp, cpuId, service.first,
                                                    object.first);
                            }
                            else if (inventory == "xyz.openbmc_project."
                                                  "Inventory.Item.Accelerator")
                            {
                                getAcceleratorDataByService(
                                    aResp, cpuId, service.first, object.first);
                            }
                        return;
                    }
                }
            }
            // Object not found
            messages::resourceNotFound(aResp->res, "Processor", cpuId);
            return;
        },
        "xyz.openbmc_project.ObjectMapper",
        "/xyz/openbmc_project/object_mapper",
        "xyz.openbmc_project.ObjectMapper", "GetSubTree",
        "/xyz/openbmc_project/inventory", 0, inventoryItems);
}

void getDimmDataByService(std::shared_ptr<AsyncResp> aResp,
                          const std::string &dimmId, const std::string &service,
                          const std::string &objPath)
{
    BMCWEB_LOG_DEBUG << "Get available system components.";
    crow::connections::systemBus->async_method_call(
        [dimmId, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const boost::container::flat_map<
                std::string, std::variant<std::string, uint32_t, uint16_t>>
                &properties) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);

                return;
            }
            aResp->res.jsonValue["Id"] = dimmId;
            aResp->res.jsonValue["Name"] = "DIMM Slot";

            const auto memorySizeProperty = properties.find("MemorySizeInKB");
            if (memorySizeProperty != properties.end())
            {
                const uint32_t *memorySize =
                    std::get_if<uint32_t>(&memorySizeProperty->second);
                if (memorySize == nullptr)
                {
                    // Important property not in desired type
                    messages::internalError(aResp->res);

                    return;
                }
                if (*memorySize == 0)
                {
                    // Slot is not populated, set status end return
                    aResp->res.jsonValue["Status"]["State"] = "Absent";
                    aResp->res.jsonValue["Status"]["Health"] = "OK";
                    // HTTP Code will be set up automatically, just return
                    return;
                }
                aResp->res.jsonValue["CapacityMiB"] = (*memorySize >> 10);
            }
            aResp->res.jsonValue["Status"]["State"] = "Enabled";
            aResp->res.jsonValue["Status"]["Health"] = "OK";

            for (const auto &property : properties)
            {
                if (property.first == "MemoryDataWidth")
                {
                    aResp->res.jsonValue["DataWidthBits"] = property.second;
                }
                else if (property.first == "PartNumber")
                {
                    aResp->res.jsonValue["PartNumber"] = property.second;
                }
                else if (property.first == "SerialNumber")
                {
                    aResp->res.jsonValue["SerialNumber"] = property.second;
                }
                else if (property.first == "Manufacturer")
                {
                    aResp->res.jsonValue["Manufacturer"] = property.second;
                }
                else if (property.first == "MemoryType")
                {
                    const auto *value =
                        std::get_if<std::string>(&property.second);
                    if (value != nullptr)
                    {
                        aResp->res.jsonValue["MemoryDeviceType"] = *value;
                        if (boost::starts_with(*value, "DDR"))
                        {
                            aResp->res.jsonValue["MemoryType"] = "DRAM";
                        }
                    }
                }
            }
        },
        service, objPath, "org.freedesktop.DBus.Properties", "GetAll", "");
}

void getDimmData(std::shared_ptr<AsyncResp> aResp, const std::string &dimmId)
{
    BMCWEB_LOG_DEBUG << "Get available system dimm resources.";
    crow::connections::systemBus->async_method_call(
        [dimmId, aResp{std::move(aResp)}](
            const boost::system::error_code ec,
            const boost::container::flat_map<
                std::string, boost::container::flat_map<
                                 std::string, std::vector<std::string>>>
                &subtree) {
            if (ec)
            {
                BMCWEB_LOG_DEBUG << "DBUS response error";
                messages::internalError(aResp->res);

                return;
            }
            for (const auto &object : subtree)
            {
                if (boost::ends_with(object.first, dimmId))
                {
                    for (const auto &service : object.second)
                    {
                        getDimmDataByService(aResp, dimmId, service.first,
                                             object.first);
                        return;
                    }
                }
            }
            // Object not found
            messages::resourceNotFound(aResp->res, "Memory", dimmId);
            return;
        },
        "xyz.openbmc_project.ObjectMapper",
        "/xyz/openbmc_project/object_mapper",
        "xyz.openbmc_project.ObjectMapper", "GetSubTree",
        "/xyz/openbmc_project/inventory", 0,
        std::array<const char *, 1>{"xyz.openbmc_project.Inventory.Item.Dimm"});
}

class ProcessorCollection : public Node
{
  public:
    /*
     * Default Constructor
     */
    ProcessorCollection(CrowApp &app) :
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    Node(app, "/redfish/v1/Systems/system/Processors/")
#else
    Node(app, "/redfish/v1/Systems/<str>/Processors", std::string())
#endif
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::put, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::post, {{"ConfigureComponents"}}}};
    }

  private:
    /**
     * Functions triggers appropriate requests on DBus
     */
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        res.jsonValue["@odata.type"] =
            "#ProcessorCollection.ProcessorCollection";
        res.jsonValue["Name"] = "Processor Collection";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#ProcessorCollection.ProcessorCollection";

        res.jsonValue["@odata.id"] = "/redfish/v1/Systems/system/Processors/";
        auto asyncResp = std::make_shared<AsyncResp>(res);

        getResourceList(asyncResp, "Processors",
                        {"xyz.openbmc_project.Inventory.Item.Cpu",
                         "xyz.openbmc_project.Inventory.Item.Accelerator"});
    }
#else
    void getProcessorList(const std::string &chassis_name,
                          std::shared_ptr<AsyncResp> asyncResp)
    {
        nlohmann::json &chassisArray = asyncResp->res.jsonValue["Members"];
        chassisArray = nlohmann::json::array();
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Processors/cpu0"}});
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Processors/cpu1"}});
        asyncResp->res.jsonValue["Members@odata.count"] = chassisArray.size();
    }

    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        const std::string &chassisId = params[0];

        res.jsonValue["@odata.type"] =
            "#ProcessorCollection.ProcessorCollection";
        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/" + chassisId + "/Processors";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#ProcessorCollection.ProcessorCollection";
        res.jsonValue["Name"] = "Processors Collection";
        auto asyncResp = std::make_shared<AsyncResp>(res);
        getProcessorList(chassisId, asyncResp);
    }
#endif // !BMCWEB_ENABLE_REDFISH_RMC
};

class Processor : public Node
{
  public:
    /*
     * Default Constructor
     */
    Processor(CrowApp &app) :
#ifndef BMCWEB_ENABLE_REDFISH_RMC
        Node(app, "/redfish/v1/Systems/system/Processors/<str>/", std::string())
#else
        Node(app, "/redfish/v1/Systems/<str>/Processors/<str>", std::string(), std::string())
#endif
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::put, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::post, {{"ConfigureComponents"}}}};
    }

  private:
    /**
     * Functions triggers appropriate requests on DBus
     */
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        // Check if there is required param, truly entering this shall be
        // impossible
        if (params.size() != 1)
        {
            messages::internalError(res);

            res.end();
            return;
        }
        const std::string &processorId = params[0];
        res.jsonValue["@odata.type"] = "#Processor.v1_3_1.Processor";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#Processor.Processor";
        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/system/Processors/" + processorId;

        auto asyncResp = std::make_shared<AsyncResp>(res);

        getCpuData(asyncResp, processorId,
                   {"xyz.openbmc_project.Inventory.Item.Cpu",
                    "xyz.openbmc_project.Inventory.Item.Accelerator"});
    }
#else
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        // Check if there is required param, truly entering this shall be
        // impossible
        if (params.size() != 2)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        const std::string &systemId = params[0];
        const std::string &processorId = params[1];

        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/" + systemId + "/Processors/" + processorId;
        res.jsonValue["@odata.type"] = "#Processor.v1_3_2.Processor";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#Processor.Processor";
        res.jsonValue["Manufacturer"] = "Intel";
        res.jsonValue["Model"] = "Intel(R) Xeon(R) Platinum 8176 CPU @ 2.10GHz";
        res.jsonValue["MaxSpeedMHz"] = 2100;
        res.jsonValue["TDPWatts"] = 165;
        res.jsonValue["TotalCores"] = 28;

        nlohmann::json &status = res.jsonValue["Status"];
        status["State"] = "Enabled";
        status["Health"] = "OK";
        status["HealthRollup"] = {};
        res.end();
    }
#endif // !BMCWEB_ENABLE_REDFISH_RMC
};

class MemoryCollection : public Node
{
  public:
    /*
     * Default Constructor
     */
    MemoryCollection(CrowApp &app) :
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    Node(app, "/redfish/v1/Systems/system/Memory/")
#else
    Node(app, "/redfish/v1/Systems/<str>/Memory", std::string())
#endif
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::put, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::post, {{"ConfigureComponents"}}}};
    }

  private:
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    /**
     * Functions triggers appropriate requests on DBus
     */
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        res.jsonValue["@odata.type"] = "#MemoryCollection.MemoryCollection";
        res.jsonValue["Name"] = "Memory Module Collection";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#MemoryCollection.MemoryCollection";
        res.jsonValue["@odata.id"] = "/redfish/v1/Systems/system/Memory/";
        auto asyncResp = std::make_shared<AsyncResp>(res);

        getResourceList(asyncResp, "Memory",
                        {"xyz.openbmc_project.Inventory.Item.Dimm"});
    }
#else
    void getMemoryList(const std::string &chassis_name,
                       std::shared_ptr<AsyncResp> asyncResp)
    {
        nlohmann::json &chassisArray = asyncResp->res.jsonValue["Members"];
        chassisArray = nlohmann::json::array();
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Memory/mem0"}});
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Memory/mem1"}});
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Memory/mem2"}});
        chassisArray.push_back(
            {{"@odata.id",
              "/redfish/v1/Systems/" + chassis_name + "/Memory/mem3"}});
        asyncResp->res.jsonValue["Members@odata.count"] = chassisArray.size();
    }

    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        const std::string &chassisId = params[0];

        res.jsonValue["@odata.type"] = "#MemoryCollection.MemoryCollection";
        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/" + chassisId + "/Memory";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#MemoryCollection.MemoryCollection";
        res.jsonValue["Name"] = "Memory Collection";
        auto asyncResp = std::make_shared<AsyncResp>(res);
        getMemoryList(chassisId, asyncResp);
    }
#endif // !BMCWEB_ENABLE_REDFISH_RMC
};

class Memory : public Node
{
  public:
    /*
     * Default Constructor
     */
    Memory(CrowApp &app) :
#ifndef BMCWEB_ENABLE_REDFISH_RMC
        Node(app, "/redfish/v1/Systems/system/Memory/<str>/", std::string())
#else
        Node(app, "/redfish/v1/Systems/<str>/Memory/<str>", std::string(), std::string())
#endif
    {
        entityPrivileges = {
            {boost::beast::http::verb::get, {{"Login"}}},
            {boost::beast::http::verb::head, {{"Login"}}},
            {boost::beast::http::verb::patch, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::put, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::delete_, {{"ConfigureComponents"}}},
            {boost::beast::http::verb::post, {{"ConfigureComponents"}}}};
    }

  private:
    /**
     * Functions triggers appropriate requests on DBus
     */
#ifndef BMCWEB_ENABLE_REDFISH_RMC
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        // Check if there is required param, truly entering this shall be
        // impossible
        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        const std::string &dimmId = params[0];

        res.jsonValue["@odata.type"] = "#Memory.v1_6_0.Memory";
        res.jsonValue["@odata.context"] = "/redfish/v1/$metadata#Memory.Memory";
        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/system/Memory/" + dimmId;
        auto asyncResp = std::make_shared<AsyncResp>(res);

        getDimmData(asyncResp, dimmId);
    }
#else
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        // Check if there is required param, truly entering this shall be
        // impossible
        if (params.size() != 2)
        {
            messages::internalError(res);
            res.end();
            return;
        }
        // Check if there is required param, truly entering this shall be

        const std::string &systemId = params[0];
        const std::string &memId = params[1];

        res.jsonValue["@odata.id"] =
            "/redfish/v1/Systems/" + systemId + "/Memory/" + memId;
        res.jsonValue["@odata.type"] = "#Memory.v1_0_0.Memory";
        res.jsonValue["@odata.context"] = "/redfish/v1/$metadata#Memory.Memory";
        res.jsonValue["CapacityMiB"] = 16 * 1024;
        res.jsonValue["Meanufacturer"] = "Samsung";
        res.jsonValue["Manufacturer"] = "Samsung";
        nlohmann::json &allowedSpeedsArray = res.jsonValue["AllowedSpeedsMHz"];
        allowedSpeedsArray = nlohmann::json::array();
        allowedSpeedsArray.push_back({1024,20});
        if (memId == "mem0")
        {
            res.jsonValue["SerialNumber"] = "390FB680";
            res.jsonValue["ModuleManufacturerID"] = "390FB680ABF0";
        }     
        else if (memId == "mem1")
        {
            res.jsonValue["SerialNumber"] = "393BE2A3";
            res.jsonValue["ModuleManufacturerID"] = "390FB680ABF1";
        }
            
        else if (memId == "mem2")
        {
            res.jsonValue["SerialNumber"] = "390FCBBD";
            res.jsonValue["ModuleManufacturerID"] = "390FB680ABF2";
        }  
        else if (memId == "mem3")
        {
            res.jsonValue["SerialNumber"] = "39359D7F";
            res.jsonValue["ModuleManufacturerID"] = "390FB680ABF3";
        }  
        else
        {
            res.jsonValue["SerialNumber"] = "39359D93";
            res.jsonValue["ModuleManufacturerID"] = "390FB680ABF4";
        }
            
        
        nlohmann::json &status = res.jsonValue["Status"];
        status["State"] = "Enabled";
        status["Health"] = "OK";
        status["HealthRollup"] = {};

        //res.jsonValue["AllowedSpeedsMHz"] = 2133;
        res.end();
    }
#endif // !BMCWEB_ENABLE_REDFISH_RMC
};

} // namespace redfish
