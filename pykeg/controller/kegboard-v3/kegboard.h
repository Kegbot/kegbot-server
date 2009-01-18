#include "HardwareSerial.h"

#define LOG(s) Serial.println(s);

#define KBSP_PREFIX           "kbsp v1 "
#define KB_BOARDNAME_MAXLEN   8

#define KB_EEP_MAGIC_0        0xba
#define KB_EEP_MAGIC_1        0xbe

#define KB_EEP_TAG_BOARDNAME       0x01
#define KB_EEP_TAG_BAUDRATE        0x02
#define KB_EEP_TAG_UPDATE_INTERVAL 0x03
#define KB_EEP_TAG_END             0xff

// Max freq 10Hz, Min freq 0.1Hz
#define KB_UPDATE_INTERVAL_MIN  100
#define KB_UPDATE_INTERVAL_MAX  10000
