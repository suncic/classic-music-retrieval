import sys
import tempfile
import pandas as pd
import streamlit as st
from pathlib import Path

POJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_FOLDER = POJECT_ROOT/"src"
if str(SRC_FOLDER) not in sys.path:
    sys.path.insert(0, str(SRC_FOLDER))

from search import search_compositions

st.set_page_config(page_title="Pretrazivanje klasicne muzike", page_icon="🎼", layout="wide")
st.title("Pretrazivanje klasicnih kompozicija")
st.write("Ucitajte MIDI odlomak kako biste pronasli najslicnije kompozicije iz kolekcije")

uploaded_file = st.file_uploader("Izaberite fajl", type=["mid", "midi"])
number_of_results = st.slider("Broj rezultata", min_value=1, max_value=20, value=5)
if uploaded_file is not None:
    st.success(f"Fajl {uploaded_file.name} je uspesno ucitan.")

search_button = st.button("Pretrazi kompozicije", type="primary", disabled=uploaded_file is None)
if search_button:
    temporary_path = None

    try:
        file_sufix = Path(uploaded_file.name).suffix or ".mid"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_sufix) as temporary_file:
            temporary_file.write(uploaded_file.getvalue())
            temporary_path = Path(temporary_file.name)

        with st.spinner("Obrada MIDI odlomka i pretrazivanje..."):
            results = search_compositions(query_path=temporary_path, top_k=number_of_results)

        if not results:
            st.warning("Nisu pronadjene slicne kompozicije")
        else:
            st.subheader("Rezultati pretrage")
            for position, result in enumerate(results, start=1):
                composer = result["composer"]
                file_name = result["file_name"]
                final_similarity = result["final_similarity"]

                with st.container(border=True):
                    first_column, second_column = st.columns([3, 1])
                    with first_column:
                        st.markdown(f"### {position}. {composer} - {file_name}")
                        st.write(f"Pronadjeni takovi {result['start_measure']}-{result['end_measure']}")
                    with second_column:
                        st.metric(f"Konacna slicnost", f"{final_similarity * 100:.2f}%")

                    progress_value = min(max(final_similarity, 0.0), 1.0)
                    st.progress(progress_value)

                    similarity_columns = st.columns(4)
                    similarity_names = [
                        ("pitch", "Tonska"),
                        ("rhythm", "Ritmicka"),
                        ("combined", "Kombinovana"),
                        ("harmonic", "Harmonska"),
                    ]

                    for column, (representation_name, label) in zip(similarity_columns, similarity_names):
                        similarity = result.get(f"{representation_name}_similarity")
                        with column:
                            if similarity is None:
                                st.metric(label, "N/A")
                            else:
                                st.metric(label, f"{similarity * 100:.2f}%")
            table_rows = []
            for position, result in enumerate(results, start=1):
                table_rows.append(
                    {
                        "Rang": position,
                        "Kompozitor": result["composer"].capitalize(),
                        "Kompozicija": result["file_name"],
                        "Taktovi": f"{result['start_measure']}–{result['end_measure']}",
                        "Slicnost": round(result["final_similarity"] * 100, 2)
                    })

            st.subheader("Sazeti prikaz")
            results_table = pd.DataFrame(table_rows)
            st.dataframe(results_table, use_container_width=True, hide_index=True)        

    except Exception as e:
        st.error(f"Doslo je do greske prilikom pretrage: {e}")
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()