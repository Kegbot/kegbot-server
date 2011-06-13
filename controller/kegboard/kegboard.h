#include "HardwareSerial.h"

#define LOG(s) Serial.println(s);

#define KB_BOARDNAME_MAXLEN   8

#define KBM_HELLO_ID      0x01
#define KBM_HELLO_TAG_PROTOCOL_VERSION  0x01
#define KBM_HELLO_TAG_FIRMWARE_VERSION  0x01

#define KBM_THERMO_READING 0x11
#define KBM_THERMO_READING_TAG_SENSOR_NAME  0x01
#define KBM_THERMO_READING_TAG_SENSOR_READING  0x02

#define KBM_METER_STATUS 0x10
#define KBM_METER_STATUS_TAG_METER_NAME  0x01
#define KBM_METER_STATUS_TAG_METER_READING  0x02

#define KBM_OUTPUT_STATUS 0x12
#define KBM_OUTPUT_STATUS_TAG_OUTPUT_NAME  0x01
#define KBM_OUTPUT_STATUS_TAG_OUTPUT_READING  0x02

#define KBM_ONEWIRE_PRESENCE 0x13
#define KBM_ONEWIRE_PRESENCE_TAG_DEVICE_ID  0x01
#define KBM_ONEWIRE_PRESENCE_TAG_STATUS 0x02

#define KBM_AUTH_TOKEN 0x14
#define KBM_AUTH_TOKEN_TAG_DEVICE 0x01
#define KBM_AUTH_TOKEN_TAG_TOKEN 0x02
#define KBM_AUTH_TOKEN_TAG_STATUS 0x03

#define KBM_PING 0x81

#define KBM_SET_OUTPUT 0x84
#define KBM_SET_OUTPUT_TAG_OUTPUT_ID 0x01
#define KBM_SET_OUTPUT_TAG_OUTPUT_MODE 0x02

#define OUTPUT_DISABLED 0
#define OUTPUT_ENABLED 1

#define KBSP_PREFIX "KBSP v1:"
#define KBSP_PREFIX_CRC 0xe3af
#define KBSP_TRAILER "\r\n"

#define KBSP_HEADER_LEN 12
#define KBSP_HEADER_PREFIX_LEN 8
#define KBSP_HEADER_ID_LEN 2
#define KBSP_HEADER_PAYLOADLEN_LEN 2

#define KBSP_FOOTER_LEN 4
#define KBSP_FOOTER_CRC_LEN 2
#define KBSP_FOOTER_TRAILER_LEN 2

#define KBSP_PAYLOAD_MAXLEN 112

// Milliseconds/day
#define MS_PER_DAY  (1000*60*60*24)
// Interval between test pulse trains
#define KB_SELFTEST_INTERVAL_MS 500

// Number of pulses per test pulse train
#define KB_SELFTEST_PULSES 10

// Minimum time, in MS, between meter update packets. Setting this to zero will
// cause the kegboard to send a meter update message for nearly every tick; this
// is not recommended.
#define KB_METER_UPDATE_INTERVAL_MS 100

// Number of relay outputs
#define KB_NUM_RELAY_OUTPUTS 6

// Maximum time a relay will remain enabled after a "set_output" command.  The
// timer is reset whenenver a new "set_output" command is received.
#define KB_RELAY_WATCHDOG_MS 10000

// RFID defines
#define STX 0x02
#define ETX 0x03
#define RFID_DATA_CHARS 10
#define RFID_CHECKSUM_CHARS 2
#define RFID_PAYLOAD_CHARS 12
#define CR '\r'
#define LF '\n'
