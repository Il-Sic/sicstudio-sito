"""Nessun apostrofo dritto (') nel testo delle pagine: dappertutto quello tipografico (’), tranne la privacy e le sue
frasi citate parola per parola. Per sistemarli: python3 -I _lavoro/strumenti/apostrofi.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "strumenti"))
from comune import pagine, nome  # noqa: E402
from apostrofi import sistema  # noqa: E402


def main():
    problemi = 0
    for p in pagine():
        if nome(p).startswith("argonauta/privacy/"):
            continue
        prima = p.read_text(encoding="utf-8")
        dopo = sistema(prima)
        if dopo != prima:
            print(f"APOSTROFI {nome(p)}: {prima.count(chr(39)) - dopo.count(chr(39))} dritti da cambiare")
            problemi += 1
    print(f"Apostrofi: {problemi} pagine da sistemare")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
