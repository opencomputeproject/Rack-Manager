SUMMARY = "OpenBMC for Facebook - Applications"
PR = "r1"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = " \
        ${PN}-system \
        "

PROVIDES += "virtual/obmc-system-mgmt"

RPROVIDES_${PN}-system += "virtual-obmc-system-mgmt"

SUMMARY_${PN}-system = "Facebook system for Yosemite platform"
RDEPENDS_${PN}-system = " \
        entity-manager \
        dbus-sensors \
        phosphor-pid-control \
        "
