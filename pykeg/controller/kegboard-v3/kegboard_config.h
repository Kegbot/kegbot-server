// Feature configuration
//
// You may enable/disable kegboard features here as desired. The deafult are
// safe.

// Check for & report 1-wire temperature sensors?
#define KB_ENABLE_ONEWIRE   1

// Use the built-in EEPROM for loading/saving the board config?
#define KB_ENABLE_EEPROM    1

// Pin configuration
//
// You may change values in this section if you know what you are doing --
// though you ordinarily shouldn't need to change these.

#define KB_PIN_METER_A      2
#define KB_PIN_METER_B      3
#define KB_PIN_RELAY_A      4
#define KB_PIN_RELAY_B      5
#define KB_PIN_THERMO_A     7
#define KB_PIN_THERMO_B     8
#define KB_PIN_SELFTEST     12

// Default values

#define KB_DEFAULT_BOARDNAME          "kegboard"
#define KB_DEFAULT_BOARDNAME_LEN      8  // must match #chars above
#define KB_DEFAULT_UPDATE_INTERVAL    500
#define KB_DEFAULT_BAUD_RATE          115200
