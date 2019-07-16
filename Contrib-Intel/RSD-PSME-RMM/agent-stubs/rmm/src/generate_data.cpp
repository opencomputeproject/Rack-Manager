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
 * */

#include "generate_data.hpp"
#include "telemetry_service.hpp"
#include "agent-framework/module/common_components.hpp"
#include "agent-framework/module/chassis_components.hpp"
#include "agent-framework/module/network_components.hpp"
#include "agent-framework/module/compute_components.hpp"

#include <tuple>

using namespace agent_framework::model;
using namespace agent_framework::module;
using namespace agent::rmm;

namespace {

static const constexpr int ZONE_MANAGERS_COUNT = 2;
static const constexpr int DRAWERS_PER_RACK = 8;
using ZoneUuidTriple = std::tuple<std::string, std::string, std::string>;

Manager make_rack_manager() {
    Manager manager{};
    manager.set_manager_type(enums::ManagerInfoType::RackManager);
    manager.set_manager_model("RackScale RMC 1.0");
    manager.set_firmware_version("2.1.71.0");
    manager.set_status({
                           agent_framework::model::enums::State::Enabled,
                           agent_framework::model::enums::Health::OK
                       });

    manager.set_guid("a3f05144-9113-41c3-b46d-6efdf560660c");
    manager.set_date_time("2017-02-16T15:08:59-05:00") ;
    manager.set_date_time_local_offset("-05:00");

    manager.add_network_service(attribute::NetworkService(enums::NetworkServiceName::HTTP, 8090, true));
    manager.add_network_service(attribute::NetworkService(enums::NetworkServiceName::HTTPS, 8091, true));
    manager.add_network_service(attribute::NetworkService(enums::NetworkServiceName::SSH, 22, true));

    manager.set_allowed_reset_actions({
        agent_framework::model::enums::ResetType::ForceRestart,
        agent_framework::model::enums::ResetType::GracefulRestart
    });

    manager.add_collection(attribute::Collection{
            enums::CollectionName::Chassis,
            enums::CollectionType::Chassis
    });
    manager.add_collection(attribute::Collection{
            enums::CollectionName::NetworkInterfaces,
            enums::CollectionType::NetworkInterfaces
    });

    return manager;
}

Manager make_zone_manager(int index) {
    Manager manager{};
    manager.set_manager_type(enums::ManagerInfoType::ManagementController);
    manager.set_firmware_version("01.07");
    manager.set_guid("c062fe60-b747-11e6-9de9-cf2f9f6de2b" + std::to_string(index));
    manager.set_status({
                           agent_framework::model::enums::State::Enabled,
                           agent_framework::model::enums::Health::OK
                       });

    manager.add_collection(attribute::Collection{
            enums::CollectionName::Chassis,
            enums::CollectionType::Chassis
    });

    return manager;
}

NetworkInterface make_network_interface(const std::string& parent) {
    NetworkInterface interface{parent};
    interface.set_frame_size(1520);
    interface.set_oem(agent_framework::model::attribute::Oem{});
    interface.set_speed_mbps(1);
    interface.set_autosense(true);
    interface.set_mac_address("AA:BB:CC:DD:EE:FF");
    interface.set_factory_mac_address("AA:BB:CC:DD:EE:FF");
    interface.set_ipv6_default_gateway("fe80::1ec1:deff:febd:67e3");
    interface.set_max_ipv6_static_addresses(1);
    interface.set_default_vlan(1);
    interface.add_ipv4_address(attribute::Ipv4Address(
        "10.0.2.2",
        "255.255.255.0",
        enums::Ipv4AddressOrigin::DHCP,
        "10.0.2.1"
    ));
    interface.add_ipv6_address(attribute::Ipv6Address(
        "fe80::1ec1:deff:fe6f:1c37",
        16,
        enums::Ipv6AddressOrigin::DHCP,
        enums::Ipv6AddressState::Preferred
    ));
    interface.set_full_duplex(true);
    interface.set_status({
                             agent_framework::model::enums::State::Enabled,
                             agent_framework::model::enums::Health::OK
                         });
    interface.add_collection(attribute::Collection(
        enums::CollectionName::EthernetSwitchPortVlans,
        enums::CollectionType::EthernetSwitchPortVlans));

    return interface;
}

EthernetSwitchPortVlan make_port_vlan(const std::string& parent, bool tagged = true) {
    EthernetSwitchPortVlan vlan{parent};
    vlan.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK));
    vlan.set_vlan_id(1);
    vlan.set_vlan_name("VLAN Name");
    vlan.set_vlan_enable(false);
    vlan.set_tagged(tagged);
    vlan.set_oem(attribute::Oem());
    return vlan;
}

