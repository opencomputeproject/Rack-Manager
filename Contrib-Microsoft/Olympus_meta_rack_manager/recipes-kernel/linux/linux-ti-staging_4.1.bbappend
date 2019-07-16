DESCRIPTION = "Customizations: Linux kernel for TI devices"

# Include dtb file for just the SK version
#KERNEL_DEVICETREE_ti43x = "am437x-sk-evm.dtb"
KERNEL_DEVICETREE_ti43x = "am437x-ms-ocs.dtb"

KERNEL_CONFIG_FRAGMENTS_append_ti43x = " ${WORKDIR}/ocs437x-rm.cfg"

# Changing default kernel config settings - add just the delta
FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://ocs437x-rm.cfg"
SRC_URI += "file://m0Patch.patch"

# Add recipe for PRU firmware under /lib/firmware in rootfs 
RDEPENDS_kernel-base_append_ocs-am437x = " pru-icss"

#v4.1.21
SRCREV = "1c9b6ad8bbbab9337ed397a797077ae9eb25c11f"
PV = "4.1.21+git${SRCPV}"

# Append to the MACHINE_KERNEL_PR so that a new SRCREV will cause a rebuild
MACHINE_KERNEL_PR_append = "l"
PR = "${MACHINE_KERNEL_PR}"

module_autoload += " pruss"
module_autoload += " pru-rproc" 
module_autoload += " virtio-rpmsg-bus" 
module_autoload += " rpmsg-pru"
module_autoload += " omap-wdt"
module_autoload += " rng-core"
module_autoload += " omap-rng"
module_autoload += " pm33xx"
module_autoload += " omap-aes-driver"
module_autoload += " omap-sham"
module_autoload += " omap-des"
module_autoload += " rtc-omap"
module_autoload += " autofs4"
module_autoload += " ipv6"
