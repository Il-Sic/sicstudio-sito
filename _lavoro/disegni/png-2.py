"""Le immagini PNG e JPEG della seconda passata, fatte con qlmanage e sips (niente altro da installare):
- apple-touch-icon.png, 180×180, il marchio su carta (disegni/marchio-quadrato-2.svg);
- favicon.ico, 32×32, il marchio di giorno (img/icona.svg) per Safari, che non usa le icone SVG;
L'anteprima dei link dello studio (img/anteprima-studio.jpg) dal 7/11 la fa disegni/anteprima-studio.py, dal paesaggio
vero della home; quella di Argonauta resta img/anteprima.jpg (la scena di Argo, da disegni/png.py).

    python3 -I _lavoro/disegni/png-2.py
"""
import pathlib, re, subprocess, tempfile

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]


def disegna(svg, lato, uscita):
    with tempfile.TemporaryDirectory() as d:
        sorgente = pathlib.Path(d) / "disegno.svg"
        sorgente.write_text(svg, encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", str(lato), "-o", d, str(sorgente)], capture_output=True)
        uscita.write_bytes((pathlib.Path(d) / "disegno.svg.png").read_bytes())


disegna((QUI / "marchio-quadrato-2.svg").read_text(encoding="utf-8"), 180, SITO / "apple-touch-icon.png")

grande, piccola = QUI / "icona-256.png", QUI / "icona-32.png"
icona = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", (SITO / "img" / "icona.svg").read_text(encoding="utf-8"))
disegna(icona, 256, grande)
subprocess.run(["sips", "-z", "32", "32", str(grande), "--out", str(piccola)], capture_output=True)
subprocess.run(["sips", "-s", "format", "ico", str(piccola), "--out", str(SITO / "favicon.ico")], capture_output=True)
grande.unlink(); piccola.unlink()
# Senza i metadati che scrive qlmanage (il PNG resta com'è, pixel per pixel).
subprocess.run(["python3", "-I", str(SITO / "_lavoro" / "strumenti" / "pulisci.py"), str(SITO / "apple-touch-icon.png")])

for p in (SITO / "apple-touch-icon.png", SITO / "favicon.ico"):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)], capture_output=True, text=True).stdout
    print(p.name, " ".join(out.split()[-4:]), p.stat().st_size // 1024, "KB")
