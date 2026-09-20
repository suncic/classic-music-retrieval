# Classical Music Retrieval

Sistem za pretrazivanje klasicnih kompozicija na osnovu slicnosti tonskih, ritmickih i harmonskih obrazaca izdvojenih iz MIDI zapisa.

## Cilj projekta

Korisnik aplikaciji prosledjuje kraci MIDI odlomak, nakon cega sistem pretrazuje kolekciju klasicnih kompozicija i vraca rangiranu listu najslicnijih rezultata.

## Funkcionalnosti

- ucitavanje i obrada MIDI fajlova;
- izdvajanje nota, akorda, pauza i njihovih trajanja;
- formiranje muzickih n-grama;
- izracunavanje tonske, ritmicke, kombinovane i harmonske slicnosti;
- rangiranje pronadjenih kompozicija;
- prikaz rezultata kroz Streamlit aplikaciju.

## Tehnologije

- Python
- music21
- NumPy
- pandas
- SciPy
- scikit-learn
- Streamlit
- Docker

## Pokretanje aplikacije pomocu Dockera

Aplikacija se preuzima sa Docker Hub-a i pokrece komandom:

```bash
docker run --rm -p 8501:8501 suncic/classic-music-retrieval:latest
```