DESCRIPTION = "IPMITool application"
SECTION = "rmapps"
LICENSE = "BSD"
PR = "r0"

LIC_FILES_CHKSUM = "file://COPYING;md5=9aa91e13d644326bf281924212862184"

# Consider all files under the files directory in the same location as this recipe file
FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRCREV = "2c3a876a7354e3c5dc1d500bc10f90f2f40f2035"
SRC_URI = "git://git.code.sf.net/p/ipmitool/source"
SRC_URI += "file://ipmitool_rmfiles.patch"
SRC_URI += "file://ipmitool_addfiles.patch"
SRC_URI += "file://ipmitool_modify.patch"

S = "${WORKDIR}/git"

inherit autotools 

DEPENDS = "openssl readline"
     
