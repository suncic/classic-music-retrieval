import streamlit as st

st.set_page_config(page_title="Pretrazivanje klasicne muzike", page_icon="🎼", layout="wide")
st.title("Pretrazivanje klasicnih kompozicija")
st.write("Ucitajte MIDI odlomak kako biste pronasli najslicnije kompozicije iz kolekcije")

uploaded_file = st.file_uploader("Izaberite fajl", type=["mid", "midi"])
if uploaded_file is not None:
    st.success(f"Fajl {uploaded_file.name} je uspesno ucitan.")

    if st.button("Pretrazi kompozicije"):
        st.info("u nastavku...")