import os
import json
from pathlib import Path

from download_data import COMPOSERS

def load_composition(file_path):
    with file_path.open("r") as f:
        return json.load(f)

def get_measure_numbers(music_events):
    measure_numbers = set()

    for event in music_events:
        measure_numbers.add(event["measure"])

    return sorted(measure_numbers)

def create_composition_segments(composition):
    music_events = composition["music_events"]
    measure_numbers = get_measure_numbers(music_events)

def prepare_all_compositions():
    all_segments = []

    for composer in COMPOSERS:
        composer_folder = Path(f"data/processed/{composer}")
        json_files = sorted(composer_folder.glob("*.json"))

        for json_path in json_files:
            try:
                composition = load_composition(json_path)
                composition_segments = create_composition_segments(composition)
            except Exception as e:
                pass