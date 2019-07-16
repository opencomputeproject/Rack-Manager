PREFIX ?= $(shell pwd)/build
LIB_INST ?= /usr/lib
INC_INST ?= /usr/include
BIN_INST ?= /usr/bin
PWD := $(shell pwd)/

UTILS_DIR := Utils
OCS_DIRS := $(notdir $(shell find . -maxdepth 1 -type d -not -name '.*' -not -name $(UTILS_DIR)))
EXTRA_INCLUDES := $(UTILS_DIR) ocsgpio/libocsgpio

ifneq ($(PC_INCLUDE),)
EXTRA_INCLUDES += $(UTILS_DIR)/pc_include
endif

RPATH_ARG := -Wl,-rpath-link=
OCS_INC = $(addprefix -I$(PWD)/, $(OCS_DIRS) $(EXTRA_INCLUDES))
OCS_LIB = $(addsuffix /lib, $(addprefix -L$(PWD)/, $(OCS_DIRS)))
OCS_RPATH = $(addsuffix /lib, $(addprefix $(RPATH_ARG)$(PWD)/, $(OCS_DIRS)))

OCS_CFLAGS = $(OCS_INC) $(CFLAGS)
OCS_LDFLAGS = $(OCS_LIB) $(OCS_RPATH) $(LDFLAGS)

ifneq ($(PC_DEBUG),)
OCS_CFLAGS += -DPC_DEBUG
endif

MAKE_ARGS = 'CFLAGS=$(OCS_CFLAGS)' 'LDFLAGS=$(OCS_LDFLAGS)'
BUILD_CMD = $(MAKE) $(MAKE_ARGS)
INST_ARGS := PREFIX=$(PREFIX) LIB_INST=$(LIB_INST) INC_INST=$(INC_INST) BIN_INST=$(BIN_INST)

OCS_BUILD := \
	ocslock \
	ocslog \
	ocsblademap \
	ocsfile \
	ocsauth \
	ocsprecheck \
	ocsi2c \
	ocscmdline \
	ocs-pmic \
	ocshsc \
	ocshdc \
	ocsswitch \
	ocspersist \
	ocspru \
	ocsgpio \
	ocstelemetry \
	ocsaudit \
	ocsinit \
	ocsfwupgrade \
	ocs-itp \
	runtimewatchdog \
	ocsfrui2c \
	ocsadc \
	ocs-fru \
	ocsmac


.PHONY: all
all: $(OCS_BUILD)

# Build rules for OCS libraries and applications.
.PHONY: ocslock
ocslock:
	$(BUILD_CMD) -C SemLock
	
.PHONY: ocslog
ocslog: ocslock
	$(BUILD_CMD) -C Ocslog
	
.PHONY: ocsblademap
ocsblademap: ocslog
	$(BUILD_CMD) -C BladeMap
	
.PHONY: ocsfile
ocsfile: ocslog ocslock
	$(BUILD_CMD) -C FileIntegrity
	
.PHONY: ocsauth
ocsauth: ocslog ocslock
	$(BUILD_CMD) -C security
	
.PHONY: ocsprecheck
ocsprecheck: ocslog ocsauth ocsgpio
	$(BUILD_CMD) -C Prechecks
	
.PHONY: ocsi2c
ocsi2c: ocslock ocslog
	$(BUILD_CMD) -C Ocsi2c
	
.PHONY: ocscmdline
ocscmdline:
	$(BUILD_CMD) -C CmdLine
	
.PHONY: ocs-pmic
ocs-pmic: ocslog ocsi2c ocscmdline
	$(BUILD_CMD) -C PMIC_TPS65218
	
.PHONY: ocshsc
ocshsc: ocslog ocsi2c ocscmdline
	$(BUILD_CMD) -C HSC_LM25066
	
.PHONY: ocshdc
ocshdc: ocslog ocsi2c ocscmdline
	$(BUILD_CMD) -C HDC1080
	
.PHONY: ocsswitch
ocsswitch: ocslog ocsblademap
	$(BUILD_CMD) -C Switch
	
.PHONY: ocspersist
ocspersist: ocslog ocslock
	$(BUILD_CMD) -C Persist
	
.PHONY: ocspru
ocspru: ocslog ocslock ocspersist ocscmdline
	$(BUILD_CMD) -C PRU
	
.PHONY: ocsgpio
ocsgpio: ocslog ocslock
	$(BUILD_CMD) -C ocsgpio
	
.PHONY: ocstelemetry
ocstelemetry: ocspru ocshdc ocshsc ocsblademap ocsgpio ocslock ocsprecheck ocsauth ocslog
	$(BUILD_CMD) -C OcsTelemetry
	
.PHONY: ocsaudit
ocsaudit: ocslog
	$(BUILD_CMD) -C OcsAudit
	
.PHONY: ocsinit
ocsinit: ocslog ocslock ocsfile
	$(BUILD_CMD) -C Init
	
.PHONY: ocsfwupgrade
ocsfwupgrade:
	$(BUILD_CMD) -C ocsfwup
	
.PHONY: ocs-itp
ocs-itp: ocslog ocsblademap ocsprecheck ocsgpio
	$(BUILD_CMD) -C RemoteITP
	
.PHONY: runtimewatchdog
runtimewatchdog: ocslog
	$(BUILD_CMD) -C Watchdog
	
.PHONY: ocsfrui2c
ocsfrui2c: ocslog
	$(BUILD_CMD) -C frui2clib
	
.PHONY: ocsadc
ocsadc: ocslog ocsfrui2c ocspru
	$(BUILD_CMD) -C adc-util
	
.PHONY: ocs-fru
ocs-fru: ocslog ocsfrui2c
	$(BUILD_CMD) -C fru-util
	
.PHONY: ocsmac
ocsmac: ocslog ocsfrui2c
	$(BUILD_CMD) -C mac-util


.PHONY: clean
clean:
	rm -rf build
	for ocs in $(OCS_DIRS); do \
		$(MAKE) -C $$ocs clean; \
	done

.PHONY: install
install:
	install -d $(PREFIX)/$(LIB_INST)
	install -d $(PREFIX)/$(INC_INST)
	install -d $(PREFIX)/$(BIN_INST)
	for ocs in $(OCS_DIRS); do \
		$(MAKE) $(INST_ARGS) -C $$ocs install; \
	done