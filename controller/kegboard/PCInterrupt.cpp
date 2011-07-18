//
//  PCInterrupt.cpp
//  KegBoard
//
//  An extension to the interrupt support for Arduino.
//  Adds pin change interrupts to the external interrupts, allowing
//  any pin to support external interrupts efficiently.
//
//  Theory: all IO pins on Atmega168 are covered by Pin Change Interrupts.
//  The PCINT corresponding to the pin must be enabled and masked, and
//  an ISR routine provided.  Since PCINTs are per port, not per pin, the ISR
//  must use some logic to actually implement a per-pin interrupt service.
//
//  Pin to interrupt map:
//  D0-D7 = PCINT 16-23 = PCIR2 = PD = PCIE2 = pcmsk2
//  D8-D13 = PCINT 0-5 = PCIR0 = PB = PCIE0 = pcmsk0
//  A0-A5 (D14-D19) = PCINT 8-13 = PCIR1 = PC = PCIE1 = pcmsk1
//
//  Originally by ckiick at http://www.arduino.cc/playground/Main/PcInt
//  Modified to support RISING/FALLING by John Boiles 9/30/10
//
//  This program is free software; you can redistribute it and/or
//  modify it under the terms of the GNU General Public License
//  as published by the Free Software Foundation; either version 2
//  of the License, or (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#include "pins_arduino.h"
#include "WProgram.h"

volatile uint8_t *PCintPortToInputMask[] = {
  &PCMSK0,
  &PCMSK1,
  &PCMSK2
};

static int PCintMode[24];

typedef void (*voidFuncPtr)(void);

volatile static voidFuncPtr PCintFunc[24] = { NULL };

volatile static uint8_t PCintLast[3];

 void PCattachInterrupt(uint8_t pin, void (*userFunc)(void), int mode) {
  uint8_t bit = digitalPinToBitMask(pin);
  uint8_t port = digitalPinToPort(pin);
  uint8_t slot;
  volatile uint8_t *pcmask;

  pinMode(pin, INPUT);
  // map pin to PCIR register
  if (port == NOT_A_PORT) {
    return;
  } 
  else {
    port -= 2;
    pcmask = PCintPortToInputMask[port];
  }

  // Fix by Baziki. In the original sources there was a little bug,
  // which caused analog ports to work incorrectly.
  if (port == 1) {
    slot = port * 8 + (pin - 14);
  }
  else {
    slot = port * 8 + (pin % 8);
  }

  PCintMode[slot] = mode;
  PCintFunc[slot] = userFunc;
  // set the mask
  *pcmask |= bit;
  // enable the interrupt
  PCICR |= 0x01 << port;
}

void PCdetachInterrupt(uint8_t pin) {
  uint8_t bit = digitalPinToBitMask(pin);
  uint8_t port = digitalPinToPort(pin);
  volatile uint8_t *pcmask;

  // map pin to PCIR register
  if (port == NOT_A_PORT) {
    return;
  } else {
    port -= 2;
    pcmask = PCintPortToInputMask[port];
  }

  // disable the mask.
  *pcmask &= ~bit;
  // if that's the last one, disable the interrupt.
  if (*pcmask == 0) {
    PCICR &= ~(0x01 << port);
  }
}

// common code for isr handler. "port" is the PCINT number.
// there isn't really a good way to back-map ports and masks to pins.
static void PCint(uint8_t port) {
  uint8_t bit;
  uint8_t curr;
  uint8_t mask;
  uint8_t pin;

  // get the pin states for the indicated port.
  curr = *portInputRegister(port+2);
  mask = curr ^ PCintLast[port];
  // mask is pins that have changed. screen out non pcint pins.
  if ((mask &= *PCintPortToInputMask[port]) == 0) {
    return;
  }
  // mask is pcint pins that have changed.
  for (uint8_t i=0; i < 8; i++) {
    bit = 0x01 << i;
    if (bit & mask) {
      pin = port * 8 + i;
      // Trigger interrupt if mode is CHANGE, or if mode is RISING and
      // the bit is currently high, or if mode is FALLING and bit is low.
      if ((PCintMode[pin] == CHANGE
          || ((PCintMode[pin] == RISING) && (curr & bit))
          || ((PCintMode[pin] == FALLING) && !(curr & bit)))
          && (PCintFunc[pin] != NULL)) {
        PCintFunc[pin]();
      }
    }
  }
  // Save current pin values
  PCintLast[port] = curr;
}


SIGNAL(PCINT0_vect) {
  PCint(0);
}
SIGNAL(PCINT1_vect) {
  PCint(1);
}
SIGNAL(PCINT2_vect) {
  PCint(2);
}
