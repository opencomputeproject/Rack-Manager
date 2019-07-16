SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocsmac
LIB_STATIC :=
LIB_SRCS := mac-lib.c
LIB_INC := mac-lib.h
LIB_VERSION :=
LIB_DEPLIB := ocsfrui2c ocslog

APP_NAME := ocs-mac
APP_SRCS := mac-util.c
APP_DEPLIB := $(LIB_NAME) ocslog


include ../ocs.mk