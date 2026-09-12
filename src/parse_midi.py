import json

from pathlib import Path
from music21 import chord, converter, note, stream, tempo

from download_data import COMPOSERS

DURATIONS = [0.0, 0.125, 0.25, 1 / 3, 0.5, 2 / 3, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
TIME_SHIFTS = [0.0, 0.125, 0.25, 1 / 3, 0.5, 2 / 3, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
TEMPO_STEP = 5
DEFAULT_TEMPO = 120

def find_nearest_allowed_value(value, allowed_values):
    return min(allowed_values, key=lambda allowed_value: abs(allowed_value - value))

def round_tempo(bpm):
    return max(TEMPO_STEP, int(round(bpm / TEMPO_STEP) * TEMPO_STEP))

def get_tempo_changes(midi):
    tempo_changes = []
    flat_midi = midi.flatten()
    tempo_marks = flat_midi.getElementsByClass(tempo.MetronomeMark)

    for tempo_mark in tempo_marks:
        bpm = tempo_mark.getQuarterBPM()
        if bpm is None:
            continue

        tempo_changes.append((float(tempo_mark.offset), round_tempo(float(bpm))))

    if not tempo_changes or tempo_changes[0][0] > 0:
        tempo_changes.insert(0, (0.0, DEFAULT_TEMPO))
    
    return sorted(tempo_changes, key=lambda pair: pair[0])

def find_tempo_at_music_event_start(music_event_start, tempo_changes):
    tempo_at_current_event_start = DEFAULT_TEMPO

    for number_of_measure, tempo in tempo_changes:
        if number_of_measure <= music_event_start:
            tempo_at_current_event_start = tempo

    return tempo_at_current_event_start

def get_instrument_name(part, part_number):
    instrument = part.getInstrument(returnDefault=True)

    if part.partName:
        return str(part.partName)
    
    if instrument.instrumentName:
        return str(instrument.instrumentName)
    
    return f"Part_{part_number}"

def get_measure_information(music_event, part):
    measure = music_event.getContextByClass(stream.Measure)

    if measure is None:
        return 0, 0.0
    
    measure_number = measure.number
    measure_of_event_start = float(measure.getOffsetInHierarchy(part))
    music_event_start = float(music_event.getOffsetInHierarchy(part))
    position_in_measure = find_nearest_allowed_value(max(0.0, music_event_start - measure_of_event_start), TIME_SHIFTS)
    return measure_number, position_in_measure

def create_music_event(element, part, part_number, instrument_name, tempo_changes):
    music_event_start = float(element.getOffsetInHierarchy(part))
    duration = find_nearest_allowed_value(float(element.duration.quarterLength), DURATIONS)
    measure_number, position_in_measure = get_measure_information(element, part)

    if isinstance(element, note.Note):
        music_event_type = "NOTE"
        pitch = str(element.pitch)
    elif isinstance(element, chord.Chord):
        music_event_type = "CHORD"
        pitch = ".".join(str(current_pitch) for current_pitch in element.pitches)
    elif isinstance(element, note.Rest):
        music_event_type = "REST"
        pitch = "NONE"
    else:
        return None
    
    return {
        "type": music_event_type,
        "pitch": pitch,
        "duration": duration,
        "tempo": find_tempo_at_music_event_start(music_event_start, tempo_changes),
        "instrument": instrument_name,
        "part": part_number,
        "measure": measure_number,
        "position_in_measure": position_in_measure,
        "event_start": music_event_start
    }

def add_time_shifts(music_events):
    previous_event_start = None

    for music_event in music_events:
        current_event_start = music_event["event_start"]

        if previous_event_start is None:
            time_shift = 0.0
        else:
            time_shift = find_nearest_allowed_value(max(0.0, current_event_start - previous_event_start), TIME_SHIFTS) 

        music_event["time_shift"] = time_shift
        previous_event_start = current_event_start     

def extract_harmonic_events(midi):
    harmonic_midi = midi.chordify()
    harmonic_events = []

    for element in harmonic_midi.flatten().notes:
        if not isinstance(element, chord.Chord):
            continue

        ordered_pitches = sorted(element.pitches, key=lambda current_pitch: current_pitch.midi)
        pitch_names = [str(current_pitch) for current_pitch in ordered_pitches]
        root = element.root()

        harmonic_events.append(
            {
                "pitches": pitch_names,
                "root": str(root) if root is not None else None,
                "quality": element.quality,
                "duration": find_nearest_allowed_value(float(element.duration.quarterLength), DURATIONS),
                "event_start": float(element.offset)
            }
        )
    
    return harmonic_events

def parse_midi_file(file_path):
    music_events = []
    midi = converter.parse(file_path)
    tempo_changes = get_tempo_changes(midi)

    for part_number, part in enumerate(midi.parts, start=1):
        instrument_name = get_instrument_name(part, part_number)

        for element in part.recurse().notesAndRests:
            music_event = create_music_event(
                element=element, 
                part=part, 
                part_number=part_number, 
                instrument_name=instrument_name, 
                tempo_changes=tempo_changes
            )

            if music_event is not None:
                music_events.append(music_event)
    
    music_events.sort(key=lambda music_event: (music_event["event_start"], music_event["part"]))
    add_time_shifts(music_events)
    harmonic_events = extract_harmonic_events(midi)

    return {
        "music_events": music_events,
        "harmonic_events": harmonic_events
    }

def parse_midi_folder(midi_folder, parsed_folder):
    midi_folder = Path(midi_folder)
    parsed_folder = Path(parsed_folder)
    if not midi_folder.exists():
        print(f"Folder sa MIDI fajlovima ne postoji {midi_folder}")
        return
    
    parsed_folder.mkdir(parents=True, exist_ok=True)
    midi_files = sorted(midi_folder.glob("*.mid"))
    print(f"Pronadjeno {len(midi_files)} MIDI fajlova")

    for midi_file in midi_files:
        json_path = parsed_folder/f"{midi_file.stem}.json"
        if json_path.exists():
            print(f"JSON fajl {json_path} vec postoji")
            continue

        try:
            parsed_composition = parse_midi_file(midi_file)
            if not parsed_composition["music_events"]:
                print(f"Kompozicija {midi_file.name} nema dogadjaje")
                continue

            parsed_composition["file_name"] = midi_file.name
            parsed_composition["composer"] = midi_file.parent.name

            with json_path.open("w") as f:
                json.dump(parsed_composition, f, indent=2)

            print(f"Sacuvano: {json_path.name}") 
            print(f"Muzickih dogadjaja: {len(parsed_composition['music_events'])}")
            print(f"Harmonskih dogadjaja: {len(parsed_composition['harmonic_events'])}")

        except Exception as e:
            print(f"Greska pri obradi fajla {midi_file}: {e}")
    
if __name__ == "__main__":
    for composer in COMPOSERS:
        parse_midi_folder(midi_folder=Path(f"data/raw/{composer}"), parsed_folder=Path(f"data/processed/{composer}"))