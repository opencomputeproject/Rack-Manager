DESCRIPTION = "Get RM version info"
SECTION = "core"
LICENSE = "GPLv2"

LIC_FILES_CHKSUM = "file://rmversions.sh;beginline=3;endline=8;md5=3f33611ea3245ee13c56e410b84db27d"

PR = "r0"

SRC_URI =  " \
    file://rmversions.sh \
    file://pkg-info \
    file://rfs-info \
"

S = "${WORKDIR}"

do_compile() {
}

do_install() {
	install -d ${D}${sysconfdir}/
    install -m 0755 ${S}/rmversions.sh ${D}${sysconfdir}/
    install -m 0744 ${S}/pkg-info ${D}${sysconfdir}/
	install -m 0744 ${S}/rfs-info ${D}${sysconfdir}/
}

