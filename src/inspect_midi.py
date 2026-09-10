import sys
from pathlib import Path
from music21 import chord, converter, note


def inspect_midi(file_path):
    midi_path = Path(file_path)

    if not midi_path.exists():
        print(f"Fajl {midi_path} ne postoji")
        return

    composition = converter.parse(midi_path)
    print(f"Broj delova: {len(composition.parts)}")
    for part_number, part in enumerate(composition.parts, start=1):
        instrument = part.getInstrument()

        print(f"Deo {part_number}")
        print(f"Instrument {instrument.instrumentName}")
        
        print("Prvih 10 događaja:")
        events = list(part.flatten().notesAndRests)
        print(f"Broj događaja: {len(events)}")

        for event in events[:10]:
            if isinstance(event, note.Note):
                print(f"  NOTA: {event.pitch.nameWithOctave}, početak={event.offset}, trajanje={event.duration.quarterLength}")

            elif isinstance(event, chord.Chord):
                pitches = [pitch.nameWithOctave for pitch in event.pitches]
                print(f"  AKORD: {pitches}, početak={event.offset}, trajanje={event.duration.quarterLength}")

            elif isinstance(event, note.Rest):
                print(f"  PAUZA, početak={event.offset}, trajanje={event.duration.quarterLength}")

        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Upotreba: python src/inspect_midi.py putanja_do_midi_fajla")
    else:
        inspect_midi(sys.argv[1])