Chassis make_rack_chassis(const std::string& parent) {
    Chassis chassis{parent};
    chassis.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );

    chassis.set_asset_tag("asset tag");
    chassis.set_geo_tag("1.234234, 54.234234");
    chassis.set_sku("Rack SKU");
    chassis.set_indicator_led(enums::IndicatorLed::Unknown);
    chassis.set_type(enums::ChassisType::Rack);
    chassis.set_fru_info(attribute::FruInfo{
        "1234567890",
        "Intel",
        "RackScale_Rack",
        "0987654321"
    });
    chassis.set_location_id("10");
    chassis.set_location_offset(137);
    chassis.set_disaggregated_power_cooling_support(false);

    return chassis;
}

Chassis make_drawer(const std::string& parent,
                    const uint32_t offset,
                    const std::string& parent_location_id,
                    const std::string& thermal_zone_uuid,
                    const std::string& power_zone_uuid) {
    Chassis chassis{parent};
    chassis.set_status(attribute::Status{
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK
    });

    chassis.set_sku("Drawer SKU");
    chassis.set_indicator_led(enums::IndicatorLed::Unknown);
    chassis.set_type(enums::ChassisType::Drawer);
    chassis.set_fru_info(attribute::FruInfo{
        "1234567890",
        "Intel",
        "RackScale_RMM",
        "0987654321"
    });

    chassis.set_parent_id(parent_location_id);
    chassis.set_location_id("Drawer " + std::to_string(offset));
    chassis.set_location_offset(offset);

    chassis.set_thermal_zone(thermal_zone_uuid);
    chassis.set_power_zone(power_zone_uuid);

    chassis.set_allowed_reset_actions({
        agent_framework::model::enums::ResetType::ForceRestart,
        agent_framework::model::enums::ResetType::GracefulRestart
    });

    return chassis;
}

Chassis make_zone_chassis(const std::string& parent) {
    Chassis chassis{parent};
    chassis.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );

    chassis.set_sku("Zone SKU");
    chassis.set_indicator_led(enums::IndicatorLed::Unknown);
    chassis.set_type(enums::ChassisType::Zone);
    chassis.set_fru_info(attribute::FruInfo{
        "1234567890",
        "Intel",
        "RackScale_RMM",
        "0987654321"
    });

    chassis.add_collection(attribute::Collection{
            enums::CollectionName::PowerZones,
            enums::CollectionType::PowerZones
    });

    chassis.add_collection(attribute::Collection{
            enums::CollectionName::ThermalZones,
            enums::CollectionType::ThermalZones
    });

    return chassis;
}

PowerZone make_power_zone(const std::string& parent) {
    PowerZone power_zone{parent};

    power_zone.set_power_requested_watts(8500);
    power_zone.set_power_available_watts(8500);
    power_zone.set_power_capacity_watts(10000);
    power_zone.set_power_allocated_watts(8500);

    power_zone.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );

    power_zone.add_collection(attribute::Collection{
            enums::CollectionName::Psus,
            enums::CollectionType::PSUs
            });

    return power_zone;
}

ThermalZone make_thermal_zone(const std::string& parent) {
    ThermalZone thermal_zone{parent};

    thermal_zone.set_desired_speed_pwm(80);

    thermal_zone.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );

    thermal_zone.add_collection(attribute::Collection{
            enums::CollectionName::Fans,
            enums::CollectionType::Fans
    });

    return thermal_zone;
}

Psu make_psu(const std::string& parent) {
    Psu psu{parent};

    psu.set_power_capacity_watts(200);
    psu.set_last_power_output_watts(150);
    psu.set_power_supply_type(agent_framework::model::enums::PowerSupplyType::AC);
    psu.set_line_input_voltage_type(agent_framework::model::enums::LineInputVoltageType::AC240V);
    psu.set_line_input_voltage_volts(244);
    psu.set_indicator_led(enums::IndicatorLed::Off);

    psu.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );
    psu.set_fru_info(attribute::FruInfo{
        "1234567890",
        "Intel",
        "RackScale_RMM",
        "0987654321"
    });

    return psu;
}

Fan make_fan(const std::string& parent) {
    Fan fan{parent};

    fan.set_status(attribute::Status(
        agent_framework::model::enums::State::Enabled,
        agent_framework::model::enums::Health::OK)
    );
    fan.set_fru_info(attribute::FruInfo{
        "1234567890",
        "Intel",
        "RackScale_RMM",
        "0987654321"
    });

    return fan;
}

void create_psus(const std::string& parent) {
    for (int i = 0; i < 2; ++i) {
        auto psu = ::make_psu(parent);
        log_debug("rmm_agent", "Adding psu: " << psu.get_uuid());
        get_manager<Psu>().add_entry(psu);
    }
}

void create_fans(const std::string& parent) {
    for (int i = 0; i < 2; ++i) {
        auto fan = ::make_fan(parent);
        telemetry::build_metric(fan, telemetry::MetricType::FanReading, "/Reading", 2000);
        log_debug("rmm_agent", "Adding fan: " << fan.get_uuid());
        get_manager<Fan>().add_entry(fan);
    }
}

