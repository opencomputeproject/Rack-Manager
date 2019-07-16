# Pooled System Management Engine (PSME) Software

PSME Software is a bundle of applications working and communicating with each other to manage and control specific assets in a setup.

# PSME Software

## Agents
- **PSME Rack Management Module (RMM) Agent**:
    is responsible for management of a rack's hardware.

## Services
 **PSME REST Server**:

    The HTTP server with REST API and JSON data container is responsible for gathering and presenting information about assets and available
    operations on these assets. This application communicates with the appropriate agents through JSON-RPC as a transport and the Generic Asset Management
    Interface as a payload protocol.

## Build instruction
- RMM agent (./agents/rmm) :
  ./build_main.sh -b release -a 64 -c gcc -t psme-rmm
- REST server (./application):
  ./build_main.sh -b release -a 64 -c gcc -t psme-rest-server

# Getting started
The PSME Software is designed and developed to support generic hardware. It should compile and run on any Linux* system if the required
libraries are available and at the proper version for the specific operating system. The reference operating systems is Ubuntu* v16.04 LTS.
