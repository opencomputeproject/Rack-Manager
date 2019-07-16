msocs_do_install() {
    oe_runmake 'PREFIX=${D}' 'LIB_INST=${libdir}' 'INC_INST=${includedir}' 'BIN_INST=${bindir}' install
}

EXPORT_FUNCTIONS do_install