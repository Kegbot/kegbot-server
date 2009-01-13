// kegboard3 - v3.0.0
// Arduino implementation of Kegboard firmware
//
// TODO:
//  - implement serial reading (relay on/off) commands
//  - get/set boardname with eeprom
//  - implement selftest mode

#include <util/crc16.h>

//
// Constants/defines
//

#define KBSP_PREFIX      "kbsp v1 "
#define KB3_BOARDNAME    "kegboard"

// Loop delay time
#define LOOP_DELAY_MS 500

//
// Pin definitions
//

int meter_a_pin = 2;
int meter_b_pin = 3;
int relay_a_pin = 4;
int relay_b_pin = 5;


// meter 'a' tick counter
volatile unsigned long meter_a_count = 0;

// meter 'b' tick counter
volatile unsigned long meter_b_count = 0;


void setup()
{
  pinMode(meter_a_pin, INPUT);
  pinMode(meter_b_pin, INPUT);
  
  attachInterrupt(0, meterInterruptA, RISING);
  attachInterrupt(1, meterInterruptB, RISING);

  pinMode(relay_a_pin, OUTPUT);
  pinMode(relay_b_pin, OUTPUT);
  
  Serial.begin(57600);
}

void meterInterruptA()
{
  meter_a_count += 1;
}

void meterInterruptB()
{
  meter_b_count += 1;
}

uint16_t genCrc(unsigned long val)
{
  uint16_t crc=0;
  int i=0;
  for (i=3;i>=0;i--)
    crc = _crc_xmodem_update(crc, (val >> (8*i)) & 0xff);
  return crc;
}

void writeStatusPacket()
{
  const unsigned long meter_a_tmp = meter_a_count;
  const unsigned long meter_b_tmp = meter_b_count;
  unsigned short meter_a_crc = genCrc(meter_a_tmp);
  unsigned short meter_b_crc = genCrc(meter_b_tmp);

  // prefix: kbsp v1 kegboard:
  Serial.print(KBSP_PREFIX);
  Serial.print(KB3_BOARDNAME);
  Serial.print(":\t");
  
  // flow_0 value && crc
  Serial.print("flow_0=");
  Serial.print(meter_a_count, DEC);
  Serial.print("flow_0_crc=0x");
  Serial.print(meter_a_crc, HEX);
  
  // flow_1 value && crc
  Serial.print("\tflow_1=");
  Serial.print(meter_b_count, DEC);
  Serial.print("\t");
  Serial.print("\tflow_1_crc=0x");
  Serial.print(meter_b_crc, HEX);
  
  // relay_0 && relay_1
  Serial.print("\trelay_0=");
  Serial.print(digitalRead(relay_a_pin), DEC);
  Serial.print("\trelay_1=");
  Serial.print(digitalRead(relay_b_pin), DEC);
  
  Serial.print("\r\n");
}

void loop()
{
   writeStatusPacket();
   delay(LOOP_DELAY_MS);
}
