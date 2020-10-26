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

#include <boost/container/flat_map.hpp>

namespace redfish
{

class UpdateService : public Node
{
  public:
    UpdateService(CrowApp &app) : Node(app, "/redfish/v1/UpdateService/")
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
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        res.jsonValue["@odata.type"] = "#UpdateService.v1_2_0.UpdateService";
        res.jsonValue["@odata.id"] = "/redfish/v1/UpdateService";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#UpdateService/$entity";
        res.jsonValue["Id"] = "UpdateService";
        res.jsonValue["Description"] = "Service for Software Update";
        res.jsonValue["Name"] = "Update Service";
        res.jsonValue["Status"]["Health"] = "OK";
        res.jsonValue["Status"]["HealthRollup"] = "OK";
        res.jsonValue["Status"]["State"] = "Enabled";
        // UpdateService cannot be disabled
        res.jsonValue["ServiceEnabled"] = true;

        nlohmann::json &actions = res.jsonValue["Actions"];
        actions["#UpdateService.SimpleUpdate"]["target"] =
            "/redfish/v1/UpdateService/Actions/SimpleUpdate";
        actions["@Redfish.ActionInfo"] =
            "/redfish/v1/UpdateService/SimpleUpdateActionIfo";
        res.end();
    }
};

class SoftwareInventoryCollection : public Node
{
  public:
    template <typename CrowApp>
    SoftwareInventoryCollection(CrowApp &app) :
        Node(app, "/redfish/v1/UpdateService/FirmwareInventory/")
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
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        std::shared_ptr<AsyncResp> asyncResp = std::make_shared<AsyncResp>(res);
        res.jsonValue["@odata.type"] =
            "#SoftwareInventoryCollection.SoftwareInventoryCollection";
        res.jsonValue["@odata.id"] =
            "/redfish/v1/UpdateService/FirmwareInventory";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/"
            "$metadata#SoftwareInventoryCollection.SoftwareInventoryCollection";
        res.jsonValue["Name"] = "Software Inventory Collection";
        res.end();
    }
};

class SoftwareInventory : public Node
{
  public:
    template <typename CrowApp>
    SoftwareInventory(CrowApp &app) :
        Node(app, "/redfish/v1/UpdateService/FirmwareInventory/<str>/",
             std::string())
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
    void doGet(crow::Response &res, const crow::Request &req,
               const std::vector<std::string> &params) override
    {
        std::shared_ptr<AsyncResp> asyncResp = std::make_shared<AsyncResp>(res);
        res.jsonValue["@odata.type"] =
            "#SoftwareInventory.v1_1_0.SoftwareInventory";
        res.jsonValue["@odata.context"] =
            "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory";
        res.jsonValue["Name"] = "Software Inventory";
        res.jsonValue["Updateable"] = false;
        res.jsonValue["Status"]["Health"] = "OK";
        res.jsonValue["Status"]["HealthRollup"] = "OK";
        res.jsonValue["Status"]["State"] = "Enabled";

        if (params.size() != 1)
        {
            messages::internalError(res);
            res.end();
            return;
        }

        std::shared_ptr<std::string> swId =
            std::make_shared<std::string>(params[0]);

        res.jsonValue["@odata.id"] =
            "/redfish/v1/UpdateService/FirmwareInventory/" + *swId;

        res.end();
    }
};

} // namespace redfish
