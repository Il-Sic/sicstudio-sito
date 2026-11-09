"""Le classi del foglio di stile che nessuna pagina usa più: le regole rimaste dalle prove.

    python3 -I _lavoro/strumenti/regole-morte.py

Cerca ogni classe dei selettori di style.css negli attributi class delle pagine (anche dentro gli SVG), nei disegni
SVG di img/ e nel foglio stesso fuori dai selettori (per esempio nei nomi delle animazioni no). Dice le classi che non
si trovano e quanti byte pesano le regole che le usano da sole.
"""
import pathlib, re

SITO = pathlib.Path(__file__).resolve().parents[2]
css = (SITO / "style.css").read_text(encoding="utf-8")
usate = set()
for f in list(SITO.rglob("*.html")) + list((SITO / "img").rglob("*.svg")):
    if "_lavoro" in f.parts:
        continue
    for valore in re.findall(r'class="([^"]*)"', f.read_text(encoding="utf-8")):
        usate.update(valore.split())
# Le regole al livello più basso (anche dentro @media e @supports): selettori { dichiarazioni }.
senza_commenti = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
morte, pesi = {}, {}
for m in re.finditer(r"([^{}@;]+)\{([^{}]*)\}", senza_commenti):
    selettori = m.group(1).strip()
    if not selettori or selettori.startswith(("from", "to")) or re.match(r"^[\d.%, ]+$", selettori):
        continue
    for sel in (s.strip() for s in selettori.split(",")):
        classi = re.findall(r"\.(-?[_a-zA-Z][\w-]*)", re.sub(r"\[[^\]]*\]|\([^)]*\)", "", sel))
        mancanti = [c for c in classi if c not in usate]
        if mancanti:
            morte.setdefault(sel, mancanti)
            pesi[sel] = len(m.group(0)) if "," not in selettori else len(sel) + 1
for sel, mancanti in sorted(morte.items(), key=lambda x: -pesi[x[0]]):
    print(f"{pesi[sel]:5d}  {sel}   [{', '.join(mancanti)}]")
print("totale circa", sum(pesi.values()), "byte")
