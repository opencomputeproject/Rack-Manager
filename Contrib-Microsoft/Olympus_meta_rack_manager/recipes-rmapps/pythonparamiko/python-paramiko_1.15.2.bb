DESCRIPTION = "SSH2 protocol library"
HOMEPAGE = "https://github.com/paramiko/paramiko/"
SECTION = "devel/python"
LICENSE = "LGPLv2.1"
LIC_FILES_CHKSUM = "file://LICENSE;md5=fd0120fc2e9f841c73ac707a30389af5"

PR = "r0"
SRCNAME = "paramiko"

SRC_URI = "http://pypi.python.org/packages/source/p/${SRCNAME}/${SRCNAME}-${PV}.tar.gz"

SRC_URI[md5sum] = "6bbfb328fe816c3d3652ba6528cc8b4c"
SRC_URI[sha256sum] = "4f56a671a3eecbb76e6143e6e4ca007d503a39aa79aa9e14ade667fa53fd6e55"

S = "${WORKDIR}/${SRCNAME}-${PV}"

inherit setuptools

RDEPENDS_${PN} += "python-pycrypto"