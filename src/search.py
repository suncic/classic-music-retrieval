import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Upotreba search.py: python src/search.py putanja_do_upita.mid [broj_rezultata]")
        sys.exit()

    query_file_path = sys.argv[1]