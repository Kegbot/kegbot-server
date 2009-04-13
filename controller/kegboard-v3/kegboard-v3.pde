// kegboard3 - v3.0.0
// Arduino implementation of Kegboard firmware.
//
// This firmware is intended for an Arduino Diecimila board (or similar)
// http://www.arduino.cc/en/Main/ArduinoBoardDiecimila
//
// This firmware implements the Kegboard Serial Protocol, version 1
// (KBSP v1). For more information on what that means, see the kegbot
// docs: http://kegbot.org/docs/
//
// You may change the pin configuration by editing kegboard_config.h; you should
// not need to change anything in this file.
//
// TODO:
//  - implement serial reading (relay on/off) commands
//  - get/set boardname with eeprom
//  - implement selftest mode
//  - Thermo:
//    * check CRC
//    * clean up code
//  - leak detect circuit/alarm support

#include "kegboard.h"
#include "kegboard_config.h"
#include "ds1820.h"
#include "KegboardPacket.h"

#include <util/crc16.h>

#ifdef KB_ENABLE_EEPROM
#include <EEPROM.h>
#endif

#ifdef KB_ENABLE_ONEWIRE
#include "OneWire.h"
#endif


//
// Config Globals -- defaults may be overridden by readEeprom()
//

int gBaudRate = KB_DEFAULT_BAUD_RATE;
char gBoardName[KB_BOARDNAME_MAXLEN+1] = KB_DEFAULT_BOARDNAME;
int gBoardNameLen = KB_DEFAULT_BOARDNAME_LEN;
int gUpdateInterval = KB_DEFAULT_UPDATE_INTERVAL;


//
// Other Globals
//

#ifdef KB_ENABLE_ONEWIRE
OneWire gThermoBusA(KB_PIN_THERMO_A);
OneWire gThermoBusB(KB_PIN_THERMO_B);
DS1820Sensor gThermoSensors[] = { DS1820Sensor(&gThermoBusA), DS1820Sensor(&gThermoBusA) };
#endif

unsigned long volatile gMeters[] = {0, 0};

static KegboardPacket gOutputPacket;

//
// EEPROM functions
//

#ifdef KB_ENABLE_EEPROM
int eepReadIntTag(byte off, int* val)
{
  int ret;
  ret = EEPROM.read(off++) << 8;
  ret |= EEPROM.read(off++) & 0xff;
  *val = ret;
  return off;
}

int eepWriteIntTag(byte off, byte tag, int val)
{
  EEPROM.write(off++, tag);
  EEPROM.write(off++, 2);
  EEPROM.write(off++, (val >> 8));
  EEPROM.write(off++, (val & 0xff));
  return off;
}

void eepReadBoardname(byte off, byte len)
{
  char tmpname[KB_BOARDNAME_MAXLEN];
  int i;
  int tmplen = 0;

  if (len > KB_BOARDNAME_MAXLEN)
    return;

  for (i=0; i<KB_BOARDNAME_MAXLEN && i < len; i++) {
    byte c = EEPROM.read(off+i);
    if (c == '\0')
      break;
    if (c < 'A' || c > 'z')
      return;
    tmpname[tmplen++] = c;
  }

  if (tmplen < 1)
    return;

  for (i=0; i<tmplen; i++)
    gBoardName[i] = tmpname[i];
  gBoardName[++i] = '\0';
  gBoardNameLen = tmplen;
}

int eepWriteBoardname(byte off)
{
  int i;
  if (gBoardNameLen <= 0)
    return off;

  EEPROM.write(off++, KB_EEP_TAG_BOARDNAME);
  EEPROM.write(off++, gBoardNameLen);
  for (i=0; i <= gBoardNameLen; i++)
    EEPROM.write(off++, gBoardName[i]);
  return off;
}

int eepReadBaudrate(byte off, byte len)
{
  if (len != 2)
    return -1;
  byte hi = EEPROM.read(off);
  byte low = EEPROM.read(off+1);
  int rate = (hi << 8) | (low & 0xff);

  switch (rate) {
    case 9600:
    case 19200:
    case 28800:
    case 57600:
    case 115200:
      gBaudRate = rate;
      break;
    default:
      return -1;
  }
}

int eepWriteBaudrate(byte off)
{
  return eepWriteIntTag(off, KB_EEP_TAG_BAUDRATE, gBaudRate);
}

int eepReadUpdateInterval(byte off, byte len)
{
  if (len != 2)
    return -1;
  byte hi = EEPROM.read(off);
  byte low = EEPROM.read(off+1);
  int rate = (hi << 8) | (low & 0xff);

  if (rate < KB_UPDATE_INTERVAL_MIN || rate > KB_UPDATE_INTERVAL_MAX)
    return -1;

  gUpdateInterval = rate;
}

int eepWriteUpdateInterval(byte off)
{
  return eepWriteIntTag(off, KB_EEP_TAG_UPDATE_INTERVAL, gUpdateInterval);
}

