/**
 * kegboard.pde - Kegboard v3 Arduino project
 * Copyright 2003-2009 Mike Wakerly <opensource@hoho.com>
 *
 * This file is part of the Kegbot package of the Kegbot project.
 * For more information on Kegbot, see http://kegbot.org/
 *
 * Kegbot is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Kegbot is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Kegbot.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * This firmware is intended for an Arduino Diecimila board (or similar)
 * http://www.arduino.cc/en/Main/ArduinoBoardDiecimila
 *
 * This firmware implements the Kegboard Serial Protocol, version 1 (KBSP v1).
 * For more information on what that means, see the kegbot docs:
 * http://kegbot.org/docs/
 *
 * You may change the pin configuration by editing kegboard_config.h; you should
 * not need to change anything in this file.
 *
 * TODO:
 *  - implement serial reading (relay on/off) commands
 *  - get/set boardname with eeprom
 *  - Thermo:
 *    * check CRC
 *    * clean up code
 *  - leak detect circuit/alarm support
 */

#include "kegboard.h"
#include "kegboard_config.h"
#include "ds1820.h"
#include "KegboardPacket.h"
#include <util/delay.h>

#include <util/crc16.h>

#if (KB_ENABLE_ONEWIRE_THERMO || KB_ENABLE_ONEWIRE_PRESENCE)
#include "OneWire.h"
#endif

#if KB_ENABLE_BUZZER
#include "buzzer.h"
#endif


//
// Config Globals
//

static int gBaudRate = KB_DEFAULT_BAUD_RATE;
static char gBoardName[KB_BOARDNAME_MAXLEN+1] = KB_DEFAULT_BOARDNAME;
static int gBoardNameLen = KB_DEFAULT_BOARDNAME_LEN;
static int gUpdateInterval = KB_DEFAULT_UPDATE_INTERVAL;


//
// Other Globals
//

// Up to 6 meters supported if using Arduino Mega
static unsigned long volatile gMeters[] = {0, 0, 0, 0, 0, 0};
static unsigned long volatile gLastMeters[] = {0, 0, 0, 0, 0, 0};
static KegboardPacket gOutputPacket;

#if KB_ENABLE_BUZZER
struct MelodyNote BOOT_MELODY[] = {
  {4, 3, 100}, {0, -1, 100},
  {4, 3, 70}, {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},

  {4, 0, 100}, {0, -1, 25},
  {4, 0, 100}, {0, -1, 25},
  {4, 0, 100}, {0, -1, 25},

  {4, 3, 100}, {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},
  {4, 3, 200},

  {-1, -1, -1},
};

struct MelodyNote ALARM_MELODY[] = {
  {3, 1, 500}, {5, 1, 500},
  {-1, -1, -1},
};
#endif

#if KB_ENABLE_ONEWIRE_THERMO
static OneWire gOnewireThermoBus(KB_PIN_ONEWIRE_THERMO);
static DS1820Sensor gThermoSensor;
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
static OneWire gOnewireIdBus(KB_PIN_ONEWIRE_PRESENCE);
#endif

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

#ifdef KB_PIN_METER_C
void meterInterruptC()
{
  gMeters[2] += 1;
}
#endif

#ifdef KB_PIN_METER_D
void meterInterruptD()
{
  gMeters[3] += 1;
}
#endif

#ifdef KB_PIN_METER_E
void meterInterruptE()
{
  gMeters[4] += 1;
}
#endif

#ifdef KB_PIN_METER_F
void meterInterruptF()
{
  gMeters[5] += 1;
}
#endif

//
// Serial I/O
//

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
  int foo = PROTOCOL_VERSION;
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_HELLO_ID);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_HELLO_TAG_PROTOCOL_VERSION, sizeof(foo), (char*)&foo);
  writeOutputPacket();
}

#if KB_ENABLE_ONEWIRE_THERMO
void byteToChars(uint8_t byte, char* out) {
  for (int i=0; i<2; i++) {
    uint8_t val = (byte >> (4*i)) & 0xf;
    if (val < 10) {
      out[1-i] = (char) ('0' + val);
    } else if (val < 16) {
      out[1-i] = (char) ('a' + (val - 10));
    }
  }
}

void writeThermoPacket(DS1820Sensor *sensor)
{
  long temp = sensor->GetTemp();
  if (temp == INVALID_TEMPERATURE_VALUE) {
    return;
  }

  char name[23] = "thermo-";
  char* pos = (name + 7);
  for (int i=7; i>=0; i--) {
    byteToChars(sensor->m_addr[i], pos);
    pos += 2;
  }
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_THERMO_READING);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_NAME, 23, name);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_READING, sizeof(temp), (char*)(&temp));
  writeOutputPacket();
}
#endif

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
  if (status == gLastMeters[channel]) {
    return;
  } else {
    gLastMeters[channel] = status;
  }
  name[4] = 0x30 + channel;
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_METER_STATUS);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_NAME, 5, name);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_READING, sizeof(status), (char*)(&status));
  writeOutputPacket();
}

