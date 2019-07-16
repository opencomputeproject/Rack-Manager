/*!
 * @copyright
 * Copyright (c) 2017-2019 Intel Corporation
 *
 * @copyright
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * @copyright
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * @copyright
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @file command/set_component_attributes.cpp
 * @brief Implementation of SetComponentAttributes command
 * */

#include "agent-framework/module/chassis_components.hpp"
#include "agent-framework/command/rmm_commands.hpp"
#include "agent-framework/command/registry.hpp"
#include "agent-framework/module/requests/validation/common.hpp"
#include "agent-framework/module/requests/validation/rmm.hpp"


using namespace agent_framework;
using namespace agent_framework::command;

namespace {

template <typename T, typename Mutex>
void invoke_reset_on_resource(generic::ObjReference<T, Mutex>& resource, const std::string& reset_type) {
    const auto& reset = model::enums::ResetType::from_string(reset_type);
    auto status = resource->get_status();
    switch (reset) {
        case model::enums::ResetType::None:
        default:
            break;
        case model::enums::ResetType::GracefulRestart:
        case model::enums::ResetType::ForceRestart:
        case model::enums::ResetType::PushPowerButton:
            status.set_state(model::enums::State::Starting);
            break;
        case model::enums::ResetType::On:
        case model::enums::ResetType::ForceOn:
            status.set_state(model::enums::State::Enabled);
            break;
        case model::enums::ResetType::ForceOff:
        case model::enums::ResetType::GracefulShutdown:
        case model::enums::ResetType::Nmi:
            status.set_state(model::enums::State::StandbyOffline);
            break;
    }
    resource->set_status(status);
}

void restore_defaults() {
    for (const auto& chassis_uuid : module::get_manager<model::Chassis>().get_keys()) {
        auto chassis = module::get_manager<model::Chassis>().get_entry_reference(chassis_uuid);
        chassis->set_asset_tag({});
        chassis->set_geo_tag({});
        chassis->set_location_id({});
    }
    for (const auto& psu_uuid : module::get_manager<model::Psu>().get_keys()) {
        auto psu = module::get_manager<model::Psu>().get_entry_reference(psu_uuid);
        psu->set_status(model::attribute::Status(
            agent_framework::model::enums::State::Enabled,
            agent_framework::model::enums::Health::OK)
        );
    }
    for (const auto& tzone_uuid : module::get_manager<model::ThermalZone>().get_keys()) {
        auto tzone = module::get_manager<model::ThermalZone>().get_entry_reference(tzone_uuid);
        tzone->set_desired_speed_pwm({});
    }
}

void process_chassis(const std::string& uuid, const model::attribute::Attributes& attributes,
                     std::string& message, SetComponentAttributes::Response& response) {

    model::requests::validation::CommonValidator::validate_set_chassis_attributes(attributes);
    const auto attribute_names = attributes.get_names();
    if (attribute_names.empty()) {
        message += " * Nothing has been changed (empty request).\n";
        return;
    }

    auto chassis = module::get_manager<model::Chassis>().get_entry_reference(uuid);
    for (const auto& name : attribute_names) {
        try {
            const auto& value = attributes.get_value(name);
            auto message_short = "Changed " + name + " attribute value to: " + value.dump();
            if (model::literals::Chassis::RESET == name) {
                ::invoke_reset_on_resource(chassis, value.get<std::string>());
            }
            else if (model::literals::Chassis::ASSET_TAG == name) {
                chassis->set_asset_tag(value);
            }
            else if (model::literals::Chassis::GEO_TAG == name) {
                if (chassis->get_type() != model::enums::ChassisType::Rack) {
                    THROW(exceptions::UnsupportedValue, "rmm-agent", "Geo-location tag can be set only on Racks.");
                }
                chassis->set_geo_tag(value.get<std::string>());
            }
            else if (model::literals::Chassis::LOCATION_ID == name) {
                chassis->set_location_id(value.get<std::string>());
            }
            message += " * " + message_short + ".\n";
        }
        catch (const exceptions::GamiException& ex) {
            response.add_status({name, ex.get_error_code(), ex.get_message()});
        }
    }
}

void process_psu(const std::string& uuid, const model::attribute::Attributes& attributes,
                 std::string& message, SetComponentAttributes::Response& response) {
    model::requests::validation::RmmValidator::validate_set_psu_attributes(attributes);
    const auto attribute_names = attributes.get_names();
    if (attribute_names.empty()) {
        message += " * Nothing has been changed (empty request).\n";
        return;
    }

    auto psu = module::get_manager<model::Psu>().get_entry_reference(uuid);
    for (const auto& name : attribute_names) {
        try {
            const auto& value = attributes.get_value(name);
            auto message_short = "Changed " + name + " attribute value to: " + value.dump();
            if (model::literals::Psu::REQUESTED_STATE == name) {
                const auto& requested_state = model::enums::State::from_string(value.get<std::string>());
                psu->set_status(model::attribute::Status{
                    requested_state,
                    psu->get_status().get_health()
                });
            }
            message += " * " + message_short + ".\n";
        }
        catch (const exceptions::GamiException& ex) {
            response.add_status({name, ex.get_error_code(), ex.get_message()});
        }
    }
}

void process_manager(const std::string& uuid, const model::attribute::Attributes& attributes,
                     std::string& message, SetComponentAttributes::Response& response) {

    model::requests::validation::CommonValidator::validate_set_manager_attributes(attributes);
    const auto attribute_names = attributes.get_names();
    if (attribute_names.empty()) {
        message += " * Nothing has been changed (empty request).\n";
        return;
    }

    auto manager = module::get_manager<model::Manager>().get_entry_reference(uuid);
    for (const auto& name : attribute_names) {
        try {
            const auto& value = attributes.get_value(name);
            auto message_short = "Changed " + name + " attribute value to: " + value.dump();
            if (model::literals::Manager::RESET == name) {
                ::invoke_reset_on_resource(manager, value.get<std::string>());
            }
            else if (model::literals::Manager::FACTORY_DEFAULTS == name) {
                const auto load_defaults = value.get<bool>();
                if (load_defaults) {
                    ::restore_defaults();
                }
            }
            message += " * " + message_short + ".\n";
        }
        catch (const exceptions::GamiException& ex) {
            response.add_status({name, ex.get_error_code(), ex.get_message()});
        }
    }
}

void process_thermal_zone(const std::string& uuid, const model::attribute::Attributes& attributes,
                          std::string& message, SetComponentAttributes::Response& response) {

    model::requests::validation::RmmValidator::validate_set_thermal_zone_attributes(attributes);
    const auto attribute_names = attributes.get_names();
    if (attribute_names.empty()) {
        message += " * Nothing has been changed (empty request).\n";
        return;
    }

    auto thermal_zone = module::get_manager<model::ThermalZone>().get_entry_reference(uuid);
    for (const auto& name : attribute_names) {
        try {
            const auto& value = attributes.get_value(name);
            auto message_short = "Changed " + name + " attribute value to: " + value.dump();
            if (model::literals::ThermalZone::DESIRED_SPEED_PWM == name) {
                thermal_zone->set_desired_speed_pwm(value.get<uint32_t>());
            }
            message += " * " + message_short + ".\n";
        }
        catch (const exceptions::GamiException& ex) {
            response.add_status({name, ex.get_error_code(), ex.get_message()});
        }
    }
}


void set_component_attributes(const SetComponentAttributes::Request& request,
                              SetComponentAttributes::Response& response) {
    const auto& uuid = request.get_component();
    const auto& attributes = request.get_attributes();
    std::string message{};

    if (module::get_manager<model::ThermalZone>().entry_exists(uuid)) {
        message = "For thermal zone with UUID: '" + uuid + "':\n";
        ::process_thermal_zone(uuid, attributes, message, response);
    }
    else if (module::get_manager<model::Manager>().entry_exists(uuid)) {
        message = "For manager with UUID: '" + uuid + "':\n";
        ::process_manager(uuid, attributes, message, response);
    }
    else if (module::get_manager<model::Chassis>().entry_exists(uuid)) {
        message = "For chassis with UUID: '" + uuid + "':\n";
        ::process_chassis(uuid, attributes, message, response);
    }
    else if (module::get_manager<model::Psu>().entry_exists(uuid)) {
        message = "For PSU with UUID: '" + uuid + "':\n";
        ::process_psu(uuid, attributes, message, response);
    }
    else {
        THROW(agent_framework::exceptions::InvalidUuid, "rmm-agent",
              "No component with UUID: '" + uuid + "'.");
    }

    log_info("rmm-agent", message);
    log_info("rmm-agent", "setComponentAttributes finished successfully.");
}

}

REGISTER_COMMAND(SetComponentAttributes, ::set_component_attributes);
