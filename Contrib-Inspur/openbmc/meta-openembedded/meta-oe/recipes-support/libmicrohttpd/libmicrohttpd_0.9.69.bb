DESCRIPTION = "A small C library that is supposed to make it easy to run an HTTP server as part of another application"
HOMEPAGE = "http://www.gnu.org/software/libmicrohttpd/"
LICENSE = "LGPL-2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=57d09285feac8a64efa878e692b14f36"
SECTION = "net"

DEPENDS = "file"

SRC_URI = "${GNU_MIRROR}/libmicrohttpd/${BPN}-${PV}.tar.gz \
"
SRC_URI[md5sum] = "3ce03db1f10007517cecf05e040069af"
SRC_URI[sha256sum] = "fb9b6b148b787493e637d3083588711e65cbcb726fa02cee2cd543c5de27e37e"

inherit autotools lib_package pkgconfig gettext

CFLAGS += "-pthread -D_REENTRANT"

EXTRA_OECONF += "--disable-static --with-gnutls=${STAGING_LIBDIR}/../"

PACKAGECONFIG ?= "curl https"
PACKAGECONFIG_append_class-target = "\
        ${@bb.utils.filter('DISTRO_FEATURES', 'largefile', d)} \
"
PACKAGECONFIG[largefile] = "--enable-largefile,--disable-largefile,,"
PACKAGECONFIG[curl] = "--enable-curl,--disable-curl,curl,"
PACKAGECONFIG[https] = "--enable-https,--disable-https,libgcrypt gnutls,"

do_compile_append() {
    sed -i s:-L${STAGING_LIBDIR}::g libmicrohttpd.pc
}
