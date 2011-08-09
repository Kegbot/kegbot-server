/**
 * kegboard.pde - Kegboard v3 Arduino project
 * Copyright 2003-2011 Mike Wakerly <opensource@hoho.com>
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

#include <WProgram.h>
#include <avr/pgmspace.h>
#include <string.h>
#include <util/crc16.h>
#include <util/delay.h>
#include <wiring.h>

#include "kegboard.h"
#include "kegboard_config.h"
#include "ds1820.h"
#include "KegboardPacket.h"
#include "version.h"

#if (KB_ENABLE_ONEWIRE_THERMO || KB_ENABLE_ONEWIRE_PRESENCE)
#include "OneWire.h"
#endif

#if KB_ENABLE_BUZZER
#include "buzzer.h"
#endif

#if KB_ENABLE_ID12_RFID
#include "NewSoftSerial.h"
NewSoftSerial gSerialRfid = NewSoftSerial(KB_PIN_SERIAL_RFID_RX, -1);
int gRfidPos = -1;
unsigned char gRfidChecksum = 0;
unsigned char gRfidBuf[RFID_PAYLOAD_CHARS];
#endif

#if KB_ENABLE_MAGSTRIPE
#include "MagStripe.h"
#include "PCInterrupt.h"
#endif

//
// Other Globals
//

// Up to 6 meters supported if using Arduino Mega
static unsigned long volatile gMeters[] = {0, 0, 0, 0, 0, 0};
static unsigned long volatile gLastMeters[] = {0, 0, 0, 0, 0, 0};
static uint8_t gOutputPins[] = {
  KB_PIN_RELAY_A,
  KB_PIN_RELAY_B,
  KB_PIN_RELAY_C,
  KB_PIN_RELAY_D,
  KB_PIN_LED_FLOW_A,
  KB_PIN_LED_FLOW_B
};

static KegboardPacket gInputPacket;

// Structure that holds the state of incoming serial bytes.
typedef struct {
  uint8_t header_bytes_read;
  uint8_t payload_bytes_remain;
  bool have_packet;
} RxPacketStat;

static RxPacketStat gPacketStat;

// Relay output status.
typedef struct {
  bool enabled;
  unsigned long touched_timestamp_ms;
} RelayOutputStat;

static RelayOutputStat gRelayStatus[KB_NUM_RELAY_OUTPUTS];

// Structure to keep information about this device's uptime. 
typedef struct {
  unsigned long uptime_ms;
  unsigned long last_uptime_ms;
  unsigned long last_meter_event;
  int uptime_days;
} UptimeStat;

static UptimeStat gUptimeStat;

#if KB_ENABLE_ONEWIRE_PRESENCE
// Structure used to cache information about devices on the onewire bus.
typedef struct {
  uint64_t id;
  bool valid;
  uint8_t present_count;
} OnewireEntry;

static OnewireEntry gOnewireCache[ONEWIRE_CACHE_SIZE];
#endif

#if KB_ENABLE_SELFTEST
static unsigned long gLastTestPulseMillis = 0;
#endif

#if KB_ENABLE_BUZZER
PROGMEM prog_uint16_t BOOT_MELODY[] = {
  MELODY_NOTE(4, 3, 100), MELODY_NOTE(0, NOTE_SILENCE, 100),
  MELODY_NOTE(4, 3, 70 ), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 3, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),

  MELODY_NOTE(4, 0, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 0, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 0, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),

  MELODY_NOTE(4, 3, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 3, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 3, 100), MELODY_NOTE(0, NOTE_SILENCE, 25),
  MELODY_NOTE(4, 3, 100), MELODY_NOTE(4, 3, 100),

  MELODY_NOTE(0, NOTE_SILENCE, 0)
};

#if (KB_ENABLE_ID12_RFID || KB_ENABLE_ONEWIRE_PRESENCE)
PROGMEM prog_uint16_t AUTH_ON_MELODY[] = {
  MELODY_NOTE(4, 1, 50), MELODY_NOTE(0, NOTE_SILENCE, 10),
  MELODY_NOTE(4, 4, 50 ), MELODY_NOTE(0, NOTE_SILENCE, 10),
  MELODY_NOTE(4, 8, 50),

  MELODY_NOTE(0, NOTE_SILENCE, 0)
};
#endif  // KB_ENABLE_ID12_RFID || KB_ENABLE_ONEWIRE_PRESENCE
#endif  // KB_ENABLE_BUZZER

#if KB_ENABLE_ONEWIRE_THERMO
static OneWire gOnewireThermoBus(KB_PIN_ONEWIRE_THERMO);
static DS1820Sensor gThermoSensor;
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
static OneWire gOnewireIdBus(KB_PIN_ONEWIRE_PRESENCE);
#endif

#if KB_ENABLE_MAGSTRIPE
static MagStripe gMagStripe(KB_PIN_MAGSTRIPE_CLOCK, KB_PIN_MAGSTRIPE_DATA, KB_PIN_MAGSTRIPE_CARD_PRESENT);
#endif

//
// ISRs
//

void meterInterruptA()
{
  gMeters[0] += 1;
}

#ifdef KB_PIN_METER_B
void meterInterruptB()
{
  gMeters[1] += 1;
}
#endif

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

#if KB_ENABLE_MAGSTRIPE
void magStripeClockInterrupt()
{
  gMagStripe.clockData();
}
#endif

//
// Serial I/O
//

void writeHelloPacket()
{
  int foo = FIRMWARE_VERSION;
  KegboardPacket packet;
  packet.SetType(KBM_HELLO_ID);
  packet.AddTag(KBM_HELLO_TAG_FIRMWARE_VERSION, sizeof(foo), (char*)&foo);
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
  packet.SetType(KBM_THERMO_READING);
  packet.AddTag(KBM_THERMO_READING_TAG_SENSOR_NAME, 23, name);
  packet.AddTag(KBM_THERMO_READING_TAG_SENSOR_READING, sizeof(temp), (char*)(&temp));
  packet.Print();
}
#endif

void writeRelayPacket(int channel)
{
  char name[6] = "relay";
  int status = (int) (gRelayStatus[channel].enabled);
  name[5] = 0x30 + channel;
  KegboardPacket packet;
  packet.SetType(KBM_OUTPUT_STATUS);
  packet.AddTag(KBM_OUTPUT_STATUS_TAG_OUTPUT_NAME, 6, name);
  packet.AddTag(KBM_OUTPUT_STATUS_TAG_OUTPUT_READING, sizeof(status), (char*)(&status));
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
  packet.SetType(KBM_METER_STATUS);
  packet.AddTag(KBM_METER_STATUS_TAG_METER_NAME, 5, name);
  packet.AddTag(KBM_METER_STATUS_TAG_METER_READING, sizeof(status), (char*)(&status));
  packet.Print();
}

void writeAuthPacket(char* device_name, uint8_t* token, int token_len,
    char status) {
  KegboardPacket packet;
  packet.SetType(KBM_AUTH_TOKEN);
  packet.AddTag(KBM_AUTH_TOKEN_TAG_DEVICE, strlen(device_name), device_name);
  packet.AddTag(KBM_AUTH_TOKEN_TAG_TOKEN, token_len, (char*)token);
  packet.AddTag(KBM_AUTH_TOKEN_TAG_STATUS, 1, &status);
  packet.Print();
#if KB_ENABLE_BUZZER
  if (status == 1) {
    playMelody(AUTH_ON_MELODY);
  }
#endif
}

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

#ifdef KB_PIN_METER_B
  pinMode(KB_PIN_METER_B, INPUT);
  digitalWrite(KB_PIN_METER_B, HIGH);
  attachInterrupt(1, meterInterruptB, RISING);
#endif

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
  pinMode(KB_PIN_RELAY_C, OUTPUT);
  pinMode(KB_PIN_RELAY_D, OUTPUT);
  pinMode(KB_PIN_LED_FLOW_A, OUTPUT);
  pinMode(KB_PIN_LED_FLOW_B, OUTPUT);
  pinMode(KB_PIN_ALARM, OUTPUT);
  pinMode(KB_PIN_TEST_PULSE, OUTPUT);

  Serial.begin(115200);

#if KB_ENABLE_BUZZER
  pinMode(KB_PIN_BUZZER, OUTPUT);
  setupBuzzer();
  playMelody(BOOT_MELODY);
#endif

#if KB_ENABLE_ID12_RFID
  gSerialRfid.begin(9600);
  pinMode(KB_PIN_RFID_RESET, OUTPUT);
  digitalWrite(KB_PIN_RFID_RESET, HIGH);
#endif

#if KB_ENABLE_MAGSTRIPE
  PCattachInterrupt(KB_PIN_MAGSTRIPE_CLOCK, magStripeClockInterrupt, FALLING);
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
  unsigned long now = millis();

  // Are we already working on a sensor? service it, possibly emitting a a
  // thermo packet.
  if (gThermoSensor.Initialized() || gThermoSensor.Busy()) {
    if (gThermoSensor.Update(now)) {
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
  gThermoSensor.Update(now);
  return 1;
}
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
void stepOnewireIdBus() {
  uint64_t addr;
  uint8_t* addr_ptr = (uint8_t*) &addr;

  // No more devices on the bus; reset the bus.
  if (!gOnewireIdBus.search(addr_ptr)) {
    gOnewireIdBus.reset_search();

    for (int i=0; i < ONEWIRE_CACHE_SIZE; i++) {
      OnewireEntry* entry = &gOnewireCache[i];
      if (!entry->valid) {
        continue;
      }

      entry->present_count -= 1;
      if (entry->present_count == 0) {
        entry->valid = false;
        writeAuthPacket("onewire", (uint8_t*)&(entry->id), 8, 0);
      }
    }
    return;
  }

  // We found a device; check the address CRC and ignore if invalid.
  if (OneWire::crc8(addr_ptr, 7) != addr_ptr[7]) {
    return;
  }

  // Ignore the null address. TODO(mikey): Is there a bug in OneWire.cpp that
  // causes this to be reported?
  if (addr == 0) {
    return;
  }

  // Look for id in cache. If seen last time around, mark present (and do not
  // emit packet).
  for (int i=0; i < ONEWIRE_CACHE_SIZE; i++) {
    OnewireEntry* entry = &gOnewireCache[i];
    if (entry->valid && entry->id == addr) {
      entry->present_count = ONEWIRE_CACHE_MAX_MISSING_SEARCHES;
      return;
    }
  }

  // Add id to cache and emit presence packet.
  // NOTE(mikey): If the cache is full, no packet will be emitted. This is
  // probably the best behavior; removing a device from the bus will clear up an
  // entry in the cache.
  for (int i=0; i < ONEWIRE_CACHE_SIZE; i++) {
    OnewireEntry* entry = &gOnewireCache[i];
    if (!entry->valid) {
      entry->valid = true;
      entry->present_count = ONEWIRE_CACHE_MAX_MISSING_SEARCHES;
      entry->id = addr;
      writeAuthPacket("onewire", (uint8_t*)&(entry->id), 8, 1);
      return;
    }
  }
}
#endif

static void readSerialBytes(char *dest_buf, int num_bytes, int offset) {
  while (num_bytes-- != 0) {
    dest_buf[offset++] = Serial.read();
  }
}

#if KB_ENABLE_ID12_RFID
static void doProcessRfid() {
  if (gSerialRfid.available() == 0) {
    return;
  }

  if (gRfidPos == -1) {
    if (gSerialRfid.read() != 0x02) {
      return;
    } else {
      gRfidPos = 0;
      gRfidChecksum = 0;
    }
  }

  while (gRfidPos < 12) {
    unsigned char b;
    int rfid_index = (RFID_PAYLOAD_CHARS/2 - 1) - gRfidPos / 2;
    if (gSerialRfid.available() == 0) {
      return;
    }

    b = gSerialRfid.read();
    if (b == CR || b == LF || b == STX || b == ETX) {
      goto out_reset;
    }

    // ASCII to hex
    if (b >= '0' && b <= '9') {
      b -= '0';
    } else if (b >= 'A' && b <= 'F') {
      b -= 'A';
      b += 10;
    }

    if ((gRfidPos % 2) == 0) {
      // Clears previous value.
      gRfidBuf[rfid_index] = b << 4;
    } else {
      gRfidBuf[rfid_index] |= b;
      gRfidChecksum ^= gRfidBuf[rfid_index];
    }

    gRfidPos++;
  }

  if (gRfidPos == RFID_PAYLOAD_CHARS) {
    if (gRfidChecksum == 0) {
      writeAuthPacket("core.rfid", gRfidBuf+1, 5, 1);
      writeAuthPacket("core.rfid", gRfidBuf+1, 5, 0);
    }
  }

  digitalWrite(KB_PIN_RFID_RESET, LOW);
  delay(200);
  digitalWrite(KB_PIN_RFID_RESET, HIGH);

out_reset:
  gRfidPos = -1;
  gRfidChecksum = 0;
}
#endif

#if KB_ENABLE_MAGSTRIPE
void doProcessMagStripe()
{
  // Return if there is no data
  uint8_t* data;
  int dataSize = gMagStripe.getData(&data);
  if (dataSize <= 0) return;

  writeAuthPacket("magstripe", data, dataSize, 1);
  writeAuthPacket("magstripe", data, dataSize, 0);
}
#endif

void resetInputPacket() {
  memset(&gPacketStat, 0, sizeof(RxPacketStat));
  gInputPacket.Reset();
}

void readIncomingSerialData() {
  char serial_buf[KBSP_PAYLOAD_MAXLEN];
  volatile uint8_t bytes_available = Serial.available();

  // Do not read a new packet if we have one awiting processing.  This should
  // never happen.
  if (gPacketStat.have_packet) {
    return;
  }

  // Look for a new packet.
  if (gPacketStat.header_bytes_read < KBSP_HEADER_PREFIX_LEN) {
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
        if (next_char == KBSP_PREFIX[0]) {
          gPacketStat.header_bytes_read = 1;
        } else {
          gPacketStat.header_bytes_read = 0;
        }
      }
    }
  }

  // Read the remainder of the header, if not yet found.
  if (gPacketStat.header_bytes_read < KBSP_HEADER_LEN) {
    if (bytes_available < 4) {
      return;
    }
    gInputPacket.SetType(Serial.read() | (Serial.read() << 8));
    gPacketStat.payload_bytes_remain = Serial.read() | (Serial.read() << 8);
    bytes_available -= 4;
    gPacketStat.header_bytes_read += 4;

    // Check that the 'len' field is not bogus. If it is, throw out the packet
    // and reset.
    if (gPacketStat.payload_bytes_remain > KBSP_PAYLOAD_MAXLEN) {
      goto out_reset;
    }
  }

  // If we haven't yet found a frame, or there are no more bytes to read after
  // finding a frame, bail out.
  if (bytes_available == 0 || (gPacketStat.header_bytes_read < KBSP_HEADER_LEN)) {
    return;
  }

  // TODO(mikey): Just read directly into KegboardPacket.
  if (gPacketStat.payload_bytes_remain) {
    int bytes_to_read = (gPacketStat.payload_bytes_remain >= bytes_available) ?
        bytes_available : gPacketStat.payload_bytes_remain;
    readSerialBytes(serial_buf, bytes_to_read, 0);
    gInputPacket.AppendBytes(serial_buf, bytes_to_read);
    gPacketStat.payload_bytes_remain -= bytes_to_read;
    bytes_available -= bytes_to_read;
  }

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
  resetInputPacket();
}

void setRelayOutput(uint8_t id, uint8_t mode) {
  gRelayStatus[id].touched_timestamp_ms = millis();
  if (mode == OUTPUT_DISABLED && gRelayStatus[id].enabled) {
    digitalWrite(gOutputPins[id], LOW);
    gRelayStatus[id].enabled = false;
  } else if (mode == OUTPUT_ENABLED && !gRelayStatus[id].enabled) {
    digitalWrite(gOutputPins[id], HIGH);
    gRelayStatus[id].enabled = true;
  } else {
    return;
  }
  writeRelayPacket(id);
}

void handleInputPacket() {
  if (!gPacketStat.have_packet) {
    return;
  }

  // Process the input packet.
  switch (gInputPacket.GetType()) {
    case KBM_PING:
      writeHelloPacket();
      break;

    case KBM_SET_OUTPUT: {
      uint8_t id, mode;

      if (!gInputPacket.ReadTag(KBM_SET_OUTPUT_TAG_OUTPUT_ID, &id)
          || !gInputPacket.ReadTag(KBM_SET_OUTPUT_TAG_OUTPUT_MODE, &mode)) {
        break;
      }

      if (id < KB_NUM_RELAY_OUTPUTS) {
        setRelayOutput(id, mode);
      }
      break;
    }
  }
  resetInputPacket();
}

void writeMeterPackets() {
  unsigned long now = millis();

  // Forcibly coalesce meter updates; we want to be responsive, but sending
  // meter updates at every opportunity would cause too many messages to be
  // sent.
  if ((now - gUptimeStat.last_meter_event) > KB_METER_UPDATE_INTERVAL_MS) {
    gUptimeStat.last_meter_event = now;
  } else {
    return;
  }

  writeMeterPacket(0);
#ifdef KB_PIN_METER_B
  writeMeterPacket(1);
#endif
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
}

void stepRelayWatchdog() {
  for (int i = 0; i < KB_NUM_RELAY_OUTPUTS; i++) {
    if (gRelayStatus[i].enabled == true) {
      unsigned long now = millis();
      if ((now - gRelayStatus[i].touched_timestamp_ms) > KB_RELAY_WATCHDOG_MS) {
        setRelayOutput(i, OUTPUT_DISABLED);
      }
    }
  }
}

void loop()
{
  updateTimekeeping();

  readIncomingSerialData();
  handleInputPacket();

  writeMeterPackets();
  stepRelayWatchdog();

#if KB_ENABLE_ONEWIRE_THERMO
  stepOnewireThermoBus();
#endif

#if KB_ENABLE_ONEWIRE_PRESENCE
  stepOnewireIdBus();
#endif

#if KB_ENABLE_ID12_RFID
  doProcessRfid();
#endif

#if KB_ENABLE_MAGSTRIPE
  doProcessMagStripe();
#endif

#if KB_ENABLE_SELFTEST
  doTestPulse();
#endif
}

// vim: syntax=c
