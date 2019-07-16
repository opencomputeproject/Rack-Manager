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

#include "agent-framework/module/common_components.hpp"
#include "agent-framework/registration/amc_connection_manager.hpp"
#include "agent-framework/signal.hpp"
#include "agent-framework/version.hpp"
#include "agent-framework/eventing/utils.hpp"
#include "agent-framework/command/command_server.hpp"
#include "agent-framework/logger_loader.hpp"

#include "configuration/configuration.hpp"
#include "default_configuration.hpp"

#include "generate_data.hpp"

#include "json-rpc/connectors/http_server_connector.hpp"

#include <csignal>
#include <cstdio>
#include <memory>

using namespace agent_framework;
using namespace agent_framework::model;
using namespace agent_framework::generic;
using namespace logger_cpp;
using namespace configuration;

using agent::generic::DEFAULT_CONFIGURATION;
using agent::generic::DEFAULT_ENV_FILE;
using agent::generic::DEFAULT_FILE;

static constexpr unsigned int DEFAULT_SERVER_PORT = 7791;

/*!
 * @brief Generic Agent main method.
 * */
int main(int argc, char* argv[]) {
    std::uint16_t server_port = DEFAULT_SERVER_PORT;

    /* Initialize configuration */
    log_info("agent",
        agent_framework::generic::Version::build_info());
    auto& basic_config = Configuration::get_instance();
    basic_config.set_default_configuration(DEFAULT_CONFIGURATION);
    basic_config.set_default_file(DEFAULT_FILE);
    basic_config.set_default_env_file(DEFAULT_ENV_FILE);
    /* @TODO This should be replaced with nice arguments parsing class */
    while (argc > 1) {
        basic_config.add_file(argv[argc - 1]);
        --argc;
    }
    basic_config.load_key_file();
    const json::Json& configuration = basic_config.to_json();

    /* Initialize logger */
    LoggerLoader loader(configuration);
    loader.load(LoggerFactory::instance());
    log_info("agent", "Running Rmm Stub...\n");

    try {
        server_port = configuration.value("server", json::Json::object()).value("port", std::uint16_t{});
    } catch (const std::exception& e) {
        log_error("agent",
                "Cannot read server port " << e.what());
    }

    RegistrationData registration_data{configuration};

    EventDispatcher event_dispatcher;
    event_dispatcher.start();

    AmcConnectionManager amc_connection(event_dispatcher, registration_data);
    amc_connection.start();

    /* Initialize command server */
    auto http_server_connector = new json_rpc::HttpServerConnector(server_port, registration_data.get_ipv4_address());
    json_rpc::AbstractServerConnectorPtr http_server(http_server_connector);
    agent_framework::command::CommandServer server(http_server);
    server.add(command::Registry::get_instance()->get_commands());
    server.start();

    ::agent::rmm::generate_data();

    agent_framework::eventing::send_add_notifications_for_each<Manager>();
    agent_framework::eventing::send_add_notifications_for_each<MetricDefinition>();
    agent_framework::eventing::send_add_notifications_for_each<Metric>();

    /* Stop the program and wait for interrupt */
    wait_for_interrupt();

    log_info("agent", "Stopping Rmm Stub Agent...\n");

    /* Cleanup */
    server.stop();
    amc_connection.stop();
    event_dispatcher.stop();
    Configuration::cleanup();
    LoggerFactory::cleanup();

    return 0;
}
