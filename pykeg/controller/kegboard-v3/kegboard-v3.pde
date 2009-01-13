// kegboard3 - v3.0.0
// Arduino implementation of Kegboard firmware

//
// Constants/defines
//

#define KB3_PROTO_PREFIX      "kb3 v1 "
#define KB3_PROTO_BOARDNAME   "kegboard"

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

void writeStatusPacket()
{
  Serial.print(KB3_PROTO_PREFIX);
  Serial.print(KB3_PROTO_BOARDNAME);
  Serial.print(": ");
  
  Serial.print("flow_0=");
  Serial.print(meter_a_count, DEC);
  Serial.print(" flow_1=");
  Serial.print(meter_b_count, DEC);
  Serial.print(" ");
  
  Serial.print("relay_0=");
  Serial.print(digitalRead(relay_a_pin), DEC);
  Serial.print(" relay_1=");
  Serial.print(digitalRead(relay_b_pin), DEC);
  
  Serial.print("\r\n");
}

void loop()
{
   writeStatusPacket();
   delay(LOOP_DELAY_MS);
}
