DESCRIPTION = "Common Api for Ocscli and RackManager"
SECTION = "rmapps"
LICENSE = "GPLv2"
PR = "r0"

RDEPENDS_${PN} = " \
    python \
    python-xml \
    python-netaddr \
    python-paramiko \
    ipmitool \
    update-rc.d \
    ocs \
    ocs-itp \
    rm-versions \
"

PYTHON_DEST = "${D}${libdir}"
PYTHON_NAME = "commonapi"
inherit msocs_python

FILES_${PN} += "${libdir}/${PYTHON_NAME}"