"""Le due immagini PNG del sito, fatte con qlmanage e sips (niente altro da installare):
- apple-touch-icon.png, 180×180, dalla sagoma di Argo su fondo blu (disegni/icona-quadrata.svg);
- img/anteprima.jpg, 1200×630, la scena di Argo di giorno, per i link mandati su WhatsApp o iMessage;
- favicon.ico, 32×32, l'icona tonda di giorno (img/icona.svg) per Safari, che non usa le icone SVG.

qlmanage disegna un SVG dentro un quadrato: per l'anteprima si ritaglia il centro con sips.
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


# L'icona per la Home di iPhone: quadrata e piena, gli angoli li arrotonda iOS.
disegna((QUI / "icona-quadrata.svg").read_text(encoding="utf-8"), 180, SITO / "apple-touch-icon.png")

# L'icona per Safari: disegnata grande e rimpicciolita, poi in ICO.
grande = QUI / "icona-256.png"
# Senza la parte per la notte: qlmanage segue l'aspetto del Mac, e l'icona di Safari è quella del giorno.
icona = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", (SITO / "img" / "icona.svg").read_text(encoding="utf-8"))
disegna(icona, 256, grande)
piccola = QUI / "icona-32.png"
subprocess.run(["sips", "-z", "32", "32", str(grande), "--out", str(piccola)], capture_output=True)
subprocess.run(["sips", "-s", "format", "ico", str(piccola), "--out", str(SITO / "favicon.ico")], capture_output=True)
grande.unlink()
piccola.unlink()

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
for p in (SITO / "apple-touch-icon.png", SITO / "img" / "anteprima.jpg", SITO / "favicon.ico"):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)], capture_output=True, text=True).stdout
    print(p.name, " ".join(out.split()[-4:]), p.stat().st_size // 1024, "KB")
