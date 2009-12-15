#include <inttypes.h>

class KegboardPacket {
  public:
   KegboardPacket();
   void SetType(int type) {m_type = type;}
   int GetType() {return m_type;}
   void AddTag(int tag, int buflen, char *buf);
   uint8_t* FindTag(int tagnum);
   void AppendBytes(char *buf, int buflen);
   void Reset();
   bool IsReset();
   void Print();
   uint16_t GenCrc();
  private:
   int m_type;
   int m_len;
   uint8_t m_payload[KBSP_PAYLOAD_MAXLEN];
};
