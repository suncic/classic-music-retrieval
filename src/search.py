import sys
import json
import joblib
import numpy as np

from pathlib import Path
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

from build_index import INDEX_FOLDER, TOKEN_GROUPS
from parse_midi import parse_midi_file
from prepare_data import create_combined_token, create_harmonic_token, create_pitch_token, create_rhythm_token

SIMILARITY_WEIGHTS = {
    "pitch": 0.3,
    "rhythm": 0.2,
    "combined": 0.3,
    "harmonic": 0.2
}

def load_metadata():
    metadata_path = INDEX_FOLDER/"segments_metadata.json"
    with metadata_path.open("r") as f:
        return json.load(f)

def create_query_tokens(parsed_query):
    music_events = parsed_query["music_events"]
    harmonic_events = parsed_query["harmonic_events"]
    return {
        "pitch": [create_pitch_token(music_event) for music_event in music_events],
        "rhythm": [create_rhythm_token(music_event) for music_event in music_events],
        "combined": [create_combined_token(music_event) for music_event in music_events],
        "harmonic": [create_harmonic_token(harmonic_event) for harmonic_event in harmonic_events]
    }

def load_vectorizer(representation_name):
    vectorizer_path = INDEX_FOLDER/f"{representation_name}_vectorizer.pkl"
    return joblib.load(vectorizer_path)

def load_tfidf_matrix(representation_name):
    matrix_path = INDEX_FOLDER/f"{representation_name}_matrix.npz"
    return load_npz(matrix_path)

def calculate_representation_similarity(representation_name, query_tokens):
    if not query_tokens:
        return None
    
    query_document = " ".join(query_tokens)
    vectorizer = load_vectorizer(representation_name)
    tfidf_matrix = load_tfidf_matrix(representation_name)
    query_vector = vectorizer.transform([query_document])
    if query_vector.nnz == 0:
        return None
    
    return cosine_similarity(query_vector, tfidf_matrix).flatten()

def calculate_all_similarities(query_tokens):
    representation_similarities = {}
    for representation_name in TOKEN_GROUPS:
        similarities = calculate_representation_similarity(representation_name, query_tokens[representation_name])
        if similarities is not None:
            representation_similarities[representation_name] = similarities
    return representation_similarities

def calculate_final_similarities(representation_similarities, number_of_segments):
    final_similarities = np.zeros(number_of_segments, dtype=float)
    total_weight = 0.0

    for representation_name, similarities in representation_similarities.items():
        weight = SIMILARITY_WEIGHTS[representation_name]
        final_similarities += weight * similarities
        total_weight += weight
    
    if total_weight == 0:
        raise ValueError("Upit nema tokene koji postoje u indeksu")
    
    return final_similarities / total_weight

def create_ranked_results(metadata, final_similarities, representation_similarities, top_k):
    sorted_indices = np.argsort(final_similarities)[::-1]
    results = []
    found_compositions = set()

    for matrix_row in sorted_indices:
        segment_metadata = metadata[matrix_row]
        composition_key = (segment_metadata["composer"], segment_metadata["file_name"])

        if composition_key in found_compositions:
            continue

        result = {**segment_metadata, "final_similarity": float(final_similarities[matrix_row])}

        for representation_name in TOKEN_GROUPS:
            similarities = representation_similarities.get(representation_name)
            if similarities is None:
                similarity_value = None
            else:
                similarity_value = float(similarities[matrix_row])

            result[f"{representation_name}_similarity"] = similarity_value
        
        results.append(result)
        found_compositions.add(composition_key)

        if len(results) >= top_k:
            break

    return results

def search_compositions(query_path, top_k):
    query_path = Path(query_path)
    if not query_path.exists():
        raise FileNotFoundError(f"Upitni MIDI fajl ne postoji {query_path}")
    
    metadata = load_metadata()
    if not metadata:
        raise ValueError("Indeks ne sadrzi nijedan segment")
    
    parsed_query = parse_midi_file(query_path)
    query_tokens = create_query_tokens(parsed_query)

    representation_similarities = calculate_all_similarities(query_tokens)
    final_similarities = calculate_final_similarities(representation_similarities, len(metadata))
    return create_ranked_results(metadata, final_similarities, representation_similarities, top_k)

def print_results(results):
    if not results:
        print("Nisu pronadjeni rezultati")
        return

    for position, result in enumerate(results, start=1,):
        print()
        print(f"{position}. {result['composer']} — {result['file_name']}")
        print(f"Taktovi: {result['start_measure']}–{result['end_measure']}")
        print(f"Konacna slicnost: {result['final_similarity']:.4f}")

        for representation_name in TOKEN_GROUPS:
            similarity = result[f"{representation_name}_similarity"]
            if similarity is not None:
                print(f"{representation_name}: {similarity:.4f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Upotreba search.py: python src/search.py putanja_do_upita.mid [broj_rezultata]")
        sys.exit()

    query_file_path = sys.argv[1]
    if len(sys.argv) >= 3:
        number_of_results = int(sys.argv[2])
    else:
        number_of_results = 5

    search_results = search_compositions(query_path=query_file_path, top_k=number_of_results)
    print_results(search_results)