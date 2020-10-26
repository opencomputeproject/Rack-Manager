FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"
PV = "1.0"
SRC_URI = "git://github.com/inspur-bmc/ocp-i9000-bmcweb;protocol=https"
SRCREV = "f3cc7255951cbf745b1bbb2c917e7af149466c27"
S = "${WORKDIR}/build"
LICENSE = "CLOSED"
DEPENDS += "libevdev"
EXTRA_OECMAKE_append = " \
    -DBMCWEB_ENABLE_REDFISH_RMC=ON \
    -DBMCWEB_ENABLE_REDFISH_BMC_JOURNAL=ON \
"
