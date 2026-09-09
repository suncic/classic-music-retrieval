# Classical Music Retrieval

Sistem za pretrazivanje klasicnih kompozicija na osnovu slicnosti melodijskih, ritmickih i harmonskih obrazaca izdvojenih iz MIDI zapisa.

## Cilj projekta

Korisnik aplikaciji prosledjuje kraći MIDI odlomak, nakon cega sistem pretrazuje kolekciju klasicnih kompozicija i vraća rangiranu listu najslicnijih rezultata.

## Planirane funkcionalnosti

- ucitavanje i obrada MIDI fajlova;
- izdvajanje nota, intervala, trajanja i akorda;
- formiranje muzickih n-grama;
- racunanje melodijske, ritmicke i harmonske slicnosti;
- rangiranje kompozicija;
- prikaz rezultata kroz Streamlit aplikaciju.

## Tehnologije

- Python
- music21
- NumPy
- pandas
- scikit-learn
- Streamlit

## Pokretanje projekta

Aktiviranje virtuelnog okruzenja:

```bash
source .venv/bin/activate
```
Pokretanje streamlit aplikacije:

```bash
streamlit run app/app.py