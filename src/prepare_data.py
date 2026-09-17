import json
from pathlib import Path

from download_data import COMPOSERS

SEGMENT_LENGTH = 4
SEGMENT_STEP = 2

PROCESSED_DATA_FOLDER = Path("data/processed")
PREPARED_DATA_FOLDER = Path("data/prepared")

def load_composition(file_path):
    with file_path.open("r") as f:
        return json.load(f)

def get_measure_numbers(music_events):
    measure_numbers = set()
    for event in music_events:
        measure_number = event["measure"]
        if isinstance(measure_number, int) and measure_number > 0:
            measure_numbers.add(measure_number)

    return sorted(measure_numbers)

def select_music_events(music_events, selected_measures):
    return [music_event for music_event in music_events if music_event["measure"] in selected_measures]

def select_harmonic_events(harmonic_events, segment_start, segment_end):
    return [harmonic_event for harmonic_event in harmonic_events if segment_start <= harmonic_event["event_start"] < segment_end]

def create_pitch_token(music_event):
    event_type = music_event["type"]
    if event_type == "REST":
        return "REST"
    
    pitch = music_event["pitch"]
    return f"{event_type}_{pitch}"

def create_rhythm_token(music_event):
    event_type, duration, time_shift = music_event["type"], music_event["duration"], music_event["time_shift"]
    return f"{event_type}_D{duration}_T{time_shift}"

def create_combined_token(music_event):
    event_type, pitch, duration, time_shift = music_event["type"], music_event["pitch"], music_event["duration"], music_event["time_shift"]
    return f"{event_type}_{pitch}_D{duration}_T{time_shift}"

def create_harmonic_token(harmonic_event):
    root, quality, duration = harmonic_event["root"], harmonic_event["quality"], float(harmonic_event["duration"])
    if root is None:
        root = "UNKNOWN"

    if not quality:
        quality = "unknown"
    
    return f"HARMONY_{root}_{quality}_D{duration}"

def create_segment(composition, selected_measures, segment_number):
    music_events = select_music_events(composition["music_events"], selected_measures)
    if not music_events:
        return None
    
    pitch_tokens = [create_pitch_token(music_event) for music_event in music_events]
    rhythm_tokens = [create_rhythm_token(music_event) for music_event in music_events]
    combined_tokens = [create_combined_token(music_event) for music_event in music_events]

    segment_start = min(music_event["event_start"] for music_event in music_events)
    segment_end = max(music_event["event_start"] + music_event["duration"] for music_event in music_events)
    harmonic_events = select_harmonic_events(composition["harmonic_events"], segment_start, segment_end)
    harmonic_tokens = [create_harmonic_token(harmonic_event) for harmonic_event in harmonic_events]

    composition_name = Path(composition["file_name"]).stem
    segment_id = f"{composition['composer']}_{composition_name}_{segment_number}"
    return{
        "segment_id": segment_id,
        "composer": composition["composer"],
        "file_name": composition["file_name"],
        "start_measure": selected_measures[0],
        "end_measure": selected_measures[-1],
        "start_time": segment_start,
        "end_time": segment_end,
        "pitch_tokens": pitch_tokens,
        "rhythm_tokens": rhythm_tokens,
        "combined_tokens": combined_tokens,
        "harmonic_tokens": harmonic_tokens
    }

def create_composition_segments(composition):
    measure_numbers = get_measure_numbers(composition["music_events"])
    
    segments = []
    segment_number = 1

    for start_index in range(0, len(measure_numbers), SEGMENT_STEP):
        selected_measures = measure_numbers[start_index:start_index + SEGMENT_LENGTH]

        if len(selected_measures) < 2:
            continue

        segment = create_segment(composition, selected_measures, segment_number)
        if segment is not None:
            segments.append(segment)
            segment_number += 1

    return segments

if __name__ == "__main__":
    for composer in COMPOSERS:
        composer_folder = PROCESSED_DATA_FOLDER/composer
        json_files = sorted(composer_folder.glob("*.json"))

        prepared_composer_folder = PREPARED_DATA_FOLDER/composer
        prepared_composer_folder.mkdir(parents=True, exist_ok=True)

        print(f"Priprema podataka za {composer}")

        for json_path in json_files:
            output_path = prepared_composer_folder/json_path.name
            try:
                composition = load_composition(json_path)
                composition_segments = create_composition_segments(composition)
                prepared_composition = {
                    "composer": composition["composer"],
                    "file_name": composition["file_name"],
                    "number_of_segments": len(composition_segments),
                    "segments": composition_segments
                }
                print(f"Od {json_path.name} napravljeno {len(composition_segments)} segmenata")

                with output_path.open("w") as f:
                    json.dump(prepared_composition, f, indent=2)

            except Exception as e:
                print(f"Greska prilikom obrade {json_path}: {e}")

    print("Zavrseno pripremanje podataka")
        