std::string create_power_zone(const std::string& parent) {
    auto pzone = ::make_power_zone(parent);
    create_psus(pzone.get_uuid());
    telemetry::build_metric(pzone, telemetry::MetricType::Voltage1, "/ReadingVolts", 137);
    telemetry::build_metric(pzone, telemetry::MetricType::Voltage2, "/ReadingVolts", 138);
    telemetry::build_metric(pzone, telemetry::MetricType::InputPower, "/Oem/Intel_RackScale/InputACPowerWatts", 9000);
    telemetry::build_metric(pzone, telemetry::MetricType::PowerConsumed, "/PowerConsumedWatts", 8000);
    log_debug("rmm_agent", "Adding Power Zone: " << pzone.get_uuid());
    get_manager<PowerZone>().add_entry(pzone);
    return pzone.get_uuid();
}

std::string create_thermal_zone(const std::string& parent) {
    auto tzone = ::make_thermal_zone(parent);
    create_fans(tzone.get_uuid());
    telemetry::build_metric(tzone, telemetry::MetricType::Temperature1, "/ReadingCelsius", 37);
    telemetry::build_metric(tzone, telemetry::MetricType::Temperature2, "/ReadingCelsius", 38);
    telemetry::build_metric(tzone, telemetry::MetricType::Airflow, "/Oem/Intel_RackScale/VolumetricAirflowCfm", 100);
    log_debug("rmm_agent", "Adding Thermal Zone: " << tzone.get_uuid());
    get_manager<ThermalZone>().add_entry(tzone);
    return tzone.get_uuid();
}

ZoneUuidTriple create_zone_chassis(const std::string& parent) {
    auto zone_chassis = ::make_zone_chassis(parent);
    auto pzone_uuid = ::create_power_zone(zone_chassis.get_uuid());
    auto tzone_uuid = ::create_thermal_zone(zone_chassis.get_uuid());
    log_debug("rmm_agent", "Adding Zone chassis: " << zone_chassis.get_uuid());
    get_manager<Chassis>().add_entry(zone_chassis);
    return ZoneUuidTriple(tzone_uuid, pzone_uuid, zone_chassis.get_uuid());
}

std::string create_rack_chassis(const std::string& parent, const std::vector<ZoneUuidTriple>& zones) {
    auto rack_chassis = ::make_rack_chassis(parent);

    for (unsigned int i = 0; i < ::DRAWERS_PER_RACK; ++i) {
        ZoneUuidTriple zone{};
        zone = zones[i % ::ZONE_MANAGERS_COUNT];

        auto drawer = ::make_drawer(parent, i, rack_chassis.get_location_id(), std::get<0>(zone), std::get<1>(zone));
        log_debug("rmm_agent", "Adding Drawer chassis: " << drawer.get_uuid());
        get_manager<Chassis>().add_entry(drawer);
    }

    log_debug("rmm_agent", "Adding Rack chassis: " << rack_chassis.get_uuid());
    get_manager<Chassis>().add_entry(rack_chassis);
    return rack_chassis.get_uuid();
}

void create_vlans(const std::string& parent) {
    for (int i = 0; i < 2; ++i) {
        auto vlan = ::make_port_vlan(parent, (i != 0));
        log_debug("rmm_agent", "Adding port vlan: " << vlan.get_uuid());
        get_manager<EthernetSwitchPortVlan>().add_entry(vlan);
    }
}

void create_network_interfaces(const std::string& parent) {
    for (int i = 0; i < 2; ++i) {
        auto iface = ::make_network_interface(parent);
        // First Network Interface on RMM has VLANs and 2 IPv4 addresses
        if (i == 0) {
            create_vlans(iface.get_uuid());
            iface.add_ipv4_address(attribute::Ipv4Address(
                "1.1.1.254",
                "255.255.255.0",
                enums::Ipv4AddressOrigin::Static,
                "0.0.0.0"
            ));
        }
        log_debug("rmm_agent", "Adding network interface: " << iface.get_uuid());
        get_manager<NetworkInterface>().add_entry(iface);
    }

}

void create_managers() {
    std::vector<ZoneUuidTriple> zones{};
    for (int i = 0; i < ::ZONE_MANAGERS_COUNT; ++i) {
        auto zone_manager = ::make_zone_manager(i);
        auto zone = ::create_zone_chassis(zone_manager.get_uuid());
        zones.push_back(zone);
        zone_manager.set_location(std::get<2>(zone));
        log_debug("rmm_agent", "Adding Zone manager: " << zone_manager.get_uuid());
        get_manager<Manager>().add_entry(zone_manager);
    }

    auto rack_manager = ::make_rack_manager();
    auto rack_chassis_uuid = ::create_rack_chassis(rack_manager.get_uuid(), zones);
    rack_manager.set_location(rack_chassis_uuid);
    ::create_network_interfaces(rack_manager.get_uuid());
    log_debug("rmm_agent", "Adding Rack manager: " << rack_manager.get_uuid());
    get_manager<Manager>().add_entry(rack_manager);
}
}

void agent::rmm::generate_data() {
    telemetry::build_metric_definitions();
    ::create_managers();
}
