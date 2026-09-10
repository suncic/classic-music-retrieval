from pathlib import Path
from music21 import chord, converter, note

def parse_music_event(event):
    if isinstance(event, note.Note):
        return {
            "type": "NOTE",
            "pitches": [event.pitch.nameWithOctave],
            "midi_pitches": [event.pitch.midi],
            "offset": float(event.offset),
            "duration": float(event.duration.quarterLength)
        }

    elif isinstance(event, chord.Chord):
        return {
            "type": "CHORD",
            "pitches": [pitch.nameWithOctave for pitch in event.pitches],
            "midi_pitches": [pitch.midi for pitch in event.pitches],
            "offset": float(event.offset),
            "duration": float(event.duration.quarterLength)
        }
    
    elif isinstance(event, note.Rest):
        return {
            "type": "REST",
            "pitches": [],
            "midi_pitches": [],
            "offset": float(event.offset),
            "duration": float(event.duration.quarterLength)
        }
    
    else:
        return None
    
def parse_midi(file_path):
    midi_path = Path(file_path)

    if not midi_path.exists():
        raise FileNotFoundError(f"Fajl {midi_path} ne postoji")
    
    composition = converter.parse(midi_path)
    parsed_parts = []

    for part_number, part in enumerate(composition.parts, start=1):
        instrument = part.getInstrument()
        parsed_events = []

        for event in part.flatten().notesAndRests:
            parsed_event = parse_music_event(event)

            if parsed_event is not None:
                parsed_events.append(parsed_event)

        parsed_parts.append({
            "part_number": part_number,
            "instrument": instrument.instrumentName,
            "events": parsed_events
        })

    return {
        "file_name": midi_path.name,
        "file_path": str(midi_path),
        "number_of_parts": len(parsed_parts),
        "parts": parsed_parts
    }

if __name__ == "__main__":
    composition = parse_midi("data/raw/bach/bwv1.6.mid")

    for part in composition["parts"]:
        print(f"Deo {part['part_number']}: {len(part['events'])} dogadjaja")
        print(part["events"][:3])
        print()