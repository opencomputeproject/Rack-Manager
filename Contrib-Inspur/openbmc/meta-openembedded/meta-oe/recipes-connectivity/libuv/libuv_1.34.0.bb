SUMMARY = "A multi-platform support library with a focus on asynchronous I/O"
HOMEPAGE = "https://github.com/libuv/libuv"
BUGTRACKER = "https://github.com/libuv/libuv/issues"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a68902a430e32200263d182d44924d47"

SRCREV = "15ae750151ac9341e5945eb38f8982d59fb99201"
SRC_URI = "git://github.com/libuv/libuv;branch=v1.x"

S = "${WORKDIR}/git"

inherit autotools

do_configure() {
    ${S}/autogen.sh || bbnote "${PN} failed to autogen.sh"
    oe_runconf
}

BBCLASSEXTEND = "native"
