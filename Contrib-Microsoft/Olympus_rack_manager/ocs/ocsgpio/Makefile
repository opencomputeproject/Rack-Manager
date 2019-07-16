SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)libocsgpio/
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR) kernelmod/ include/
CREATEDIR := .create

LIB_NAME := ocsgpio
LIB_STATIC :=
LIB_SRCS := $(wildcard $(LIBSRCDIR)*.c)
LIB_INC := $(wildcard $(LIBSRCDIR)*.h)
LIB_VERSION := $(LIBSRCDIR)ocsgpioaccess.h
LIB_DEPLIB := ocslock ocslog

APP_NAME := ocs-gpio
APP_SRCS := $(wildcard $(APPSRCDIR)*.c)
APP_DEPLIB := $(LIB_NAME) ocslog


include ../ocs.mk