"""Ogni animazione si ferma con «Riduci movimento» (prefers-reduced-motion: reduce).

Nel CSS del sito: ci dev'essere la regola che spegne animazioni e transizioni per tutti gli elementi dentro
@media (prefers-reduced-motion: reduce). Negli SVG con animazioni proprie, la stessa regola dentro il file;
niente animazioni SMIL (<animate>), che il CSS non ferma.
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import file_del_sito, pagine, nome

REGOLA = re.compile(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{.{0,800}?animation:\s*none\s*!important", re.S)


def main():
    problemi = 0
    animazioni = 0
    for p in list(file_del_sito(".css", ".svg")):
        t = p.read_text(encoding="utf-8")
        n = len(re.findall(r"animation(-name)?\s*:(?!\s*none)", t))
        animazioni += n
        if n and not REGOLA.search(t) and p.suffix == ".svg":
            print(f"{nome(p)}: {n} animazioni senza la regola di «Riduci movimento»"); problemi += 1
        if p.suffix == ".css" and n and not REGOLA.search(t):
            print(f"{nome(p)}: {n} animazioni senza la regola di «Riduci movimento»"); problemi += 1
        if re.search(r"<animate|<animateTransform|<animateMotion|<set\b", t):
            print(f"{nome(p)}: animazioni SMIL"); problemi += 1
    for p in pagine():
        if re.search(r"<animate|<animateTransform|<animateMotion|<set\b", p.read_text(encoding="utf-8")):
            print(f"{nome(p)}: animazioni SMIL"); problemi += 1
    print(f"Movimento: {animazioni} dichiarazioni di animazione, {problemi} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
