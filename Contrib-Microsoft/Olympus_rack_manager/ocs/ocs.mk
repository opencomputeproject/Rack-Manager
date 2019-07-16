LIB_OBJS := $(addprefix $(BUILDDIR), $(LIB_SRCS:%.c=%.o))
LIB_DEPS := $(LIB_OBJS:.o=.d)
LIB_LINK := $(addprefix -l, $(LIB_DEPLIB))
ifeq ($(LIB_STATIC),)
LIB_TYPE := .so
ifneq ($(LIB_VERSION),)
LIB_MAJOR := $(shell cat $(LIB_VERSION) | grep SOLIB_VERSION_MAJOR | awk '{print $$3}')
LIB_MINOR := $(shell cat $(LIB_VERSION) | grep SOLIB_VERSION_MINOR | awk '{print $$3}')
LIB_EXT := .$(LIB_MAJOR).$(LIB_MINOR)
LIB_BUILD := symlinks
endif
else
LIB_TYPE := .a
endif
ifneq ($(LIB_NAME),)
LIB_FILE := lib$(LIB_NAME)$(LIB_TYPE)
LIB_BASE := $(LIBDIR)$(LIB_FILE)
LIB_OUT := $(LIB_BASE)$(LIB_EXT)
LIB_SHARED_TARGET := $(subst $(LIB_TYPE),.so,$(LIB_OUT))
LIB_STATIC_TARGET := $(subst $(LIB_TYPE),.a,$(LIB_OUT))
SONAME := $(LIB_FILE)$(LIB_EXT)
ifneq ($(LIB_EXT),)
LIB_SYMLINKS := $(LIB_FILE) $(LIB_FILE).$(LIB_MAJOR)
endif
INSTALL += libinstall
endif

APP_OBJS := $(addprefix $(BUILDDIR), $(APP_SRCS:%.c=%.o))
APP_DEPS := $(APP_OBJS:.o=.d)
APP_LINK := $(addprefix -l, $(APP_DEPLIB))
ifneq ($(APP_NAME),)
APP_OUT := $(APPDIR)$(APP_NAME)
APP_OUT_LIST += $(APP_OUT)
INSTALL += appinstall
endif

override CFLAGS += -g -Wall -Wextra
override LDFLAGS += -L$(LIBDIR)

ifneq ($(INCDIR),)
LOCAL_INC := $(addprefix -I, $(INCDIR))
override CFLAGS := $(LOCAL_INC) $(CFLAGS)
endif


# Default build rule, which must preceed the dependency inclusion
.PHONY: all lib app
all: lib app
lib: $(LIB_OUT) $(LIB_BUILD)
app: $(APP_OUT)

-include $(LIB_DEPS)
-include $(APP_DEPS)


$(LIB_SHARED_TARGET): $(LIBDIR)$(CREATEDIR) $(LIB_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -pthread -Wl,-soname,$(SONAME) -o $@ $(LIB_OBJS) $(LIB_LINK)
	
.PHONY: symlinks
symlinks: $(LIB_OUT)
	for f in $(LIB_SYMLINKS); do \
		ln -sf $(LIB_FILE)$(LIB_EXT) $(LIBDIR)$$f; \
	done
	
$(LIB_STATIC_TARGET): $(LIBDIR)$(CREATEDIR) $(LIB_OBJS)
	$(AR) rcs $@ $(LIB_OBJS)

$(APP_OUT): $(APPDIR)$(CREATEDIR) $(APP_OBJS) lib
	$(CC) $(CFLAGS) $(LDFLAGS) -pthread -o $@ $(APP_OBJS) $(APP_LINK)


.PHONY: clean
clean:
	rm -rf $(BUILDDIR) $(LIBDIR) $(APPDIR)
	
$(BUILDDIR)%.o: %.c
	$(CC) $(CFLAGS) -c -fPIC -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o $@ $<

$(LIB_OBJS): $(BUILDDIR)$(LIBSRCDIR)$(CREATEDIR)
$(APP_OBJS): $(BUILDDIR)$(APPSRCDIR)$(CREATEDIR)

.PRECIOUS: %/$(CREATEDIR)
%/$(CREATEDIR):
	mkdir -p $(@D)
	touch $@
	
	
# Protect against accidentially installing in the main system path.  This action can be forced by
# specifying a PREFIX of '/'.
PREFIX ?= $(shell pwd)

LIB_INST ?= /usr/lib
INC_INST ?= /usr/include
BIN_INST ?= /usr/bin
	
.PHONY: install libinstall appinstall
install: $(INSTALL)

libinstall:
	install -d $(PREFIX)/$(LIB_INST)
	install -m 0755 $(LIB_OUT) $(PREFIX)/$(LIB_INST)
	for f in $(LIB_SYMLINKS); do \
		ln -sf $(LIB_FILE)$(LIB_EXT) $(PREFIX)/$(LIB_INST)/$$f; \
	done
	
	install -d $(PREFIX)/$(INC_INST)
	for f in $(LIB_INC); do \
		install -m 0644 $$f $(PREFIX)/$(INC_INST); \
	done
	
appinstall:
	install -d $(PREFIX)/$(BIN_INST)
	for f in $(APP_OUT_LIST); do \
		install -m 0755 $$f $(PREFIX)/$(BIN_INST); \
	done