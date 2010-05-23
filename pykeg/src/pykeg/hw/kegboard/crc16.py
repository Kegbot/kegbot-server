import types

_CRC16_CCITT_TABLE = []

def _crc16_ccitt_update(crc, byte):
  """CRC-16-CCITT (x^16 + x^12 + x^5 + 1)"""
  if type(byte) != types.IntType:
    byte = ord(byte)
  byte ^= (crc & 0xff)
  byte ^= (byte << 4) & 0xff

  ret = (byte << 8) | ((crc >> 8) & 0xff)
  ret ^= (byte >> 4)
  ret ^= byte << 3
  return ret

def _get_crc16_ccitt_table():
  global _CRC16_CCITT_TABLE
  if not _CRC16_CCITT_TABLE:
    ret = []
    for i in xrange(256):
      ret.append(_crc16_ccitt_update(0, i))
    _CRC16_CCITT_TABLE = ret
  return _CRC16_CCITT_TABLE

def crc16_ccitt(bytes):
  table = _get_crc16_ccitt_table()
  crc = 0
  for byte in bytes:
    byte = ord(byte)
    crc = ((crc >> 8) ^ table[(crc ^ byte) & 0xff])
  return crc
