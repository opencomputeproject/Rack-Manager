/*!
 * @brief definitions RMM stub utils for generation of telemetric resources
 *
 * @copyright Copyright (c) 2017-2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @file telemetry_service.cpp
 */

#include "telemetry_service.hpp"

using namespace agent::rmm::telemetry;
using namespace agent_framework::model;

MetricDefinition& agent::rmm::telemetry::get_metric_definition(MetricType type) {
    static MetricDefinition fan_reading_definition;
    static MetricDefinition inlet_temperature_definition1;
    static MetricDefinition inlet_temperature_definition2;
    static MetricDefinition voltage_definition1;
    static MetricDefinition voltage_definition2;
    static MetricDefinition airflow_definition;
    static MetricDefinition input_power_definition;
    static MetricDefinition power_consumed_definition;

    switch (type) {
        case MetricType::Temperature1: return inlet_temperature_definition1;
        case MetricType::Temperature2: return inlet_temperature_definition2;
        case MetricType::Voltage1: return voltage_definition1;
        case MetricType::Voltage2: return voltage_definition2;
        case MetricType::FanReading: return fan_reading_definition;
        case MetricType::Airflow: return airflow_definition;
        case MetricType::InputPower: return input_power_definition;
        case MetricType::PowerConsumed: return power_consumed_definition;
        default: return fan_reading_definition;
    }
}

void agent::rmm::telemetry::build_metric_definitions() {
    // TODO: use MetricDefinitionBuilder

    MetricDefinition& fan_reading_definition = get_metric_definition(MetricType::FanReading);
    fan_reading_definition.set_implementation(enums::MetricImplementation::PhysicalSensor);
    fan_reading_definition.set_calculable(enums::MetricCalculable::NonSummable);
    fan_reading_definition.set_units("RPM");
    fan_reading_definition.set_data_type(enums::MetricDataType::Int32);
    fan_reading_definition.set_is_linear(true);
    fan_reading_definition.set_metric_type(enums::MetricType::Numeric);
    fan_reading_definition.set_physical_context(enums::PhysicalContext::Exhaust);
    fan_reading_definition.set_sensor_type(enums::SensorType::Fan);
    log_debug("rmm_agent", "Adding definition: " << fan_reading_definition.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(fan_reading_definition);

    MetricDefinition& inlet_temperature_definition1 = get_metric_definition(MetricType::Temperature1);
    inlet_temperature_definition1.set_name("Drawer first inlet Temp sensor");
    inlet_temperature_definition1.set_implementation(enums::MetricImplementation::PhysicalSensor);
    inlet_temperature_definition1.set_calculable(enums::MetricCalculable::NonSummable);
    inlet_temperature_definition1.set_units("Celsius");
    inlet_temperature_definition1.set_data_type(enums::MetricDataType::Int32);
    inlet_temperature_definition1.set_is_linear(true);
    inlet_temperature_definition1.set_metric_type(enums::MetricType::Numeric);
    inlet_temperature_definition1.set_physical_context(enums::PhysicalContext::Exhaust);
    inlet_temperature_definition1.set_sensor_type(enums::SensorType::Temperature);
    log_debug("rmm_agent", "Adding definition: " << inlet_temperature_definition1.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(inlet_temperature_definition1);

    MetricDefinition& inlet_temperature_definition2 = get_metric_definition(MetricType::Temperature2);
    inlet_temperature_definition2 = inlet_temperature_definition1;
    inlet_temperature_definition2.make_random_uuid();
    inlet_temperature_definition2.set_name("Drawer second inlet Temp sensor");
    log_debug("rmm_agent", "Adding definition: " << inlet_temperature_definition2.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(inlet_temperature_definition2);

    MetricDefinition& voltage_definition1 = get_metric_definition(MetricType::Voltage1);
    voltage_definition1.set_name("VRM0 Voltage");
    voltage_definition1.set_implementation(enums::MetricImplementation::PhysicalSensor);
    voltage_definition1.set_calculable(enums::MetricCalculable::NonSummable);
    voltage_definition1.set_units("V");
    voltage_definition1.set_data_type(enums::MetricDataType::Int32);
    voltage_definition1.set_is_linear(true);
    voltage_definition1.set_metric_type(enums::MetricType::Numeric);
    voltage_definition1.set_physical_context(enums::PhysicalContext::VoltageRegulator);
    voltage_definition1.set_sensor_type(enums::SensorType::Voltage);
    log_debug("rmm_agent", "Adding definition: " << voltage_definition1.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(voltage_definition1);

    MetricDefinition& voltage_definition2 = get_metric_definition(MetricType::Voltage2);
    voltage_definition2 = voltage_definition1;
    voltage_definition2.make_random_uuid();
    voltage_definition2.set_name("VRM1 Voltage");
    log_debug("rmm_agent", "Adding definition: " << voltage_definition2.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(voltage_definition2);

    MetricDefinition& airflow_definition = get_metric_definition(MetricType::Airflow);
    airflow_definition.set_implementation(enums::MetricImplementation::PhysicalSensor);
    airflow_definition.set_calculable(enums::MetricCalculable::NonSummable);
    airflow_definition.set_units("Cfm");
    airflow_definition.set_data_type(enums::MetricDataType::Int32);
    airflow_definition.set_is_linear(true);
    airflow_definition.set_metric_type(enums::MetricType::Numeric);
    airflow_definition.set_physical_context(enums::PhysicalContext::Exhaust);
    airflow_definition.set_sensor_type(enums::SensorType::Fan);
    log_debug("rmm_agent", "Adding definition: " << airflow_definition.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(airflow_definition);

    MetricDefinition& input_power_definition = get_metric_definition(MetricType::InputPower);
    input_power_definition.set_implementation(enums::MetricImplementation::PhysicalSensor);
    input_power_definition.set_calculable(enums::MetricCalculable::NonSummable);
    input_power_definition.set_units("W");
    input_power_definition.set_data_type(enums::MetricDataType::Int32);
    input_power_definition.set_is_linear(true);
    input_power_definition.set_metric_type(enums::MetricType::Numeric);
    input_power_definition.set_physical_context(enums::PhysicalContext::PowerSupplyBay);
    input_power_definition.set_sensor_type(enums::SensorType::PowerSupplyOrConverter);
    log_debug("rmm_agent", "Adding definition: " << input_power_definition.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(input_power_definition);

    MetricDefinition& power_consumed_definition = get_metric_definition(MetricType::PowerConsumed);
    power_consumed_definition.set_implementation(enums::MetricImplementation::PhysicalSensor);
    power_consumed_definition.set_calculable(enums::MetricCalculable::NonSummable);
    power_consumed_definition.set_units("W");
    power_consumed_definition.set_data_type(enums::MetricDataType::Int32);
    power_consumed_definition.set_is_linear(true);
    power_consumed_definition.set_metric_type(enums::MetricType::Numeric);
    power_consumed_definition.set_physical_context(enums::PhysicalContext::PowerSupply);
    power_consumed_definition.set_sensor_type(enums::SensorType::PowerSupplyOrConverter);
    log_debug("rmm_agent", "Adding definition: " << power_consumed_definition.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::MetricDefinition>().add_entry(power_consumed_definition);
}
