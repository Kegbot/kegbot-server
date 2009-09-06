/**
 * kegboard-v3.pde - Kegboard v3 Arduino project
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

#if KB_ENABLE_ONEWIRE
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

static unsigned long volatile gMeters[] = {0, 0};
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

#if KB_ENABLE_ONEWIRE
static OneWire gThermoBusA(KB_PIN_THERMO_A);
static OneWire gThermoBusB(KB_PIN_THERMO_B);
static DS1820Sensor gThermoSensors[] = {
  DS1820Sensor(&gThermoBusA),
  DS1820Sensor(&gThermoBusB),
};
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
  pinMode(KB_PIN_METER_A, INPUT);
  pinMode(KB_PIN_METER_B, INPUT);

  // enable internal pullup to prevent disconnected line from ticking away
  digitalWrite(KB_PIN_METER_A, HIGH);
  digitalWrite(KB_PIN_METER_B, HIGH);

  attachInterrupt(0, meterInterruptA, RISING);
  attachInterrupt(1, meterInterruptB, RISING);

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
}

void loop()
{
  writeHelloPacket();

  writeMeterPacket(0);
  writeMeterPacket(1);

  writeRelayPacket(0);
  writeRelayPacket(1);

#if KB_ENABLE_ONEWIRE
  {
    unsigned long clock = millis();
    gThermoSensors[0].Update(clock);
    gThermoSensors[1].Update(clock);
  }
  writeThermoPacket(0);
  writeThermoPacket(1);
#endif

#if KB_ENABLE_SELFTEST
  doTestPulse();
#endif

  delay(gUpdateInterval);
}

// vim: syntax=c
