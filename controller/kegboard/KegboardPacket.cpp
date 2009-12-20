#include "kegboard.h"
#include "KegboardPacket.h"
#include <avr/io.h>
#include <string.h>
#include <util/crc16.h>

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
  while (i < buflen && m_len < KBSP_PAYLOAD_MAXLEN) {
    m_payload[m_len++] = (uint8_t) (*(buf+i));
    i++;
  }
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

  crc = _crc_ccitt_update(crc, m_type & 0xff);
  crc = _crc_ccitt_update(crc, (m_type >> 8) & 0xff);
  crc = _crc_ccitt_update(crc, m_len & 0xff);
  crc = _crc_ccitt_update(crc, (m_len >> 8) & 0xff);

  for (int i=0; i<m_len; i++) {
    crc = _crc_ccitt_update(crc, m_payload[i]);
  }

  return crc;
}

void KegboardPacket::Print()
{
  int i;
  // header
  // header: prefix
  Serial.print(KBSP_PREFIX);

  // header: message_id
  Serial.print(m_type & 0xff, BYTE);
  Serial.print((m_type >> 8) & 0xff, BYTE);
  // header: payload_len
  Serial.print(m_len & 0xff, BYTE);
  Serial.print((m_len >> 8) & 0xff, BYTE);

  // payload
  for (i=0; i<m_len; i++) {
    Serial.print(m_payload[i], BYTE);
  }

  // trailer
  uint16_t crc = GenCrc();
  Serial.print(crc & 0xff, BYTE);
  Serial.print((crc >> 8) & 0xff, BYTE);
  Serial.print('\r', BYTE);
  Serial.print('\n', BYTE);
}
