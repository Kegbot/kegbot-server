########################################################################
# Kegbot Notice: This is a copy of the Arduino.mk Makefile for Arduino.
#       Version: 0.4
#        Source: http://mjo.tc/atelier/2009/02/arduino-cli.html
#       License: LGPL v2
# Local changes: None beyond this this comment block.
########################################################################
#
# Arduino command line tools Makefile
# System part (i.e. project independent)
#
# Copyright (C) 2010 Martin Oldfield <m@mjo.tc>, based on work that is
# Copyright Nicholas Zambetti, David A. Mellis & Hernando Barragan
# 
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# Adapted from Arduino 0011 Makefile by M J Oldfield
#
# Original Arduino adaptation by mellis, eighthave, oli.keller
#
# Version 0.1  17.ii.2009  M J Oldfield
#
#         0.2  22.ii.2009  M J Oldfield
#                          - fixes so that the Makefile actually works!
#                          - support for uploading via ISP
#                          - orthogonal choices of using the Arduino for
#                            tools, libraries and uploading
#
#         0.3  21.v.2010   M J Oldfield
#                          - added proper license statement
#                          - added code from Philip Hands to reset
#                            Arduino prior to upload
#
#         0.4  25.v.2010   M J Oldfield
#                          - tweaked reset target on Philip Hands' advice
#
########################################################################
#
# STANDARD ARDUINO WORKFLOW
#
# Given a normal sketch directory, all you need to do is to create
# a small Makefile which defines a few things, and then includes this one.
#
# For example:
#
#       ARDUINO_DIR  = /Applications/arduino-0013
#
#       TARGET       = CLItest
#       ARDUINO_LIBS = LiquidCrystal
#
#       MCU          = atmega168
#       F_CPU        = 16000000
#       ARDUINO_PORT = /dev/cu.usb*
#
#       include /usr/local/share/Arduino.mk
#
# Hopefully these will be self-explanatory but in case they're not:
#
#    ARDUINO_DIR  - Where the Arduino software has been unpacked
#    TARGET       - The basename used for the final files. Canonically
#                   this would match the .pde file, but it's not needed
#                   here: you could always set it to xx if you wanted!
#    ARDUINO_LIBS - A list of any libraries used by the sketch (we assume
#                   these are in $(ARDUINO_DIR)/hardware/libraries
#    MCU,F_CPU    - The target processor description
#    ARDUINO_PORT - The port where the Arduino can be found (only needed
#                   when uploading
#
# Once this file has been created the typical workflow is just
#
#   $ make upload
#
# All of the object files are created in the build-cli subdirectory
# All sources should be in the current directory and can include:
#  - at most one .pde file which will be treated as C++ after the standard
#    Arduino header and footer have been affixed.
#  - any number of .c, .cpp, .s and .h files
#
#
# Besides make upload you can also
#   make            - no upload
#   make clean      - remove all our dependencies
#   make depends    - update dependencies
#   make reset      - reset the Arduino by tickling DTR on the serial port
#   make raw_upload - upload without first resetting
#
########################################################################
#
# ARDUINO WITH OTHER TOOLS
#
# If the tools aren't in the Arduino distribution, then you need to 
# specify their location:
#
#    AVR_TOOLS_PATH = /usr/bin
#    AVRDUDE_CONF   = /etc/avrdude/avrdude.conf
#
########################################################################
#
# ARDUINO WITH ISP
#
# You need to specify some details of your ISP programmer and might
# also need to specify the fuse values:
#
#     ISP_PROG	   = -c stk500v2
#     ISP_PORT     = /dev/ttyACM0
#     
#     ISP_LOCK_FUSE_PRE  = 0x3f
#     ISP_LOCK_FUSE_POST = 0xcf
#     ISP_HIGH_FUSE      = 0xdf
#     ISP_LOW_FUSE       = 0xff
#     ISP_EXT_FUSE       = 0x01
#
# I think the fuses here are fine for uploading to the ATmega168
# without bootloader.
# 
# To actually do this upload use the ispload target:
#
#    make ispload
#
#
########################################################################
# Some paths
#

