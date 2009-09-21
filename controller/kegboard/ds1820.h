#define INVALID_TEMPERATURE_VALUE 0x7fffffff

class OneWire;

class DS1820Sensor {
  public:
   DS1820Sensor();
   void Update(unsigned long clock);
   void PrintTemp(void);
   long GetTemp();
   bool Busy();
   bool Initialized();
   int CompareId(uint8_t* other);
   void Initialize(OneWire* bus, uint8_t* addr);

   uint8_t m_addr[8];

  private:
   bool ResetAndSkip();
   bool StartConversion();
   bool FetchConversion();
   void Reset(uint8_t *addr);

  private:
   OneWire* m_bus;
   unsigned long m_refresh_ms;

   bool m_initialized;
   bool m_converting;
   unsigned long m_next_conversion_clock;
   unsigned long m_conversion_start_clock;
   unsigned long m_temp;
   bool m_temp_is_valid;
};
