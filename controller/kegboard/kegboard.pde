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
// Other Globals
//

// Up to 6 meters supported if using Arduino Mega
static unsigned long volatile gMeters[] = {0, 0, 0, 0, 0, 0};
static unsigned long volatile gLastMeters[] = {0, 0, 0, 0, 0, 0};
static bool volatile gRelayStatus[] = {false, false};

static KegboardPacket gInputPacket;

typedef struct {
  uint8_t header_bytes_read;
  uint8_t payload_bytes_remain;
  bool have_packet;
} RxPacketStat;

static RxPacketStat gPacketStat;

typedef struct {
  unsigned long uptime_ms;
  unsigned long last_uptime_ms;
  int uptime_days;
} UptimeStat;

static UptimeStat gUptimeStat;


#if KB_ENABLE_SELFTEST
static unsigned long gLastTestPulseMillis = 0;
#endif

#if KB_ENABLE_BUZZER
struct MelodyNote BOOT_MELODY[] = {
  {4, 3, 100}, {0, -1, 100},
  {4, 3, 70},  {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},

  {4, 0, 100}, {0, -1, 25},
  {4, 0, 100}, {0, -1, 25},
  {4, 0, 100}, {0, -1, 25},

  {4, 3, 100}, {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},
  {4, 3, 100}, {0, -1, 25},
  {4, 3, 100}, {4, 3, 100},

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

void writeHelloPacket()
{
  int foo = PROTOCOL_VERSION;
  KegboardPacket packet;
  packet.SetType(KB_MESSAGE_TYPE_HELLO_ID);
  packet.AddTag(KB_MESSAGE_TYPE_HELLO_TAG_PROTOCOL_VERSION, sizeof(foo), (char*)&foo);
  packet.Print();
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
  KegboardPacket packet;
  packet.SetType(KB_MESSAGE_TYPE_THERMO_READING);
  packet.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_NAME, 23, name);
  packet.AddTag(KB_MESSAGE_TYPE_THERMO_READING_TAG_SENSOR_READING, sizeof(temp), (char*)(&temp));
  packet.Print();
}
#endif

void writeRelayPacket(int channel)
{
  char name[7] = "relay-";
  int status = (int)(gRelayStatus[channel]);
  name[6] = 0x30 + channel;
  KegboardPacket packet;
  packet.SetType(KB_MESSAGE_TYPE_OUTPUT_STATUS);
  packet.AddTag(KB_MESSAGE_TYPE_OUTPUT_STATUS_TAG_OUTPUT_NAME, 7, name);
  packet.AddTag(KB_MESSAGE_TYPE_OUTPUT_STATUS_TAG_OUTPUT_READING, sizeof(status), (char*)(&status));
  packet.Print();
}

void writeMeterPacket(int channel)
{
  char name[5] = "flow";
  unsigned long status = gMeters[channel];
  if (status == gLastMeters[channel]) {
    return;
  } else {
    gLastMeters[channel] = status;
  }
  name[4] = 0x30 + channel;
  KegboardPacket packet;
  packet.SetType(KB_MESSAGE_TYPE_METER_STATUS);
  packet.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_NAME, 5, name);
  packet.AddTag(KB_MESSAGE_TYPE_METER_STATUS_TAG_METER_READING, sizeof(status), (char*)(&status));
  packet.Print();
}

#if KB_ENABLE_ONEWIRE_PRESENCE
void writeOnewirePresencePacket(uint8_t* id) {
  // Hack: Ignore the 0x0 onewire id.
  // TODO(mikey): Is it a bug that OneWire::search() is generating this?
  bool null_id = true;
  for (int i=0; i<8; i++) {
    if (id[i] != 0) {
      null_id = false;
      break;
    }
  }
  if (null_id) {
    return;
  }
  KegboardPacket packet;
  packet.SetType(KB_MESSAGE_TYPE_ONEWIRE_PRESENCE);
  packet.AddTag(KB_MESSAGE_TYPE_ONEWIRE_PRESENCE_TAG_DEVICE_ID, 8, (char*)id);
  packet.Print();
}
#endif

#if KB_ENABLE_SELFTEST
void doTestPulse()
{
  // Strobes the test pin `KB_SELFTEST_PULSES` times, every
  // `KB_SELFTEST_INTERVAL_MS` milliseconds
  unsigned long now = millis();
  if ((now - gLastTestPulseMillis) >= KB_SELFTEST_INTERVAL_MS) {
    gLastTestPulseMillis = now;
    for (int i=0; i<KB_SELFTEST_PULSES; i++) {
      digitalWrite(KB_PIN_TEST_PULSE, 1);
      digitalWrite(KB_PIN_TEST_PULSE, 0);
    }
  }
}
#endif

