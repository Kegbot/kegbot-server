class OneWire;

class DS1820Sensor {
  public:
   DS1820Sensor(OneWire* bus);
   bool Update(unsigned long clock);
   void PrintTemp(void);
   long GetTemp();

  private:
   bool ResetAndSkip();
   bool StartConversion();
   bool FetchConversion();

  private:
   OneWire* m_bus;
   unsigned long m_refresh_ms;

   bool m_converting;
   unsigned long m_next_conversion_clock;
   unsigned long m_conversion_start_clock;
   unsigned long m_temp;
   bool m_temp_is_valid;
};
