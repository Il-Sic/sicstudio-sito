"""Il marchio di Sic Studio (terza passata, 13/11/2026): il sentiero a tre tornanti, senza la stella, pieno di cielo
dal tramonto alla notte. È la S del logo scelto da Sic, la direzione G rifinita con la S della direzione A; il kit del
logo (sic-studio-logo-kit.zip, nella cartella del progetto) ha tutte le sue forme e la guida.

Nella testata e nel piede il marchio è la S del kit con le sue stelle: img/marchio-giorno.svg (carta) e
img/marchio-notte.svg, dalla cartella web/ del kit, con la Via Lattea fine quanto basta per gli schermi 3x
(condivise.py, MARCHIO). Sulla copertina di Argonauta la S è piccola, e lì è solo il cielo che sfuma, nell'HTML.

Scrive img/icona.svg, la favicon: l'icona piccola del kit ridisegnata sulla griglia di 16 pixel, così i tre tratti
cadono su pixel interi e restano netti anche a 32. favicon.ico (16, 32 e 48 px) e apple-touch-icon.png sono quelli
del kit (cartella web/), come le due S con le stelle, la S vista da vicino della pagina dello studio
(img/marchio-vicino-giorno.svg e -notte.svg) e l'anteprima dei link di home e studio (img/anteprima-logo.jpg, la
scena con il nome sulla carta): li fanno gli script del kit (kit_g.py e raster.js, con Playwright), non si rifanno
qui.

    python3 -I _lavoro/disegni/marchio-3.py
"""
import pathlib

SITO = pathlib.Path(__file__).resolve().parents[2]
VIA = "M12 53H40A7 7 0 0 0 40 39H21A7 7 0 0 1 21 25H34"
# Il cielo della S, dall'alto: (posizione, colore). CARTA sui fondi chiari, NOTTE su quelli scuri.
CARTA = [("0", "#F3A97A"), ("0.09", "#B8628C"), ("0.22", "#4B3C8E"), ("0.45", "#1E2466"), ("1", "#0A0F2E")]
NOTTE = [("0", "#F7B984"), ("0.14", "#DE7C98"), ("0.36", "#8A6CD0"), ("0.62", "#5162D2"), ("1", "#3447B8")]
# Il fondo dell'icona: la notte, più chiara in basso.
FONDO = [("0", "#060918"), ("0.55", "#121747"), ("1", "#2B2266")]
# La S dell'icona sulla griglia di 16 pixel: tratti e spazi di 2 pixel, da y 3 a y 13.
VIA_16 = "M3 12H11A2 2 0 0 0 11 8H6A2 2 0 0 1 6 4H9"


def sfumatura(nome, colori, y1, y2):
    return (f'<linearGradient id="{nome}" x1="0" y1="{y1}" x2="0" y2="{y2}" gradientUnits="userSpaceOnUse">'
            + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in colori) + "</linearGradient>")


ICONA = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
<defs>{sfumatura("fondo", FONDO, 0, 16)}{sfumatura("cielo", NOTTE, 3, 13)}</defs>
<rect width="16" height="16" rx="3.5" fill="url(#fondo)"/>
<path d="{VIA_16}" fill="none" stroke="url(#cielo)" stroke-width="2" stroke-linecap="round"/>
</svg>
"""

if __name__ == "__main__":
    (SITO / "img" / "icona.svg").write_text(ICONA)
    print("img/icona.svg")
