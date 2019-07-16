DESCRIPTION = "TI PRU Code Generation Tools"
HOMEPAGE = "https://www-a.ti.com/downloads/sds_support/TICodegenerationTools/download.htm"
LICENSE = "(TI-TSPA & Thai-Open-Source-Software-Center) & BSD-3-Clause & BSL-1.0 & Hewlett-Packard & AFL-3.0 & MIT & BSD-2-Clause & PD"

LIC_FILES_CHKSUM = "file://ti-cgt-pru_${PV}/LICENSE.txt;md5=b6311962635a4f15630e36ec2d875eca"
LIC_FILES_CHKSUM_class-target = "file://usr/share/doc/ti/cgt-pru/LICENSE.txt;md5=b6311962635a4f15630e36ec2d875eca"

require recipes-ti/includes/ti-paths.inc
require recipes-ti/includes/ti-unpack.inc

BINFILE = "ti_cgt_pru_${PV}_linux_installer_x86.bin"
BINFILE_NAME = "cgt-pru-x86"
TI_BIN_UNPK_ARGS = "--prefix ${S}"
TI_BIN_UNPK_CMDS = ""

BINFILE_class-target = "ti_cgt_pru_${PV}_armlinuxa8hf_busybox_installer.sh"
BINFILE_NAME_class-target = "cgt-pru-arm"

SRC_URI = "http://software-dl.ti.com/codegen/esd/cgt_public_sw/PRU/${PV}/${BINFILE};name=${BINFILE_NAME}"

SRC_URI[cgt-pru-x86.md5sum] = "a6e38afbbbe2f16efb92bde29e795a82"
SRC_URI[cgt-pru-x86.sha256sum] = "79c89c4f91106ed55c6a6f1b1e07fd4ebc4b7e4cc82300daf4dfbffd13e60098"

do_install() {
    install -d ${D}${TI_CGT_PRU_INSTALL_DIR_RECIPE}
    cp -r ${S}/ti-cgt-pru_${PV}/. \
          ${D}${TI_CGT_PRU_INSTALL_DIR_RECIPE}/
}

do_install_class-target() {
    ${WORKDIR}/${BINFILE} --prefix ${D}
}

FILES_${PN} += "${datadir}/ti/*"

FILES_${PN}-dbg = "${TI_CGT_PRU_INSTALL_DIR_RECIPE}/bin/.debug \
                   ${TI_CGT_PRU_INSTALL_DIR_RECIPE}/lib/.debug \
"

INSANE_SKIP_${PN} += "arch staticdev"

BBCLASSEXTEND = "native nativesdk"
