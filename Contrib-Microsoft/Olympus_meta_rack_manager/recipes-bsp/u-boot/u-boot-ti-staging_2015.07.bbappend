LICENSE = "CLOSED"
DESCRIPTION = "Customization: u-boot bootloader for TI devices"

SRCREV = "2cc2dbc87659527734cbe0f73df7677104740ac7"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://ubootPatch.patch"

python __anonymous() {
    if bb.data.getVar ("UBOOT_MACHINE", d, "") == "am43xx_ocs_qspiboot_config":
        bb.data.setVar ("SPL_BINARY", "", d)
        bb.data.setVar ("SPL_UART_BINARY", "", d)
        bb.data.setVar ("UBOOT_SUFFIX", "bin", d)
        bb.data.setVar ("UBOOT_SPI_BINARY", "u-boot.bin", d)
        bb.data.setVar ("UBOOT_SPI_IMAGE", "u-boot-${MACHINE}-${PV}-${PR}.bin", d)
        bb.data.setVar ("UBOOT_SPI_SYMLINK", "u-boot-${MACHINE}.bin", d)
}