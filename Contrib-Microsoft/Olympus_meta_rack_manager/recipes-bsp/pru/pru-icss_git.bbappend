DESCRIPTION = "PRU Firmware"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://ocs-am437x/LICENSE.md;md5=082b4b727e4aa05e111f61cd44674430"

COMPATIBLE_MACHINE = "ti43x"

PACKAGES_prepend = "${PN}-prufw"
RDEPENDS_${PN}_append = "${PN}-prufw"

FILESEXTRAPATHS_prepend := "${THISDIR}/pru_fw:"

SRC_URI += "file://pru_fw.tar.gz"

SUBDIRS += "ocs-am437x/pru_fw/pru_1_0 ocs-am437x/pru_fw/pru_1_1"

do_install_append_ti43x() {
	for i in 0 1
	do
		install -m 644 ${S}/ocs-am437x/pru_fw/pru_1_${i}/gen/pru_1_${i}.out \
                   ${D}/lib/firmware/pru
	done
}

FILES_${PN}-prufw = "/lib/firmware/pru/pru_1_*"
ALTERNATIVE_pru-icss-prufw = "${PRU_ICSS_ALTERNATIVES}"

ALTERNATIVE_TARGET_pru-icss-prufw[am437x-pru1_0-fw] = "/lib/firmware/pru/pru_1_0.out"
ALTERNATIVE_TARGET_pru-icss-prufw[am437x-pru1_1-fw] = "/lib/firmware/pru/pru_1_1.out"

ALTERNATIVE_PRIORITY_pru-icss-prufw = "150"
INSANE_SKIP_${PN}-prufw = "arch"

