DESCRIPTION = "RM board init script"
SECTION = "core"
LICENSE = "GPLv2"
PR = "r0"

LIC_FILES_CHKSUM = "file://rminit.sh;beginline=3;endline=8;md5=3f33611ea3245ee13c56e410b84db27d"

SRC_URI = " \
    file://rminit.sh \
    file://exports \
"

S = "${WORKDIR}"

RDEPENDS_${PN} = " \
    ocs \
    rackmanager \
"

# This is purposely wrong to force update-rc.d to be installed in the rootfs.
INITSCRIPT_NAME = "rminit"
INITSCRIPT_PARAMS = "start 95 2 3 4 5 ."

inherit update-rc.d

do_install_append() {
    install -d ${D}${sysconfdir}/init.d/
    install -m 0755 rminit.sh ${D}${sysconfdir}/init.d
	update-rc.d -r ${D} ${INITSCRIPT_NAME}.sh ${INITSCRIPT_PARAMS}
	
	install -m 0755 exports ${D}${sysconfdir}/
}
