SUMMARY = "Phosphor post code manager"
DESCRIPTION = "Phosphor post Code Manager monitors post code posted on dbus \
interface /xyz/openbmc_project/state/boot/raw by snoopd daemon and save them \
in a file under /var/lib for history."

SRC_URI = "git://github.com/openbmc/phosphor-post-code-manager.git"
SRCREV = "655837973feb51da3767f5f246ec198877900b0b"

S = "${WORKDIR}/git"

PV = "1.0+git${SRCPV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

inherit cmake pkgconfig systemd

SYSTEMD_SERVICE_${PN} = "xyz.openbmc_project.State.Boot.PostCode.service"

DEPENDS += " \
    sdbusplus \
    phosphor-dbus-interfaces \
    phosphor-logging \
    "
