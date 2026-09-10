import json

from parse_midi import parse_midi

def select_melodic_pitch(event):
    if event["type"] == "NOTE":
        return event["midi_pitches"][0]
    elif event["type"] == "CHORD":
        return max(event["midi_pitches"])
    else:
        return None

def extract_part_features(events):
    pitches = []
    durations = []
    offsets = []

    for event in events:
        pitch = select_melodic_pitch(event)

        if pitch is None:
            continue

        pitches.append(pitch)
        durations.append(event["duration"])
        offsets.append(event["offset"])

    pitch_tokens = [f"P{pitch}" for pitch in pitches]

    interval_tokens = []
    for index in range(1, len(pitches)):
        interval = pitches[index] - pitches[index-1]
        interval_tokens.append(f"I{interval:+d}")

    rhythm_tokens = [f"D{duration:g}" for duration in durations]

    combined_tokens = []
    for index in range(1, len(pitches)):
        interval = pitches[index] - pitches[index-1]
        duration = durations[index]
        combined_tokens.append(f"I{interval:+d}_D{duration:g}")

    return {
        "pitches": pitches,
        "durations": durations,
        "offsets": offsets,
        "pitch_tokens": pitch_tokens,
        "interval_tokens": interval_tokens,
        "rhythm_tokens": rhythm_tokens,
        "combined_tokens": combined_tokens
    }

def extract_composition_features(composition):
    parts_with_features = []

    for part in composition["parts"]:
        features = extract_part_features(part["events"])
        parts_with_features.append(
            {
                "part_number": part["part_number"],
                "instrument": part["instrument"],
                "features": features
            }
        )
    
    return {
        "file_name": composition["file_name"],
        "file_path": composition["file_path"],
        "number_of_parts": composition["number_of_parts"],
        "parts": parts_with_features
    }

if __name__ == "__main__":
    composition = parse_midi("data/raw/bach/bwv1.6.mid")
    composition_features = extract_composition_features(composition)

    for part in composition_features["parts"]:
        features = part["features"]

        print(f"Deo {part['part_number']}")
        print(f"Tonovi: {features['pitch_tokens'][:10]}")
        print(f"Intervali: {features['interval_tokens'][:10]}")
        print(f"Ritam: {features['rhythm_tokens'][:10]}")
        print(f"Kombinovano: {features['combined_tokens'][:10]}")
        print()