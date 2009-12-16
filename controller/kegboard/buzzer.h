#ifndef BUZZER_H
#define BUZZER_H

// Melody note:
//  1 bit  reserved
//  3 bits for octave (0-5),
//  4 bits for note (0-11),
//  8 bits for duration (0-255),
#define MELODY_NOTE(octave, note, duration) \
	(((octave & 0x7) << 12) | ((note & 0xf) << 8) | (duration & 0xff))

#define OCTAVE(melody_note) ((melody_note >> 12) & 0x7)
#define NOTE(melody_note) ((melody_note >> 8) & 0xf)
#define DURATION(melody_note) (melody_note & 0xff)

#define NOTE_SILENCE  0xf

#include <avr/pgmspace.h>

void setupBuzzer();
void playMidiNote(uint8_t octave, uint8_t note);
void playMelody(prog_uint16_t* notes);

#endif // BUZZER_H
