DESCRIPTION = "flasher image files"
SECTION = "flasher"
LICENSE = "CLOSED"
PR = "r0"

# Consider all files under the files directory in the same location as this recipe file
FILESEXTRAPATHS_prepend := "${THISDIR}/../../../../rackmanager/ocs/ocsfwup:"
FILESEXTRAPATHS_prepend := "${TOPDIR}/images/qspi:"
FILESEXTRAPATHS_prepend := "${TOPDIR}/images/emmc:"
SRC_URI =  "file://scripts \
			file://qspi-rootfs.jffs2 \
			file://qspi-zImage.bin \
			file://qspi-am437x-msocs.dtb \
			file://pkg.manifest \
			file://qspi-u-boot.bin \
			file://emmc-u-boot.img \
			file://MLO "

S = "${WORKDIR}"

do_compile() {
}

do_install() {
	install -d ${D}${sysconfdir}/
	install -m 0755 ${S}/scripts/launchupgrade.sh ${D}${sysconfdir}/
	install -m 0755 ${S}/scripts/factorysetup.sh ${D}${sysconfdir}/
	install -m 0755 ${S}/scripts/fwupgrade.sh ${D}${sysconfdir}/
	install -m 0644 ${S}/scripts/fwup.config ${D}${sysconfdir}/
	
	install -d ${D}/etc/images/qspi
	install -m 0644 ${S}/qspi-rootfs.jffs2 ${D}/etc/images/qspi/rootfs.jffs2
	install -m 0644 ${S}/qspi-u-boot.bin ${D}/etc/images/qspi/u-boot.bin
	install -m 0644 ${S}/qspi-zImage.bin ${D}/etc/images/qspi/zImage.bin
	install -m 0644 ${S}/qspi-am437x-msocs.dtb ${D}/etc/images/qspi/am437x-msocs.dtb
	install -m 0644 ${S}/pkg.manifest ${D}/etc/images/qspi/pkg.manifest

	install -d ${D}/etc/images/emmc
	install -m 0644 ${S}/emmc-u-boot.img ${D}/etc/images/emmc/u-boot.img
	install -m 0644 ${S}/MLO ${D}/etc/images/emmc/MLO
	install -m 0644 ${S}/qspi-am437x-msocs.dtb ${D}/etc/images/emmc/am437x-msocs.dtb
}
