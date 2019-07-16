DESCRIPTION = "Handle RM HW GPIO interrupts"
LICENSE = "CLOSED"
PR = "r0"

inherit module

PR = "r0"
PV = "0.1"

FILESEXTRAPATHS_prepend := "${THISDIR}/../../../../rackmanager/ocs/ocsgpio:"

SRC_URI = "file://kernelmod"

S = "${WORKDIR}/kernelmod"

# The inherit of module.bbclass will automatically name module packages with
# "kernel-module-" prefix as required by the oe-core build environment.
