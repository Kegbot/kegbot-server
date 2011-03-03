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

#include "WProgram.h"
#include "kegboard.h"
#include "KegboardPacket.h"

#include <avr/io.h>
#include <HardwareSerial.h>
#include <string.h>
#include <util/crc16.h>

static uint16_t crc_ccitt_update_int(uint16_t crc, int value) {
  crc = _crc_ccitt_update(crc, value & 0xff);
  return _crc_ccitt_update(crc, (value >> 8) & 0xff);
}

static void serial_print_int(int value) {
  Serial.print(value & 0xff, BYTE);
  Serial.print((value >> 8) & 0xff, BYTE);
}

KegboardPacket::KegboardPacket()
{
  Reset();
}

bool KegboardPacket::IsReset() {
  return (m_type == 0) && (m_len == 0);
}

void KegboardPacket::Reset()
{
  m_len = 0;
  m_type = 0;
}

void KegboardPacket::AddTag(uint8_t tag, uint8_t buflen, char *buf)
{
  int i=0;
  m_payload[m_len++] = tag;
  m_payload[m_len++] = buflen;
  AppendBytes(buf, buflen);
}

uint8_t* KegboardPacket::FindTag(uint8_t tagnum) {
  uint8_t pos=0;
  while (pos < m_len && pos < KBSP_PAYLOAD_MAXLEN) {
    uint8_t tag = m_payload[pos];
    if (tag == tagnum) {
      return m_payload+pos;
    }
    pos += 2 + m_payload[pos+1];
  }
  return NULL;
}

bool KegboardPacket::ReadTag(uint8_t tagnum, uint8_t *value) {
  uint8_t *offptr = FindTag(tagnum);
  if (offptr == NULL) {
    return false;
  }
  *value = *(offptr+2);
  return true;
}

bool KegboardPacket::ReadTag(uint8_t tagnum, uint8_t** value) {
  uint8_t *offptr = FindTag(tagnum);
  if (offptr == NULL) {
    return false;
  }
  uint8_t slen = *(offptr+1);
  memcpy(*value, (offptr+2), slen);
  return true;
}

void KegboardPacket::AppendBytes(char *buf, int buflen)
{
  int i=0;
  while (i < buflen && m_len < KBSP_PAYLOAD_MAXLEN) {
    m_payload[m_len++] = (uint8_t) (*(buf+i));
    i++;
  }
}

uint16_t KegboardPacket::GenCrc()
{
  uint16_t crc = KBSP_PREFIX_CRC;

  crc = crc_ccitt_update_int(crc, m_type);
  crc = crc_ccitt_update_int(crc, m_len);

  for (int i=0; i<m_len; i++) {
    crc = _crc_ccitt_update(crc, m_payload[i]);
  }

  return crc;
}

void KegboardPacket::Print()
{
  int i;
  uint16_t crc = KBSP_PREFIX_CRC;

  // header
  // header: prefix
  Serial.print(KBSP_PREFIX);

  // header: message_id
  serial_print_int(m_type);
  crc = crc_ccitt_update_int(crc, m_type);

  // header: payload_len
  serial_print_int(m_len);
  crc = crc_ccitt_update_int(crc, m_len);

  // payload
  for (i=0; i<m_len; i++) {
    Serial.print(m_payload[i], BYTE);
    crc = _crc_ccitt_update(crc, m_payload[i]);
  }

  // trailer
  serial_print_int(crc);
  Serial.print('\r', BYTE);
  Serial.print('\n', BYTE);
}
