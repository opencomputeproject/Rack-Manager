DESCRIPTION = "Rack Manager Redfish RESTful Interface Application"
SECTION = "rmapps"
LICENSE = "GPLv2"
PR = "r0"

RDEPENDS_${PN} = "python python-netaddr python-ocsapi"

PYTHON_DEST = "${D}${bindir}"
PYTHON_NAME = "rackmanager"
inherit msocs_python

do_install_append() {
    # Remove the metadata script
    rm -f ${PYTHON_DEST}/${PYTHON_NAME}/redfish/schemas/metadata_generator.sh
    
    # Install the SSL certificates
    install -d -m 0755 ${D}/usr/lib/sslcerts
    mv ${PYTHON_DEST}/${PYTHON_NAME}/certs.pem ${D}/usr/lib/sslcerts
    mv ${PYTHON_DEST}/${PYTHON_NAME}/privkey.pem ${D}/usr/lib/sslcerts
}

FILES_${PN} += "${bindir}/${PYTHON_NAME} /usr/lib/sslcerts"