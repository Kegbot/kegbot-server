#include <inttypes.h>
#include <avr/io.h>

#include "kegboard.h"
#include "ds1820.h"
#include "OneWire.h"

DS1820Sensor::DS1820Sensor(OneWire* bus)
{
  m_bus = bus;
  m_refresh_ms = 5000;

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
    
    m_next_conversion_clock = clock + m_refresh_ms;
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

void DS1820Sensor::PrintTemp(void)
{
  if (!m_temp_is_valid) {
    Serial.print("-99.0");
    return;
  }
  long utemp = m_temp & 0x07ff;
  bool negative = (m_temp & 0xf800) ? true : false;
  
  long temp_100  = (6 * utemp) + utemp / 4;    // multiply by (100 * 0.0625) or 6.25
  long whole  = temp_100 / 100;  // separate off the whole and fractional portions
  long fract = temp_100 % 100;

  if (negative)
     Serial.print("-");

  Serial.print(whole);
  Serial.print(".");
  if (fract < 10)
  {
     Serial.print("0");
  }
  Serial.print(fract);
}
