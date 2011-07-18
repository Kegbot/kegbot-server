//
//  PCInterrupt.h
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

//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#include <inttypes.h>

/*
 * Dttach an interrupt to a specific pin using pin change interrupts.
 */
void PCattachInterrupt(uint8_t pin, void (*userFunc)(void), int mode);

/*
 * Detach an pin change interrupt from a specific pin.
 */
void PCdetachInterrupt(uint8_t pin);
