DESCRIPTION = "Bottle Web Framework"
SECTION = "base"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://bottle.py;beginline=1;endline=14;md5=15d806194a048a43e3a7f1d4c7574fe6"

SRC_URI = "https://pypi.python.org/packages/source/b/bottle/${PN}-${PV}.tar.gz"
SRC_URI[md5sum] = "f5850258a86224a791171e8ecbb66d99"
SRC_URI[sha256sum] = "fe0a24b59385596d02df7ae7845fe7d7135eea73799d03348aeb9f3771500051"

S = "${WORKDIR}/${PN}-${PV}"

dst="/usr/lib/python2.7"

do_install() {
  mkdir -p ${D}/${dst}
  install -m 755 bottle.py ${D}/${dst}
}

FILES_${PN} = "${dst}"

