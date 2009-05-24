/**
 * buzzer.c - Arduino buzzer routines
 * Copyright 2009 Mike Wakerly <opensource@hoho.com>
 *
 * Based on code originally written by & used with permission from:
 *   andrew@rocketnumbernine.com
 *   http://www.rocketnumbernine.com/2009/03/27/xyloduino-simple-arduinopiezo-organ/
 *
 * This file is part of the Kegbot package of the Kegbot project.
 * For more information on Kegbot, see http://kegbot.org/
 *
 * Kegbot is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Kegbot is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Kegbot.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "buzzer.h"

static int oc[] = {
  239, 225, 213, 201, 190, 179, 169, 159, 150, 142, 134, 127,
  119, 113, 106, 100, 95, 89, 84, 80, 75, 71, 67, 63};

// prescale for octaves
static int pre[] = {5, 5, 4, 4, 3, 3};

void setupBuzzer()
{
  // Toggle OC0A on compare match
  // Mode 2 - CTC mode
  TCCR0A = (0<<COM0A1) | (1<<COM0A0) | (0<<WGM02) |  (1<<WGM01) | (0<<WGM00);

  // OC0A port is D6 on atmega328 - set to output
  DDRD |= (1<<6);

  // prescale (0=Off,1=clk,2=8,3=64,4=256,5=1024) 
  TCCR0B = (1<<CS02) | (0<<CS01) | (0<<CS00);
}

// play the note (note=-1 turns off)
void playMidiNote(int octave, int note)
{
  if (note == -1) {
    TCCR0B = 0;
  } else {
    TCCR0B = pre[octave];
    OCR0A = oc[(octave%2)*12 + note];
  }
}

// Play a sequence of MelodyNotes
// Sequence must terminate with octave == -1
void playMelody(struct MelodyNote* melody)
{
  int i=0;
  for (i=0; melody[i].octave != -1; i++) {
    playMidiNote(melody[i].octave, melody[i].note);
    _delay_ms(melody[i].duration);
  }
  // Silence the buzzer at the end, in case the sequence did not do so.
  playMidiNote(-1, -1);
}