ifneq (ARDUINO_DIR,)

ifndef AVR_TOOLS_PATH
AVR_TOOLS_PATH    = $(ARDUINO_DIR)/hardware/tools/avr/bin
endif

ifndef ARDUINO_ETC_PATH
ARDUINO_ETC_PATH  = $(ARDUINO_DIR)/hardware/tools/avr/etc
endif

ifndef AVRDUDE_CONF
AVRDUDE_CONF     = $(ARDUINO_ETC_PATH)/avrdude.conf
endif

ARDUINO_LIB_PATH  = $(ARDUINO_DIR)/hardware/libraries
ARDUINO_CORE_PATH = $(ARDUINO_DIR)/hardware/arduino/cores/arduino

endif

# Everything gets built in here
OBJDIR  	  = build-cli

########################################################################
# Local sources
#
LOCAL_C_SRCS    = $(wildcard *.c)
LOCAL_CPP_SRCS  = $(wildcard *.cpp)
LOCAL_CC_SRCS   = $(wildcard *.cc)
LOCAL_PDE_SRCS  = $(wildcard *.pde)
LOCAL_AS_SRCS   = $(wildcard *.S)
LOCAL_OBJ_FILES = $(LOCAL_C_SRCS:.c=.o) $(LOCAL_CPP_SRCS:.cpp=.o) \
		$(LOCAL_CC_SRCS:.cc=.o) $(LOCAL_PDE_SRCS:.pde=.o) \
		$(LOCAL_AS_SRCS:.S=.o)
LOCAL_OBJS      = $(patsubst %,$(OBJDIR)/%,$(LOCAL_OBJ_FILES))

# Dependency files
DEPS            = $(LOCAL_OBJS:.o=.d)

