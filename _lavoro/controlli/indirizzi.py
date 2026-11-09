"""Ogni indirizzo del sito pubblicato il 6/11 (la copia in _lavoro/online-6-11) c'è ancora: nessuna pagina, immagine o
file sparisce. Le pagine nuove si aggiungono senza spostare le vecchie."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, LAVORO


def main():
    vecchio = LAVORO / "online-6-11"
    problemi, visti = 0, 0
    for p in sorted(vecchio.rglob("*")):
        if not p.is_file() or p.name.startswith("."):
            continue
        visti += 1
        rel = p.relative_to(vecchio)
        if not (SITO / rel).exists():
            print(f"MANCA {rel}")
            problemi += 1
    print(f"Indirizzi: {visti} file del 6/11, {problemi} spariti")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
