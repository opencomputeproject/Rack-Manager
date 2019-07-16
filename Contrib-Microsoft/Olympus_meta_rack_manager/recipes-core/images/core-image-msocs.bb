SUMMARY = "Customized Microsoft OCS Rack manager image."

PYTHON_PKGS = " \ 
python-core \
python-crypt \
python-curses \ 
python-io \ 
python-json \ 
python-shell \ 
python-subprocess \ 
python-argparse \ 
python-ctypes \ 
python-datetime \ 
python-email \ 
python-threading \ 
python-mime \ 
python-pickle \ 
python-misc \ 
python-netserver \ 
python-syslog \ 
python-math \ 
python-distutils \
python-pycrypto \
python-zlib \
python-ecdsa \
python-pyopenssl \
python-pycurl \
" 

IMAGE_INSTALL = " \
    packagegroup-core-boot ${ROOTFS_PKGMANAGE_BOOTSTRAP} \
    openssh \
    ${PYTHON_PKGS} \
    bash \
    i2c-tools \
    pru-icss \
    ocs \
    ocs-itp \
    python-ocsapi \
    bottle \
    cherryPy \
    rackmanager \
    ocscli \
    rm-init \
    ethtool \
    iperf3 \
    memtest \
    sysbench \
    uart-test \
    fio \
    minicom \
    rm-versions \
    curl \
    lmbench \
    stream \
    ifplugd \
    tftp-hpa-server \
    nfs-utils \
    gdb \
    ntp \
    sshpass \
    net-tools \
    wcscli \
"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit core-image

IMAGE_ROOTFS_SIZE = "56192"
IMAGE_ROOTFS_ALIGNMENT = "64"
