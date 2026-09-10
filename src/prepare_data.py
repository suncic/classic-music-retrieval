import json
from pathlib import Path
from parse_midi import parse_midi

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_FOLDER = PROJECT_ROOT/"data"/"raw"
PROCESSED_DATA_FOLDER = PROJECT_ROOT/"data"/"processed"

def prepare_composition(midi_path):
    composer_name = midi_path.parent.name
    composition = parse_midi(midi_path)

    composition["composer"] = composer_name
    composer_output_folder = PROCESSED_DATA_FOLDER/composer_name
    composer_output_folder.mkdir(parents=True, exist_ok=True)

    output_path = composer_output_folder/(midi_path.stem + ".json")
    with output_path.open("w") as f:
        json.dump(composition, f, indent=2)

def prepare_all_compositions():
    midi_paths = sorted(RAW_DATA_FOLDER.rglob("*.mid"))
    print(f"Pronadjeno {len(midi_paths)} MIDI fajlova")

    successful_count = 0
    failed_count = 0

    for midi_path in midi_paths:
        try:
            prepare_composition(midi_path)
            successful_count += 1

        except Exception as e:
            failed_count += 1
            print(f"Greska za {midi_path}: {e}")

    print()
    print(f"Uspesno obradjeno {successful_count} kompozicija")
    print(f"Nespesno obradjeno {failed_count} kompozicija")

if __name__ == "__main__":
    prepare_all_compositions()