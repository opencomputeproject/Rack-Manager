SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocshdc
LIB_STATIC :=
LIB_SRCS := hdc-lib.c
LIB_INC := hdc-lib.h
LIB_VERSION :=
LIB_DEPLIB := ocslog ocsi2c rt

APP_NAME := ocs-hdc
APP_SRCS := hdc-util.c
APP_DEPLIB := $(LIB_NAME) ocscmdline ocslog


include ../ocs.mk