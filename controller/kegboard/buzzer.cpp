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
#include <avr/pgmspace.h>

extern "C" {
// For delay()
#include <util/delay.h>
#include "WConstants.h"
}

#include "buzzer.h"

#define PRESCALER_MASK  0x07

PROGMEM prog_uchar gOctave[] = {
  239, 225, 213, 201, 190, 179, 169, 159, 150, 142, 134, 127,
  119, 113, 106, 100, 95, 89, 84, 80, 75, 71, 67, 63
};

// prescale for octaves
PROGMEM prog_uchar gPrescale[] = {5, 5, 4, 4, 3, 3};

void setupBuzzer()
{
  // Note: Buzzer uses the atmega timer2, which is responsible for arduino PWM
  // pins 3 and 11.  Arduino PWM routines (eg analogWrite) cannot be used on
  // these pins when the buzzer is enabled.
  TCCR2A = (0<<COM0A1) | (1<<COM0A0) | (0<<WGM02) | (1<<WGM01) | (0<<WGM00);
}

// play the note (note=NOTE_SILENCE turns off)
void playMidiNote(uint8_t octave, uint8_t note)
{
  TCCR2B &= ~PRESCALER_MASK;
  if (note == NOTE_SILENCE) {
    return;
  }
  TCCR2B |= pgm_read_byte_near(gPrescale + octave) & PRESCALER_MASK;
  OCR2A = pgm_read_byte_near(gOctave + ((octave%2)*12 + note));
}

// Play a sequence of MelodyNotes
// Sequence must terminate with octave == -1
void playMelody(prog_uint16_t* notes)
{
  int i=0;
  while (true) {
    uint16_t melody_note = pgm_read_word_near(notes + i);
    i++;
    uint8_t duration = DURATION(melody_note);
    if (duration == 0) {
      // Silence the buzzer at the end, in case the sequence did not do so.
      playMidiNote(0, NOTE_SILENCE);
      return;
    }
    uint8_t octave = OCTAVE(melody_note);
    uint8_t note = NOTE(melody_note);
    playMidiNote(octave, note);

    // NOTE(mikey): Originally, we used the busy-loop _delay_ms method to avoid
    // tmr0. This was blowing up the program size as well.
    delay(duration);
  }
}
