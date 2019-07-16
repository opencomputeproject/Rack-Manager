# <license_header>
#
# Copyright (c) 2017-2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# </license_header>
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_subdirectory(command)

add_library(rmm-commands-stubs STATIC
    $<TARGET_OBJECTS:rmm-command-stubs>
)

add_executable(psme-rmm-stubs
    telemetry_service.cpp
    generate_data.cpp
    main.cpp
)

generate_default_config_file(
    main.cpp
    agent
    generic
    "AGENT_RMM_CONFIGURATION_FILE"
    ../include/default_configuration.hpp
    ..
)

target_link_libraries(psme-rmm-stubs
    ${AGENT_RMM_STUB_LIBRARIES}
    rmm-commands-stubs
    agent-framework
    ${UUID_LIBRARIES}
    ${LOGGER_LIBRARIES}
    ${PCA95XX_LIBRARIES}
    ${SAFESTRING_LIBRARIES}
    configuration
    pthread
    ${CURL_LIBRARIES}
    ${MICROHTTPD_LIBRARIES}
    md5
)
