DESCRIPTION = "Ingrasys tools copy"
SECTION = "examples"
LICENSE = "CLOSED"
PR = "r0"

# Consider all files under the files directory in the same location as this recipe file
FILESEXTRAPATHS_prepend := "${THISDIR}/../../../../rackmanager/MTE/uart:"
SRC_URI = "file://*"


S = "${WORKDIR}"

do_compile() {
${CC} ttyS0.c -o ttyS0
${CC} ttyS1.c -o ttyS1
${CC} ttyS2.c -o ttyS2
}

do_install() {
	# Copy a dummy test file under /etc
	install -d ${D}/usr/bin
	install -m 0766 ttyS0 ${D}/usr/bin
	install -m 0766 ttyS1 ${D}/usr/bin
	install -m 0766 ttyS2 ${D}/usr/bin
}
     
