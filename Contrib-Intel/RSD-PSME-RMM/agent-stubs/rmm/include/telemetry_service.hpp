/*!
 * @brief declarations RMM stub utils for generation of telemetric resources
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
 * @file telemetry_service.hpp
 */

#pragma once

#include "agent-framework/module/model/model_chassis.hpp"
#include "agent-framework/module/managers/utils/manager_utils.hpp"

#include "json-wrapper/json-wrapper.hpp"

namespace agent {
namespace rmm {
namespace telemetry {

enum class MetricType : uint32_t { Temperature1, Temperature2, Voltage1, Voltage2, FanReading,
    Airflow, InputPower, PowerConsumed };

/*!
 * @brief Get metric definition by it's enum type
 *
 * @param type MetricType for identifying MetricDefinitions
 * @returns reference to static MetricDefinition object
 */
agent_framework::model::MetricDefinition& get_metric_definition(MetricType type);

/*!
 * @brief Builds all metric definitions for this agent's metrics.
 *
 * @warning should be called once, before any call to build_metric()
 */
void build_metric_definitions();

/*!
 * @brief Builds a metric for given resource.
 *
 * @param resource Resource for which metric is build.
 * @param type MetricType for matching with MetricDefinitions
 * @param metric_name the metric's name (jsonptr for REST server)
 * @param value initial value of the metric
 */
template<typename R>
void build_metric(const R& resource, MetricType type, const std::string& metric_name, const json::Json& value) {
    const auto& metric_definition_uuid = get_metric_definition(type).get_uuid();
    agent_framework::model::Metric metric{};
    metric.set_component_uuid(resource.get_uuid());
    metric.set_component_type(resource.get_component());
    metric.set_metric_definition_uuid(metric_definition_uuid);
    metric.set_name(metric_name);
    metric.set_value(value);
    log_debug("rmm_agent", "Adding metric: " << metric.get_uuid());
    agent_framework::module::get_manager<agent_framework::model::Metric>().add_entry(metric);
}

}
}
}
