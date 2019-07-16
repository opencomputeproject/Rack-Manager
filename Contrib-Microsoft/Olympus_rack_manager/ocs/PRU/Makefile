SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocspru
LIB_STATIC :=
LIB_SRCS := pru-lib.c
LIB_INC := pru-lib.h pru-rpmsg.h
LIB_VERSION :=
LIB_DEPLIB := ocslog ocslock ocspersist m

APP_NAME := ocs-pru
APP_SRCS := pru-util.c
APP_DEPLIB := $(LIB_NAME) ocscmdline ocslog


include ../ocs.mk