# core sources
ifeq ($(strip $(NO_CORE)),)
ifdef ARDUINO_CORE_PATH
CORE_C_SRCS     = $(wildcard $(ARDUINO_CORE_PATH)/*.c)
CORE_CPP_SRCS   = $(wildcard $(ARDUINO_CORE_PATH)/*.cpp)
CORE_OBJ_FILES  = $(CORE_C_SRCS:.c=.o) $(CORE_CPP_SRCS:.cpp=.o)
CORE_OBJS       = $(patsubst $(ARDUINO_CORE_PATH)/%,  \
			$(OBJDIR)/%,$(CORE_OBJ_FILES))
endif
endif

# all the objects!
OBJS            = $(LOCAL_OBJS) $(CORE_OBJS)

########################################################################
# Rules for making stuff
#

# The name of the main targets
TARGET_HEX = $(OBJDIR)/$(TARGET).hex
TARGET_ELF = $(OBJDIR)/$(TARGET).elf
TARGETS    = $(OBJDIR)/$(TARGET).*

# A list of dependencies
DEP_FILE   = $(OBJDIR)/depends.mk

# Names of executables
CC      = $(AVR_TOOLS_PATH)/avr-gcc
CXX     = $(AVR_TOOLS_PATH)/avr-g++
OBJCOPY = $(AVR_TOOLS_PATH)/avr-objcopy
OBJDUMP = $(AVR_TOOLS_PATH)/avr-objdump
AR      = $(AVR_TOOLS_PATH)/avr-ar
SIZE    = $(AVR_TOOLS_PATH)/avr-size
NM      = $(AVR_TOOLS_PATH)/avr-nm
REMOVE  = rm -f
MV      = mv -f
CAT     = cat
ECHO    = echo

# General arguments
SYS_LIBS      = $(patsubst %,$(ARDUINO_LIB_PATH)/%,$(ARDUINO_LIBS))
SYS_INCLUDES  = $(patsubst %,-I%,$(SYS_LIBS))
SYS_OBJS      = $(wildcard $(patsubst %,%/*.o,$(SYS_LIBS)))

CPPFLAGS = \
  -mmcu=$(MCU) \
  -DF_CPU=$(F_CPU) \
  -I. \
  -I$(ARDUINO_CORE_PATH) \
  $(SYS_INCLUDES) \
  -g \
  -Os \
  -w \
  -Wall \
  -ffunction-sections \
  -fdata-sections
CFLAGS        = -std=gnu99
CXXFLAGS      = -fno-exceptions
ASFLAGS       = -mmcu=$(MCU) -I. -x assembler-with-cpp
LDFLAGS       = -mmcu=$(MCU) -lm -Wl,--gc-sections -Os

# Rules for making a CPP file from the main sketch (.cpe)
PDEHEADER     = \\\#include \"WProgram.h\"

# Expand and pick the first port
ARD_PORT      = $(firstword $(wildcard $(ARDUINO_PORT)))

# Implicit rules for building everything (needed to get everything in
# the right directory)
#
# Rather than mess around with VPATH there are quasi-duplicate rules
# here for building e.g. a system C++ file and a local C++
# file. Besides making things simpler now, this would also make it
# easy to change the build options in future

# normal local sources
# .o rules are for objects, .d for dependency tracking
# there seems to be an awful lot of duplication here!!!
$(OBJDIR)/%.o: %.c
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

$(OBJDIR)/%.o: %.cc
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@

$(OBJDIR)/%.o: %.cpp
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@

$(OBJDIR)/%.o: %.S
	$(CC) -c $(CPPFLAGS) $(ASFLAGS) $< -o $@

$(OBJDIR)/%.o: %.s
	$(CC) -c $(CPPFLAGS) $(ASFLAGS) $< -o $@

$(OBJDIR)/%.d: %.c
	$(CC) -MM $(CPPFLAGS) $(CFLAGS) $< -MF $@ -MT $(@:.d=.o)

$(OBJDIR)/%.d: %.cc
	$(CXX) -MM $(CPPFLAGS) $(CXXFLAGS) $< -MF $@ -MT $(@:.d=.o)

$(OBJDIR)/%.d: %.cpp
	$(CXX) -MM $(CPPFLAGS) $(CXXFLAGS) $< -MF $@ -MT $(@:.d=.o)

$(OBJDIR)/%.d: %.S
	$(CC) -MM $(CPPFLAGS) $(ASFLAGS) $< -MF $@ -MT $(@:.d=.o)

$(OBJDIR)/%.d: %.s
	$(CC) -MM $(CPPFLAGS) $(ASFLAGS) $< -MF $@ -MT $(@:.d=.o)

# the pde -> cpp -> o file
$(OBJDIR)/%.cpp: %.pde
	$(ECHO) $(PDEHEADER) > $@
	$(CAT)  $< >> $@

$(OBJDIR)/%.o: $(OBJDIR)/%.cpp
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@

$(OBJDIR)/%.d: $(OBJDIR)/%.cpp
	$(CXX) -MM $(CPPFLAGS) $(CXXFLAGS) $< -MF $@ -MT $(@:.d=.o)

# core files
$(OBJDIR)/%.o: $(ARDUINO_CORE_PATH)/%.c
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

$(OBJDIR)/%.o: $(ARDUINO_CORE_PATH)/%.cpp
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@

# various object conversions
$(OBJDIR)/%.hex: $(OBJDIR)/%.elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

$(OBJDIR)/%.eep: $(OBJDIR)/%.elf
	-$(OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" \
		--change-section-lma .eeprom=0 -O ihex $< $@

$(OBJDIR)/%.lss: $(OBJDIR)/%.elf
	$(OBJDUMP) -h -S $< > $@

$(OBJDIR)/%.sym: $(OBJDIR)/%.elf
	$(NM) -n $< > $@

########################################################################
#
# Avrdude
#
ifndef AVRDUDE
AVRDUDE          = $(AVR_TOOLS_PATH)/avrdude
endif

AVRDUDE_COM_OPTS = -q -V -p $(MCU)
ifdef AVRDUDE_CONF
AVRDUDE_COM_OPTS += -C $(AVRDUDE_CONF)
endif

ifndef AVRDUDE_ARD_PROGRAMMER
AVRDUDE_ARD_PROGRAMMER = stk500v1
endif

ifndef AVRDUDE_ARD_BAUDRATE
AVRDUDE_ARD_BAUDRATE   = 19200
endif

AVRDUDE_ARD_OPTS = -c $(AVRDUDE_ARD_PROGRAMMER) -b $(AVRDUDE_ARD_BAUDRATE) -P $(ARD_PORT)

ifndef ISP_LOCK_FUSE_PRE
ISP_LOCK_FUSE_PRE  = 0x3f
endif

ifndef ISP_LOCK_FUSE_POST
ISP_LOCK_FUSE_POST = 0xcf
endif

ifndef ISP_HIGH_FUSE
ISP_HIGH_FUSE      = 0xdf
endif

ifndef ISP_LOW_FUSE
ISP_LOW_FUSE       = 0xff
endif

ifndef ISP_EXT_FUSE
ISP_EXT_FUSE       = 0x01
endif

ifndef ISP_PROG
ISP_PROG	   = -c stk500v2
endif

AVRDUDE_ISP_OPTS = -P $(ISP_PORT) $(ISP_PROG)


########################################################################
#
# Explicit targets start here
#

all: 		$(OBJDIR) $(TARGET_HEX)

$(OBJDIR):
		mkdir $(OBJDIR)

$(TARGET_ELF): 	$(OBJS)
		$(CC) $(LDFLAGS) -o $@ $(OBJS) $(SYS_OBJS)

$(DEP_FILE):	$(OBJDIR) $(DEPS)
		cat $(DEPS) > $(DEP_FILE)

upload:		reset raw_upload

raw_upload:	$(TARGET_HEX)
		$(AVRDUDE) $(AVRDUDE_COM_OPTS) $(AVRDUDE_ARD_OPTS) \
			-U flash:w:$(TARGET_HEX):i

# stty on MacOS likes -F, but on Debian it likes -f redirecting
# stdin/out appears to work but generates a spurious error on MacOS at
# least. Perhaps it would be better to just do it in perl ?
reset:		
		for STTYF in 'stty --file' 'stty -f' 'stty <' ; \
		  do $$STTYF /dev/tty >/dev/null 2>/dev/null && break ; \
		done ;\
		$$STTYF $(ARD_PORT)  hupcl ;\
		(sleep 0.1 || sleep 1)     ;\
		$$STTYF $(ARD_PORT) -hupcl 

ispload:	$(TARGET_HEX)
		$(AVRDUDE) $(AVRDUDE_COM_OPTS) $(AVRDUDE_ISP_OPTS) -e \
			-U lock:w:$(ISP_LOCK_FUSE_PRE):m \
			-U hfuse:w:$(ISP_HIGH_FUSE):m \
			-U lfuse:w:$(ISP_LOW_FUSE):m \
			-U efuse:w:$(ISP_EXT_FUSE):m
		$(AVRDUDE) $(AVRDUDE_COM_OPTS) $(AVRDUDE_ISP_OPTS) -D \
			-U flash:w:$(TARGET_HEX):i
		$(AVRDUDE) $(AVRDUDE_COM_OPTS) $(AVRDUDE_ISP_OPTS) \
			-U lock:w:$(ISP_LOCK_FUSE_POST):m

clean:
		$(REMOVE) $(OBJS) $(TARGETS) $(DEP_FILE) $(DEPS)

depends:	$(DEPS)
		cat $(DEPS) > $(DEP_FILE)

.PHONY:	all clean depends upload raw_upload reset

include $(DEP_FILE)
