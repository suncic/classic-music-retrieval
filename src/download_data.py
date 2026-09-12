from pathlib import Path
from music21 import corpus

COMPOSERS = ["bach", "mozart", "beethoven"]
COMPOSITIONS_PER_COMPOSER = 20

def download_pieces(composer_name, output_folder):
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"Preuzimanje kompozicija od {composer_name}")
    composition_paths = corpus.getComposer(composer_name)
    print(f"Pronadjeno {len(composition_paths)} kompozicija")

    saved_count = 0
    skipped_count = 0
    failed_count = 0

    for composition_path in composition_paths[:COMPOSITIONS_PER_COMPOSER]:
        try:
            original_name = Path(str(composition_path)).stem
            file_name = f"{original_name}.mid"
            full_path = output_folder/file_name

            if full_path.exists():
                skipped_count += 1
                print(f"Fajl {file_name} vec postoji")
                continue

            composition = corpus.parse(composition_path)
            composition.write("midi", fp=str(full_path))
            saved_count += 1
            print(f"Sacuvan fajl {file_name}")

        except Exception as e:
            failed_count += 1
            print(f"Greska pri obradi kompozicije {composition_path}: {e}")

    print(f"Zavrsena obrada kompozitora {composer_name}")
    print(f"Preuzeto {saved_count} kompozicija")
    print(f"Preskoceno {skipped_count} kompozicija")
    print(f"Neuspesno obradjeno {failed_count} kompozicija")

if __name__ == "__main__":
    for composer in COMPOSERS:
        download_pieces(composer, Path(f"data/raw/{composer}"))