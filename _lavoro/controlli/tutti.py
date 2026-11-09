"""Tutti i controlli, uno dopo l'altro, con il riassunto alla fine."""
import pathlib, subprocess, sys

QUI = pathlib.Path(__file__).resolve().parent
CONTROLLI = ["privacy", "risorse", "collegamenti", "forma", "contrasto", "pesi", "movimento", "exif", "schermate",
             "indirizzi", "apostrofi", "parole"]


def main():
    esiti = {}
    for c in CONTROLLI:
        print(f"\n===== {c} =====", flush=True)     # prima dell'uscita del controllo, anche dentro un tubo
        r = subprocess.run([sys.executable, "-I", str(QUI / f"{c}.py")])
        esiti[c] = r.returncode
    print("\n===== riassunto =====")
    for c, e in esiti.items():
        print(f"{c:13} {'ok' if e == 0 else 'DA VEDERE'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
