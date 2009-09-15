#include <inttypes.h>
#include <avr/io.h>

#include "kegboard.h"
#include "ds1820.h"
#include "OneWire.h"

#define REFRESH_MS    5000

DS1820Sensor::DS1820Sensor(OneWire* bus)
{
  m_bus = bus;

  m_converting = false;
  m_next_conversion_clock = 0;
  m_conversion_start_clock = 0;
  m_temp = 0;
  m_temp_is_valid = false;
}

bool DS1820Sensor::Update(unsigned long clock)
{
  if (clock < m_conversion_start_clock) { // overflow of clock
    m_conversion_start_clock = 0;
  }

  unsigned long delta = clock - m_conversion_start_clock;

  // if we're not converting, and it is time to start, do so.
  if (!m_converting && clock >= m_next_conversion_clock) {
    m_converting = true;
    m_conversion_start_clock = clock;
    return StartConversion();
  }

  // if we're converting, and it is time to fetch, do so.
  if (m_converting && clock >= (m_conversion_start_clock + 1000)) {
    m_converting = false;

    m_next_conversion_clock = clock + REFRESH_MS;
    if (FetchConversion()) {
      m_temp_is_valid = true;
    } else {
      m_temp_is_valid = false;
    }
    return m_temp_is_valid;
  }

  // we're in the middle of the conversion, or it is not time to fetch yet.
  return false;

}

bool DS1820Sensor::ResetAndSkip()
{
  if (!m_bus->reset()) {
    return false;
  }
  m_bus->write(0xcc, 1);
  return true;
}

bool DS1820Sensor::StartConversion()
{
  if (!ResetAndSkip())
    return false;
  m_bus->write(0x44, 1);
  return true;
}

bool DS1820Sensor::FetchConversion()
{
  if (!ResetAndSkip())
    return false;

  int data[12];
  int i;

  m_bus->write(0xBE); // read scratchpad
  for (i = 0; i < 9; i++) {
    data[i] = m_bus->read();
    //Serial.print(data[i], HEX);
    //Serial.print(" ");
  }
  //Serial.print(" CRC=");
  //Serial.print( OneWire::crc8( data, 8), HEX);
  //Serial.println();

  m_temp = ((data[1] << 8) | data[0] );
  return true;
}

long DS1820Sensor::GetTemp(void)
{
  long scaled_temp = INVALID_TEMPERATURE_VALUE;
  if (!m_temp_is_valid)
    return scaled_temp;

  // The DS18B20 reports temperature as a 16 bit value.  The least significant
  // 12 bits are the temperature value, in increments of 1/16th deg C.  The most
  // significant bits carry the sign extension.
  //
  // This method returns the temperature in 1/10^6 deg C, so the value is scaled
  // up by (10^3/16) = 62500.
  scaled_temp = (m_temp & 0x0fff) * 62500;

  // Check sign extension
  bool negative = (m_temp & 0xf000) ? true : false;

  if (negative)
    scaled_temp = -1 * scaled_temp;

  return scaled_temp;
}

void DS1820Sensor::PrintTemp(void)
{
  long temp = GetTemp() / 1000000;
  Serial.print(temp);
}
