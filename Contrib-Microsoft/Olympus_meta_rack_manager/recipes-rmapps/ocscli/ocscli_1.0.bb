DESCRIPTION = "Ocscli User Interface Application"
SECTION = "rmapps"
LICENSE = "GPLv2"
PR = "r0"

RDEPENDS_${PN} = "python python-ocsapi wcscli"

PYTHON_DEST = "${D}${bindir}"
PYTHON_NAME = "ocscli"
inherit msocs_python

do_install_append() {
    mv ${PYTHON_DEST}/${PYTHON_NAME}/ocs-cli ${D}${bindir}
    chmod 755 ${D}${bindir}/ocs-cli
    
    install -d ${D}${sysconfdir}/profile.d
    mv ${PYTHON_DEST}/${PYTHON_NAME}/ocscli.sh ${D}${sysconfdir}/profile.d
}

FILES_${PN} += "${bindir}/${PYTHON_NAME} ${sysconfdir}"