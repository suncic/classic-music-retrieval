import sys
import gc
import json
import joblib

from pathlib import Path
from prepare_data import PREPARED_DATA_FOLDER
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

NGRAM_RANGE = (1, 2)
INDEX_FOLDER = Path("data/index")
TOKEN_GROUPS = {
    "pitch": "pitch_tokens",
    "rhythm": "rhythm_tokens",
    "combined": "combined_tokens",
    "harmonic": "harmonic_tokens"
}

def load_segments_metadata(prepared_files):
    metadata = []
    matrix_row = 0

    for file_path in prepared_files:
        with file_path.open("r") as f:
            composition = json.load(f)

        for segment in composition["segments"]:
            metadata.append({
                "matrix_row": matrix_row,
                "segment_id": segment["segment_id"],
                "composer": segment["composer"],
                "file_name": segment["file_name"],
                "start_measure": segment["start_measure"],
                "end_measure": segment["end_measure"],
                "start_time": segment["start_time"],
                "end_time": segment["end_time"]
            })
            matrix_row += 1

    return metadata

def load_documents(prepared_files, token_field):
    documents = []
    for file_path in prepared_files:
        with file_path.open("r") as f:
            composition = json.load(f)

        for segment in composition["segments"]:
            tokens = segment[token_field]
            documents.append(" ".join(tokens))

    return documents

def build_vector_space(prepared_files, representation_name, token_field):
    print(f"Pravljenje TF-IDF reprezentacije {representation_name}")
    documents = load_documents(prepared_files, token_field)
    if not documents:
        raise ValueError("Nije pronadjen nijedan segment")
    
    if not any(document.strip() for document in documents):
        raise ValueError(f"Svi dokumenti za reprezentaciju {representation_name} su prazni")
    
    vectorizer = TfidfVectorizer(lowercase=False, token_pattern=r"(?u)\S+", ngram_range=NGRAM_RANGE, sublinear_tf=True, norm="l2")
    tfidf_matrix = vectorizer.fit_transform(documents)

    vectorizer_path = INDEX_FOLDER/f"{representation_name}_vectorizes.pkl"
    matrix_path = INDEX_FOLDER/f"{representation_name}_matrix.npz"
    joblib.dump(vectorizer, vectorizer_path)
    save_npz(matrix_path, tfidf_matrix, compressed=True)

    print(f"Broj segmenata: {tfidf_matrix.shape[0]}")
    print(f"Broj TF-IDF karakteristika: {tfidf_matrix.shape[1]}")

    del documents
    del vectorizer
    del tfidf_matrix
    gc.collect()

if __name__ == "__main__":
    prepared_files = sorted(PREPARED_DATA_FOLDER.rglob("*.json"))
    if not prepared_files:
        print(f"Nisu pronadjeni pripremljeni podaci")
        sys.exit()
    
    print(f"Pronadjeno {len(prepared_files)} pripremljenih kompozicija")

    INDEX_FOLDER.mkdir(parents=True, exist_ok=True)
    metadata = load_segments_metadata(prepared_files)
    metadata_path = INDEX_FOLDER/"segments_metadata.json"
    with metadata_path.open("w") as f:
        json.dump(metadata, f, indent=2)

    for representation_name, token_field in TOKEN_GROUPS.items():
        build_vector_space(prepared_files, representation_name, token_field)
    
    print("Zavrseno pravljenje indeksa za pretragu.")
