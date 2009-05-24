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
  while (i < buflen && m_len < 128) {
    m_payload[m_len++] = *(buf+i);
    i++;
  }
}

uint16_t KegboardPacket::GenCrc()
{
  uint16_t crc=0;
  int i=0;
  int val;

  crc = _crc_xmodem_update(crc, (m_type >> 8) & 0xff);
  crc = _crc_xmodem_update(crc, m_type & 0xff);
  crc = _crc_xmodem_update(crc, (m_len >> 8) & 0xff);
  crc = _crc_xmodem_update(crc, m_len & 0xff);

  for (i=0; i<m_len; i++)
    crc = _crc_xmodem_update(crc, (int)(m_payload[i]) & 0xff);

  return crc;
}

void KegboardPacket::Print()
{
  int i;
  // header
  Serial.print(m_type & 0xff, BYTE);
  Serial.print((m_type >> 8) & 0xff, BYTE);
  Serial.print(m_len & 0xff, BYTE);
  Serial.print((m_len >> 8) & 0xff, BYTE);

  // payload
  for (i=0; i<m_len; i++)
    Serial.print(m_payload[i], BYTE);

  // trailer
  uint16_t crc = GenCrc();
  Serial.print(crc & 0xff, BYTE);
  Serial.print((crc >> 8) & 0xff, BYTE);
  Serial.print('\r', BYTE);
  Serial.print('\n', BYTE);
}
