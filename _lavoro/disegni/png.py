"""L'anteprima dei link delle pagine di Argonauta (img/anteprima.jpg, 1200×630, per WhatsApp, iMessage e gli altri): la
scena di Argo di giorno, ferma. Fatta con qlmanage e sips, niente altro da installare: qlmanage disegna un SVG dentro
un quadrato, poi sips ritaglia il centro e la fa JPEG, e strumenti/pulisci.py le toglie i metadati.

    python3 -I _lavoro/disegni/png.py

La scena viene dai disegni dell'app, in _lavoro/riferimenti/svg-sito/ (scena.svg e scena.css), che restano fuori da
git: lo script si usa sul Mac che li ha. Le icone (apple-touch-icon.png e favicon.ico) le fa png-2.py.
"""
import pathlib, re, subprocess, tempfile

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
SVG_SITO = SITO / "_lavoro" / "riferimenti" / "svg-sito"


def disegna(svg, lato, uscita):
    with tempfile.TemporaryDirectory() as d:
        sorgente = pathlib.Path(d) / "disegno.svg"
        sorgente.write_text(svg, encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", str(lato), "-o", d, str(sorgente)], capture_output=True)
        png = pathlib.Path(d) / "disegno.svg.png"
        uscita.write_bytes(png.read_bytes())


# L'anteprima: la scena del sito con i colori del giorno scritti dentro, ferma.
scena = (SVG_SITO / "scena.svg").read_text(encoding="utf-8")
css = (SVG_SITO / "scena.css").read_text(encoding="utf-8")
giorno = re.split(r"@media\s*\(prefers-color-scheme:\s*dark\)", css)[0]
giorno = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", giorno)
giorno = re.sub(r"animation[^;]*;", "", giorno)
# Il riquadro con le proporzioni dell'anteprima (1200:630), tutta la larghezza della scena, e «meet»: qlmanage
# disegna nel quadrato senza tagliare, poi sips ritaglia la fascia di mezzo.
scena = scena.replace('viewBox="-60 -15 520 300" preserveAspectRatio="xMidYMid slice"',
                      'viewBox="-60 -1.5 520 273" preserveAspectRatio="xMidYMid meet"', 1)
# qlmanage riempie il suo quadrato tagliando i lati: la scena va dentro un SVG già quadrato, nella fascia di mezzo.
scena = scena.replace('<svg class="sc-scena"', '<svg class="sc-scena" x="0" y="285" width="1200" height="630"', 1)
scena = scena.replace("<defs>", "<defs>", 1)
scena = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">'
         f"<style>{giorno}</style>{scena}</svg>")
temporanea = QUI / "anteprima-quadrata.png"
disegna(scena, 1200, temporanea)
ritaglio = QUI / "anteprima-ritaglio.png"
subprocess.run(["sips", "-c", "630", "1200", str(temporanea), "--out", str(ritaglio)], capture_output=True)
# In JPEG, per stare sotto i 200 KB.
subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", str(ritaglio), "--out",
                str(SITO / "img" / "anteprima.jpg")], capture_output=True)
ritaglio.unlink()
temporanea.unlink()
subprocess.run(["python3", "-I", str(SITO / "_lavoro" / "strumenti" / "pulisci.py"), str(SITO / "img" / "anteprima.jpg")])
p = SITO / "img" / "anteprima.jpg"
out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)], capture_output=True, text=True).stdout
print(p.name, " ".join(out.split()[-4:]), p.stat().st_size // 1024, "KB")
