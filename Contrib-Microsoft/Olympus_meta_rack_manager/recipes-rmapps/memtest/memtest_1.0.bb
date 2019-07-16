DESCRIPTION = "Memtest application"
HOMEPAGE = "http://pyropus.ca/software/memtester/"
SECTION = "rmapps"
LICENSE = "CLOSED"
PR = "r0"

SRC_URI = "http://pyropus.ca/software/memtester/old-versions/memtester-${PV}.tar.gz"
PV = "4.3.0"

SRC_URI[md5sum] = "598f41b7308e1f736164bca3ab84ddbe"
SRC_URI[sha256sum] = "f9dfe2fd737c38fad6535bbab327da9a21f7ce4ea6f18c7b3339adef6bf5fd88"

S = "${WORKDIR}/memtester-${PV}"

do_compile () {
	echo '${CC} ${CFLAGS} -DPOSIX -c' > conf-cc
	echo '${CC} ${LDFLAGS}' > conf-ld
	oe_runmake
}

do_install () {
	install -d ${D}${bindir}
	install -d ${D}${mandir}/man8
	install -m 0755 memtester ${D}${bindir}/
	install -m 0755 memtester.8 ${D}${mandir}/man8/
}
