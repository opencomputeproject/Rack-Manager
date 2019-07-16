FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://busybox.patch"
INITSCRIPT_PARAMS_${PN}-syslog = "start 38 S . stop 20 0 6 ."