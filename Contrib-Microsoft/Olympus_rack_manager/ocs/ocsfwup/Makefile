SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)libocsfwupgrade/
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR) include/ ./
CREATEDIR := .create

LIB_NAME := ocsfwupgrade
LIB_STATIC :=
LIB_SRCS := $(wildcard $(LIBSRCDIR)*.c)
LIB_INC := $(wildcard $(LIBSRCDIR)*.h)
LIB_VERSION := $(LIBSRCDIR)ocsfwupgrade.h
LIB_DEPLIB :=

APP_NAME := ocs-fwup
APP_SRCS := $(wildcard $(APPSRCDIR)*.c)
APP_DEPLIB := $(LIB_NAME)


include ../ocs.mk