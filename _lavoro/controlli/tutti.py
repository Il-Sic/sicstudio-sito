"""Tutti i controlli, uno dopo l'altro, con il riassunto alla fine. Esce con 1 se almeno un controllo ha trovato
qualcosa: così se ne accorge anche chi non legge il riassunto, come GitHub a ogni pull request
(.github/workflows/controlli.yml)."""
import pathlib, subprocess, sys

QUI = pathlib.Path(__file__).resolve().parent
CONTROLLI = ["privacy", "risorse", "collegamenti", "forma", "contrasto", "pesi", "movimento", "exif", "schermate",
             "indirizzi", "apostrofi", "parole", "tavola"]
# Un controllo che non ha potuto guardare esce con 3: non è un problema, ma nel riassunto non deve sembrare «ok».
# Lo fa parole.py quando manca la sua lista, che sta solo sul Mac: su GitHub è sempre così.
SALTATO = 3


def main():
    esiti = {}
    for c in CONTROLLI:
        print(f"\n===== {c} =====", flush=True)     # prima dell'uscita del controllo, anche dentro un tubo
        r = subprocess.run([sys.executable, "-I", str(QUI / f"{c}.py")])
        esiti[c] = r.returncode
    print("\n===== riassunto =====")
    for c, e in esiti.items():
        print(f"{c:13} {'ok' if e == 0 else 'saltato' if e == SALTATO else 'DA VEDERE'}")
    return 1 if any(e not in (0, SALTATO) for e in esiti.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