//
// Main
//

void setup()
{
  memset(&gUptimeStat, 0, sizeof(UptimeStat));
  memset(&gPacketStat, 0, sizeof(RxPacketStat));

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

void updateTimekeeping() {
  // TODO(mikey): it would be more efficient to take control of timer0
  unsigned long now = millis();
  gUptimeStat.uptime_ms += now - gUptimeStat.last_uptime_ms;
  gUptimeStat.last_uptime_ms = now;

  if (gUptimeStat.uptime_ms >= MS_PER_DAY) {
    gUptimeStat.uptime_days += 1;
    gUptimeStat.uptime_ms -= MS_PER_DAY;
  }
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

static void readSerialBytes(char *dest_buf, int num_bytes, int offset) {
  while (num_bytes-- != 0) {
    dest_buf[offset++] = Serial.read();
  }
}

void readIncomingSerialData() {
  char serial_buf[KBSP_PAYLOAD_MAXLEN];
  int bytes_to_read = 0;
  int bytes_available = Serial.available();

  if (bytes_available == 0) {
    return;
  }

  // Do not read a new packet if we have one awiting processing.  This should
  // never happen.
  if (gPacketStat.have_packet) {
    return;
  }

  // Look for a new packet.
  if (gPacketStat.header_bytes_read != KBSP_HEADER_PREFIX_LEN) {
    while (bytes_available > 0) {
      char next_char = Serial.read();
      bytes_available -= 1;
      if (next_char == KBSP_PREFIX[gPacketStat.header_bytes_read]) {
        gPacketStat.header_bytes_read++;
        if (gPacketStat.header_bytes_read == KBSP_HEADER_PREFIX_LEN) {
          // Found start of packet, break.
          break;
        }
      } else {
        // Wrong character in prefix; reset framing.
        gPacketStat.header_bytes_read = 0;
      }
    }
  }

  // If we haven't yet found a frame, or there are no more bytes to read after
  // finding a frame, bail out.
  if (bytes_available == 0 || (gPacketStat.header_bytes_read < KBSP_HEADER_PREFIX_LEN)) {
    return;
  }

  // Read the remainder of the header, if not yet found.
  if (gPacketStat.header_bytes_read < KBSP_HEADER_LEN) {
    if (bytes_available < 4) {
      return;
    }
    gInputPacket.SetType((Serial.read() << 8) | Serial.read());
    gPacketStat.payload_bytes_remain = (Serial.read() << 8) | Serial.read();
    bytes_available -= 4;
    gPacketStat.header_bytes_read += 4;

    // Check that the 'len' field is not bogus. If it is, throw out the packet
    // and reset.
    if (gPacketStat.payload_bytes_remain < 0 ||
        gPacketStat.payload_bytes_remain > KBSP_PAYLOAD_MAXLEN) {
      goto out_reset;
    }
  }

  if (bytes_available == 0) {
    return;
  }

  // TODO(mikey): Just read directly into KegboardPacket.
  bytes_to_read = (gPacketStat.payload_bytes_remain >= bytes_available) ?
      gPacketStat.payload_bytes_remain : bytes_available;
  readSerialBytes(serial_buf, bytes_to_read, 0);
  gInputPacket.AppendBytes(serial_buf, bytes_to_read);
  gPacketStat.payload_bytes_remain -= bytes_to_read;

  // Need more payload bytes than are now available.
  if (gPacketStat.payload_bytes_remain > 0) {
    return;
  }

  // We have a complete payload. Now grab the footer.
  if (!gPacketStat.have_packet) {
    if (bytes_available < KBSP_FOOTER_LEN) {
      return;
    }
    readSerialBytes(serial_buf, KBSP_FOOTER_LEN, 0);

    // Check CRC

    // Check trailer
    if (strncmp((serial_buf + 2), KBSP_TRAILER, KBSP_FOOTER_TRAILER_LEN)) {
      goto out_reset;
    }
    gPacketStat.have_packet = true;
  }

  // Done!

  return;

out_reset:
  memset(&gPacketStat, 0, sizeof(RxPacketStat));
  gInputPacket.Reset();
}

void handleInputPacket() {
  if (!gPacketStat.have_packet) {
    return;
  }

  // Process the input packet.
  switch (gInputPacket.GetType()) {
    case KB_MESSAGE_TYPE_PING:
      writeHelloPacket();
      break;
  }

  // Reset the input packet.
  memset(&gPacketStat, 0, sizeof(RxPacketStat));
}

void loop()
{
  updateTimekeeping();

  readIncomingSerialData();
  handleInputPacket();

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
}

// vim: syntax=c
