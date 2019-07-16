SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocshsc
LIB_STATIC :=
LIB_SRCS := hsc-lib.c
LIB_INC := hsc-lib.h
LIB_VERSION :=
LIB_DEPLIB := ocslog ocsi2c rt m

APP_NAME := ocs-hsc
APP_SRCS := hsc-util.c
APP_DEPLIB := $(LIB_NAME) ocscmdline ocslog


include ../ocs.mk