// readEeprom
// Reads a TLV-formatted eeprom, parsing known tags and ignoring others.
int readEeprom()
{
  byte tmp1, tmp2;
  int off=0;

  // Does this look like my EEPROM? First two bytes must match the magic values.
  tmp1 = EEPROM.read(off++);
  tmp2 = EEPROM.read(off++);
  if (tmp1 != KB_EEP_MAGIC_0 || tmp2 != KB_EEP_MAGIC_1)
    return -1;

  while (off < 512) {
    byte tag = EEPROM.read(off++);
    byte len = EEPROM.read(off++);

    switch (tag) {
      case KB_EEP_TAG_BOARDNAME:
        eepReadBoardname(off, len);
        break;
      case KB_EEP_TAG_BAUDRATE:
        eepReadBaudrate(off, len);
        break;
      case KB_EEP_TAG_UPDATE_INTERVAL:
        eepReadUpdateInterval(off, len);
        break;
      case KB_EEP_TAG_END:
        return 0;
    }
    off += len;
  }
  return 0;
}

int writeEeprom()
{
  int off=0;
  EEPROM.write(off++, KB_EEP_MAGIC_0);
  EEPROM.write(off++, KB_EEP_MAGIC_1);
  off = eepWriteBoardname(off);
  off = eepWriteBaudrate(off);
  off = eepWriteUpdateInterval(off);
  while (off < 512)
    EEPROM.write(KB_EEP_TAG_END, off++);
}
#endif // KB_ENABLE_EEPROM

//
// ISRs
//

void meterInterruptA()
{
  gMeters[0] += 1;
}

void meterInterruptB()
{
  gMeters[1] += 1;
}


//
// Main
//

void setup()
{
  pinMode(KB_PIN_METER_A, INPUT);
  pinMode(KB_PIN_METER_B, INPUT);

  // enable internal pullup to prevent disconnected line from ticking away
  digitalWrite(KB_PIN_METER_A, HIGH);
  digitalWrite(KB_PIN_METER_B, HIGH);

  attachInterrupt(0, meterInterruptA, RISING);
  attachInterrupt(1, meterInterruptB, RISING);

  pinMode(KB_PIN_RELAY_A, OUTPUT);
  pinMode(KB_PIN_RELAY_B, OUTPUT);

  pinMode(KB_PIN_TEST_PULSE, OUTPUT);

  Serial.begin(115200);

#ifdef KB_ENABLE_EEPROM
  readEeprom();
#endif
}

uint16_t genCrc(unsigned long val)
{
  uint16_t crc=0;
  int i=0;
  for (i=3;i>=0;i--)
    crc = _crc_xmodem_update(crc, (val >> (8*i)) & 0xff);
  return crc;
}

void writeOutputPacket()
{
  gOutputPacket.Print();
  gOutputPacket.Reset();
}

void writeHelloPacket()
{
  int foo = 0xef;
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_HELLO_ID);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_HELLO_TAG_PROTOCOL_VERSION, sizeof(foo), (char*)&foo);
  writeOutputPacket();
}

void writeThermoPacket(int channel)
{
  char name[] = "thermoX";
  long temp;

  name[6] = 0x30 + channel;
  temp = gThermoSensors[channel].GetTemp();

  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_THERMO_READING);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_NAME, 8, name);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_READING, sizeof(temp), (char*)(&temp));
  writeOutputPacket();
}

void writeRelayPacket(int channel)
{
  char name[] = "outputX";
  int status=0;
  name[6] = 0x30 + channel;
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_OUTPUT_STATUS);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_OUTPUT_STATUS_TAG_OUTPUT_NAME, 8, name);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_OUTPUT_STATUS_TAG_OUTPUT_READING, sizeof(status), (char*)(&status));
  writeOutputPacket();
}

void writeMeterPacket(int channel)
{
  char name[] = "flowX";
  unsigned long status = gMeters[channel];
  name[4] = 0x30 + channel;
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_METER_STATUS);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_NAME, 5, name);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_READING, sizeof(status), (char*)(&status));
  writeOutputPacket();
}

void doTestPulse()
{
  // Strobes the test pin 4 times.
  int i=0;
  for (i=0; i<4; i++) {
    digitalWrite(KB_PIN_TEST_PULSE, 1);
    digitalWrite(KB_PIN_TEST_PULSE, 0);
  }
}


void loop()
{
  writeHelloPacket();

  writeMeterPacket(0);
  writeMeterPacket(1);

  writeRelayPacket(0);
  writeRelayPacket(1);

#ifdef KB_ENABLE_ONEWIRE
  {
    unsigned long clock = millis();
    gThermoSensors[0].Update(clock);
    gThermoSensors[1].Update(clock);
  }
  writeThermoPacket(0);
  writeThermoPacket(1);
#endif

  doTestPulse();

  delay(gUpdateInterval);
}

// vim: syntax=c
