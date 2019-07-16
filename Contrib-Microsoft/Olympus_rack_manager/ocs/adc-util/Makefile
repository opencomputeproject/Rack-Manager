SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)adc-lib/
APPSRCDIR := $(SRCDIR)adc-util/
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocsadc
LIB_STATIC :=
LIB_SRCS := $(wildcard $(LIBSRCDIR)*.c)
LIB_INC := $(wildcard $(LIBSRCDIR)*.h)
LIB_VERSION :=
LIB_DEPLIB := ocsfrui2c ocslog

APP_NAME := ocs-adccalibration
APP_SRCS := $(wildcard $(APPSRCDIR)*.c)
APP_DEPLIB := $(LIB_NAME) ocslog ocspru


include ../ocs.mk