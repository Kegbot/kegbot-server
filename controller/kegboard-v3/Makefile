TARGET = kegboard-v3
MCU = atmega168
F_CPU = 16000000
ARDUINO_LIBS = EEPROM

UNAME_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')

ifeq ($(UNAME_S), Linux)
ARDUINO_DIR ?= /usr/local/arduino
ARDUINO_PORT ?= /dev/cu.usb*
endif

ifeq ($(UNAME_S), Darwin)
ARDUINO_DIR ?= /Applications/arduino-0015
ARDUINO_PORT ?= /dev/ttyUSB0
endif

include Arduino.mk
