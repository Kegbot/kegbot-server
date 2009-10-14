#include "kegboard.h"
#include "KegboardPacket.h"
#include <avr/io.h>
#include <util/crc16.h>

KegboardPacket::KegboardPacket()
{
  Reset();
}

void KegboardPacket::Reset()
{
  m_len = 0;
  m_type = 0;
}

void KegboardPacket::AddTag(int tag, int buflen, char *buf)
{
  int i=0;
  m_payload[m_len++] = tag;
  m_payload[m_len++] = buflen;
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
