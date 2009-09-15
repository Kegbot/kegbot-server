#ifndef BUZZER_H
#define BUZZER_H

struct MelodyNote {
  int octave;
  int note;
  int duration;
};

void setupBuzzer();
void playMidiNote(int octave, int note);
void playMelody(struct MelodyNote* melody);

#endif // BUZZER_H
