DESCRIPTION = "WcsCli User Interface Application"
SECTION = "rmapps"
LICENSE = "GPLv2"
PR = "r0"

RDEPENDS_${PN} = "python python-ocsapi"

PYTHON_DEST = "${D}${bindir}"
PYTHON_NAME = "wcscli"
inherit msocs_python

do_install_append() {
    mv ${PYTHON_DEST}/${PYTHON_NAME}/wcs-cli ${D}${bindir}
    chmod 755 ${D}${bindir}/wcs-cli
    
    install -d ${D}${sysconfdir}/profile.d
    mv ${PYTHON_DEST}/${PYTHON_NAME}/wcscli.sh ${D}${sysconfdir}/profile.d
}

FILES_${PN} += "${bindir}/${PYTHON_NAME} ${sysconfdir}"