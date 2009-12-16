#ifndef BUZZER_H
#define BUZZER_H

struct MelodyNote {
  int8_t octave;
  int8_t note;
  int8_t duration;
};

void setupBuzzer();
void playMidiNote(int8_t octave, int8_t note);
void playMelody(struct MelodyNote* melody);

#endif // BUZZER_H
