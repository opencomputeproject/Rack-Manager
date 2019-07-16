SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create

LIB_NAME := ocslog
LIB_STATIC :=
LIB_SRCS := ocslog.c ocslog-shm.c
LIB_INC := $(wildcard $(LIBSRCDIR)*.h)
LIB_VERSION :=
LIB_DEPLIB := ocslock rt

APP_NAME := ocslog-daemon
APP_SRCS := ocslog-daemon.c
APP_DEPLIB := $(LIB_NAME) zlog


include ../ocs.mk