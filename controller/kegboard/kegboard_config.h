//
// Feature configuration
//

// You may enable/disable kegboard features here as desired. The deafult are
// safe.

// Check for & report 1-wire temperature sensors?
#define KB_ENABLE_ONEWIRE_THERMO   1

// Check for & report 1-wire devices on the ID bus?
#define KB_ENABLE_ONEWIRE_PRESENCE 1

// Enable a selftest pulse?
#define KB_ENABLE_SELFTEST  1

// Enable buzzer?
#define KB_ENABLE_BUZZER    1

// Enable ID-12 RFID?
#define KB_ENABLE_ID12_RFID 1

// Enable MagStripe reader?
#define KB_ENABLE_MAGSTRIPE 0

//
// Pin configuration - KEGBOARD VERSION
//

// You may change values in this section if you know what you are doing --
// though you ordinarily shouldn't need to change these.
//
//  Digital pin allocation:
//    2 - flowmeter 0 pulse (input)
//    3 - flowmeter 1 pulse (input)
//    4 - flow 0 LED (output)
//    5 - flow 1 LED (output)
//    6 - rfid (input from ID-12)
//    7 - thermo onewire bus (1-wire, input/output)
//    8 - presence onewire bus (1-wire, input/output)
//    9 - gpio pin C
//   10 - rfid reset
//   11 - buzzer (output)
//   12 - test pulse train (output)
//   13 - alarm (output)
//  Analog pin allocation:
//   A0 - relay 0 control (output)
//   A1 - relay 1 control (output)
//   A2 - relay 2 control (output)
//   A3 - relay 3 control (output)
//   A4 - gpio pin A
//   A5 - gpio pin B
//

#define KB_PIN_METER_A            2
#define KB_PIN_METER_B            3
#define KB_PIN_LED_FLOW_A         4
#define KB_PIN_LED_FLOW_B         5
#define KB_PIN_SERIAL_RFID_RX     6
#define KB_PIN_ONEWIRE_THERMO     7
#define KB_PIN_ONEWIRE_PRESENCE   8
#define KB_PIN_GPIO_C             9
#define KB_PIN_RFID_RESET         10
#define KB_PIN_BUZZER             11
#define KB_PIN_TEST_PULSE         12
#define KB_PIN_ALARM              13
#define KB_PIN_RELAY_A            A0
#define KB_PIN_RELAY_B            A1
#define KB_PIN_RELAY_C            A2
#define KB_PIN_RELAY_D            A3
#define KB_PIN_GPIO_A             A4
#define KB_PIN_GPIO_B             A5


#define KB_PIN_MAGSTRIPE_CLOCK    3
#define KB_PIN_MAGSTRIPE_DATA     A4
#define KB_PIN_MAGSTRIPE_CARD_PRESENT A5

// Atmega1280 (aka Arduino mega) section
#ifdef __AVR_ATmega1280__
#define KB_ATMEGA_1280            1
#define KB_NUM_METERS             6

#define KB_PIN_METER_C            21
#define KB_PIN_METER_D            20
#define KB_PIN_METER_E            19
#define KB_PIN_METER_F            18
#else
#define KB_NUM_METERS             2
#endif

//
// Device configuration defaults
//

#define KB_DEFAULT_BOARDNAME          "kegboard"
#define KB_DEFAULT_BOARDNAME_LEN      8  // must match #chars above
#define KB_DEFAULT_BAUD_RATE          115200

// Size in entries of the onewire presence bus cache.  This many IDs can be
// concurrently tracked on the bus.
#define ONEWIRE_CACHE_SIZE 8

// Number of full onewire bus searches to complete before considering a
// non-responding onewire id missing.  This is used to dampen against glitches
// where a device might be absent from a search.
#define ONEWIRE_CACHE_MAX_MISSING_SEARCHES 4
