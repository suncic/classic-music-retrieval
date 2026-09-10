from pathlib import Path
from music21 import corpus

COMPOSERS = ["bach", "mozart", "beethoven"]
COMPOSITIONS_PER_COMPOSER = 20

def download_pieces(composer_name, data_folder):
    data_folder.mkdir(parents=True, exist_ok=True)
    composition_paths = corpus.getComposer(composer_name)

    saved_count = 0
    for composition_path in composition_paths[:COMPOSITIONS_PER_COMPOSER]:
        try:
            original_name = Path(str(composition_path)).stem
            file_name = f"{original_name}.mid"
            full_path = data_folder/file_name

            if full_path.exists():
                print(f"Fajl {file_name} vec postoji")
                continue

            composition = corpus.parse(composition_path)
            composition.write("midi", fp=str(full_path))
            saved_count += 1
            print(f"Sacuvan fajl {file_name}")

        except Exception as e:
            print(f"Greska pri obradi kompozicije {composition_path}: {e}")

    print(f"Zavrsena obrada kompozitora {composer_name}")
    print(f"Preuzeto {saved_count} kompozicija")

if __name__ == "__main__":
    for composer in COMPOSERS:
        download_pieces(composer, Path(f"data/raw/{composer}"))