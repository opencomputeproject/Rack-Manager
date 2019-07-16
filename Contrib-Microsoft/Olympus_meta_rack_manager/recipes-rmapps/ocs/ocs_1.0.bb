DESCRIPTION = "OCS system libraries and services"
SECTION = "rmapps"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=b9fa8adffea4ca5ddf358161d0f9e652"

PR = "r0"

SRCREV = "${AUTOREV}"
PV = "1.0-git${SRCPV}"

SRC_URI = "git://github.com/Project-Olympus/rackmanager.git;protocol=https;subpath=ocs"

S = "${WORKDIR}/ocs"

PACKAGE_BEFORE_PN = "${PN}-itp"
INITSCRIPT_PACKAGES = "${PN} ${PN}-itp"

INITSCRIPT_NAME_${PN} = "Ocs-init.sh"
INITSCRIPT_PARAMS_${PN} = "start 39 S . stop 10 0 6 ."

INITSCRIPT_NAME_${PN}-itp = "ocs-itp.sh"
INITSCRIPT_PARAMS_${PN}-itp = "start 96 . stop 4 ."

DEPENDS = "i2c-tools zlog openssl"
RDEPENDS_${PN} = "zlog libcrypto gpio-mon"
RDEPENDS_${PN}-itp = "${PN}"

inherit msocs update-rc.d

do_install_append() {
    install -d ${D}/var/local
	install -m 0766 ${S}/adc-util/adc-util/file1.txt ${D}/var/local/adccalibration.txt
	install -m 0766 ${S}/fru-util/file1.txt ${D}/var/local/fruupdate.txt
	install -m 0766 ${S}/mac-util/file1.txt ${D}/var/local/macupdate.txt
	install -m 0644 ${S}/OcsAudit/ocsaudit_zlog.conf ${D}/var/local
	install -m 0644 ${S}/Ocslog/ocslog.conf ${D}/var/local/
	install -m 0644 ${S}/OcsTelemetry/ocstelemetry_zlog.conf ${D}/var/local
	install -m 0644 ${S}/Persist/ocs-persist.txt ${D}/var/local/ocs-persist.txt
	
	install -d ${D}${sysconfdir}
	install -m 0755 ${S}/ocsfwup/scripts/init_fwupgrade.sh ${D}${sysconfdir}
	
	install -d ${D}/${sysconfdir}/init.d
	install -m 0755 ${S}/Init/Ocs-init.sh ${D}${sysconfdir}/init.d
    install -m 0755 ${S}/RemoteITP/ocs-itp.sh ${D}/${sysconfdir}/init.d
}

FILES_${PN} += "${libdir} ${sysconfdir} /var/local"
FILES_${PN}-itp += "${sysconfdir}/init.d/ocs-itp.sh ${bindir}/ocs-itp"
FILES_SOLIBSDEV = "${libdir}/libocsgpio.so ${libdir}/libocsfwupgrade.so"
