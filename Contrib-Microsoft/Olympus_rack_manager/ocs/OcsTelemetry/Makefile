SRCDIR := 
BUILDDIR := obj/
LIBDIR := lib/
APPDIR := bin/
LIBSRCDIR := $(SRCDIR)
APPSRCDIR := $(SRCDIR)
INCDIR := $(LIBSRCDIR)
CREATEDIR := .create		

LIB_NAME := ocstelemetry_parse
LIB_SRCS := ocstelemetry_parse.c
LIB_STATIC :=
LIB_INC := $(wildcard $(LIBSRCDIR)*.h)
LIB_VERSION :=
LIB_DEPLIB := ocslock ocslog

APP_NAME := ocstelemetry_utility
APP_SRCS := ocstelemetry_utility.c
APP_DEPLIB := $(LIB_NAME)


include ../ocs.mk


# We need to build a second application for this module.
DAEMON_APP_NAME := ocstelemetry_daemon
DAEMON_APP_SRCS := ocstelemetry_daemon.c
DAEMON_APP_DEPLIB := zlog ocspru ocshdc ocshsc ocsblademap ocsgpio ocslock ocsprecheck ocsauth ocslog
DAEMON_APP_OBJS := $(addprefix $(BUILDDIR), $(DAEMON_APP_SRCS:%.c=%.o))
DAEMON_APP_DEPS := $(DAEMON_APP_OBJS:.o=.d)
DAEMON_APP_LINK := $(addprefix -l, $(DAEMON_APP_DEPLIB))
DAEMON_APP_OUT := $(APPDIR)$(DAEMON_APP_NAME)
APP_OUT_LIST += $(DAEMON_APP_OUT)

app: $(DAEMON_APP_OUT)

$(DAEMON_APP_OUT): $(APPDIR)$(CREATEDIR) $(DAEMON_APP_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -pthread -o $@ $(DAEMON_APP_OBJS) $(DAEMON_APP_LINK)

$(DAEMON_APP_OBJS): $(BUILDDIR)$(CREATEDIR)