"""Ogni indirizzo del sito pubblicato il 6/11 (la copia in _lavoro/online-6-11) c'è ancora: nessuna pagina, immagine o
file sparisce. Le pagine nuove si aggiungono senza spostare le vecchie. Fanno eccezione solo i file tolti apposta, in
TOLTI, con il giorno e il perché."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, LAVORO

# L'8/11 (commit 07eb422): immagini che nessuna pagina usava più.
TOLTI = {
    "img/carta-viaggio.svg", "img/rosa-dei-venti.svg", "img/timbro.svg",
    "img/schermate/equipaggio-chiaro.jpg", "img/schermate/equipaggio-scuro.jpg",
    "img/schermate/orfeo-chiaro.jpg", "img/schermate/orfeo-scuro.jpg",
}


def main():
    vecchio = LAVORO / "online-6-11"
    problemi, visti, tolti = 0, 0, 0
    for p in sorted(vecchio.rglob("*")):
        if not p.is_file() or p.name.startswith("."):
            continue
        visti += 1
        rel = p.relative_to(vecchio)
        if (SITO / rel).exists():
            continue
        if rel.as_posix() in TOLTI:
            tolti += 1
        else:
            print(f"MANCA {rel}")
            problemi += 1
    print(f"Indirizzi: {visti} file del 6/11, {problemi} spariti, {tolti} tolti apposta")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
