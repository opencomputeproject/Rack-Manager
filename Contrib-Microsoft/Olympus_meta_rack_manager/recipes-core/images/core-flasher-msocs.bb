SUMMARY = "Customized Microsoft OCS Rack manager initramfs image."

IMAGE_INSTALL = " \
    packagegroup-core-boot ${ROOTFS_PKGMANAGE_BOOTSTRAP} \
    bash \
    mtd-utils \
    e2fsprogs-mke2fs \
    util-linux \
    dosfstools \
    place-updater \
    rm-versions \
"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit core-image

IMAGE_ROOTFS_SIZE = "8192"
IMAGE_ROOTFS_EXTRA_SPACE = "0"

