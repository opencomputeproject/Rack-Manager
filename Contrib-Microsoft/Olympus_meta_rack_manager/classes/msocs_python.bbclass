LIC_FILES_CHKSUM = "file://../LICENSE.txt;md5=b9fa8adffea4ca5ddf358161d0f9e652"

SRCREV = "${AUTOREV}"
PV = "1.0-git${SRCPV}"

SRC_URI = "git://github.com/Project-Olympus/rackmanager.git;protocol=https;subpath=python-ocs"

S = "${WORKDIR}/python-ocs/${PYTHON_NAME}"

msocs_python_do_install() {
    install -d ${PYTHON_DEST}
    cp -r ${S} ${PYTHON_DEST}/${PYTHON_NAME}
    
    # Clear out project files and compiled scripts.
    rm -rf ${PYTHON_DEST}/${PYTHON_NAME}/.settings
    find ${PYTHON_DEST} \( -name '.*project' -o -name '*.pyc' \) -exec rm -rf {} \;
}

EXPORT_FUNCTIONS do_install