#if KB_ENABLE_ONEWIRE_PRESENCE
void writeOnewirePresencePacket(uint8_t* id) {
  gOutputPacket.Reset();
  gOutputPacket.SetType(KB_MESSAGE_TYPE_ONEWIRE_PRESENCE);
  gOutputPacket.AddTag(KB_MESSAGE_TYPE_ONEWIRE_PRESENCE_TAG_DEVICE_ID, 8, (char*)id);
  writeOutputPacket();
}
#endif

#if KB_ENABLE_SELFTEST
void doTestPulse()
{
  // Strobes the test pin 4 times.
  int i=0;
  for (i=0; i<4; i++) {
    digitalWrite(KB_PIN_TEST_PULSE, 1);
    digitalWrite(KB_PIN_TEST_PULSE, 0);
  }
}
#endif

//
// Main
//

void setup()
{
  // Flow meter steup. Enable internal weak pullup to prevent disconnected line
  // from ticking away.
  pinMode(KB_PIN_METER_A, INPUT);
  digitalWrite(KB_PIN_METER_A, HIGH);
  attachInterrupt(0, meterInterruptA, RISING);

  pinMode(KB_PIN_METER_B, INPUT);
  digitalWrite(KB_PIN_METER_B, HIGH);
  attachInterrupt(1, meterInterruptB, RISING);

#ifdef KB_PIN_METER_C
  pinMode(KB_PIN_METER_C, INPUT);
  digitalWrite(KB_PIN_METER_C, HIGH);
  attachInterrupt(2, meterInterruptC, RISING);
#endif

#ifdef KB_PIN_METER_D
  pinMode(KB_PIN_METER_D, INPUT);
  digitalWrite(KB_PIN_METER_D, HIGH);
  attachInterrupt(3, meterInterruptD, RISING);
#endif

#ifdef KB_PIN_METER_E
  pinMode(KB_PIN_METER_E, INPUT);
  digitalWrite(KB_PIN_METER_E, HIGH);
  attachInterrupt(4, meterInterruptE, RISING);
#endif

#ifdef KB_PIN_METER_F
  pinMode(KB_PIN_METER_F, INPUT);
  digitalWrite(KB_PIN_METER_F, HIGH);
  attachInterrupt(5, meterInterruptF, RISING);
#endif

  pinMode(KB_PIN_RELAY_A, OUTPUT);
  pinMode(KB_PIN_RELAY_B, OUTPUT);
  pinMode(KB_PIN_ALARM, OUTPUT);
  pinMode(KB_PIN_TEST_PULSE, OUTPUT);

  Serial.begin(115200);

#if KB_ENABLE_BUZZER
  pinMode(KB_PIN_BUZZER, OUTPUT);
  setupBuzzer();
  playMelody(BOOT_MELODY);
#endif
  writeHelloPacket();
}

#if KB_ENABLE_ONEWIRE_THERMO
int stepOnewireThermoBus() {
  uint8_t addr[8];

  // Are we already working on a sensor? service it, possibly emitting a a
  // thermo packet.
  if (gThermoSensor.Initialized() || gThermoSensor.Busy()) {
    if (gThermoSensor.Update(millis())) {
      // Just finished conversion
      writeThermoPacket(&gThermoSensor);
      gThermoSensor.Reset();
    } else if (gThermoSensor.Busy()) {
      // More cycles needed on this sensor
      return 1;
    } else {
      // finished or not started
    }
  }

  // First time, or finished with last sensor; clean up, and look more more
  // devices.
  int more_search = gOnewireThermoBus.search(addr);
  if (!more_search) {
    // Bus exhausted; start over
    gOnewireThermoBus.reset_search();
    return 0;
  }

  // New sensor. Initialize and start work.
  gThermoSensor.Initialize(&gOnewireThermoBus, addr);
  gThermoSensor.Update(millis());
  return 1;
}
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
void stepOnewireIdBus() {
  uint8_t addr[8];
  if (!gOnewireIdBus.search(addr)) {
    gOnewireIdBus.reset_search();
  } else {
    if (OneWire::crc8(addr, 7) == addr[7]) {
      writeOnewirePresencePacket(addr);
    }
  }
}
#endif

void loop()
{

  writeMeterPacket(0);
  writeMeterPacket(1);
#ifdef KB_PIN_METER_C
  writeMeterPacket(2);
#endif
#ifdef KB_PIN_METER_D
  writeMeterPacket(3);
#endif
#ifdef KB_PIN_METER_E
  writeMeterPacket(4);
#endif
#ifdef KB_PIN_METER_F
  writeMeterPacket(5);
#endif

  //writeRelayPacket(0);
  //writeRelayPacket(1);

#if KB_ENABLE_ONEWIRE_THERMO
  stepOnewireThermoBus();
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
  stepOnewireIdBus();
#endif

#if KB_ENABLE_SELFTEST
  doTestPulse();
#endif

  delay(gUpdateInterval);
}

// vim: syntax=c
