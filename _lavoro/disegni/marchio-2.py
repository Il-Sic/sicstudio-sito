"""Il marchio di Sic Studio (seconda passata): un sentiero a tre tornanti che sale verso una stella a cinque punte.

La propria via, che si trova camminando, e lo sguardo che si alza (le parole di Sic, da-sic/risposte.md, b).
Scrive img/icona.svg (con la versione per lo scuro) e _lavoro/disegni/marchio-quadrato-2.svg, da cui png.py fa
apple-touch-icon.png, favicon.ico e le anteprime. Nelle pagine il marchio è dentro l'HTML (condivise.py, MARCHIO),
con il colore del testo.

    python3 -I _lavoro/disegni/marchio-2.py
"""
import pathlib

SITO = pathlib.Path(__file__).resolve().parents[2]
VIA = "M12 53H40A7 7 0 0 0 40 39H21A7 7 0 0 1 21 25H34"
STELLA = ("M48 8L49.94 13.33L55.61 13.53L51.14 17.02L52.7 22.47L48 19.3L43.3 22.47L44.86 17.02L40.39 13.53"
          "L46.06 13.33Z")

ICONA = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<style>
.f {{ fill: #FAF7F0; }} .v {{ fill: none; stroke: #1E1B17; stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; }} .s {{ fill: #D99A1E; }}
@media (prefers-color-scheme: dark) {{ .f {{ fill: #0C1015; }} .v {{ stroke: #F0EBE1; }} .s {{ fill: #F2C14E; }} }}
</style>
<rect class="f" width="64" height="64" rx="14"/>
<path class="v" d="{VIA}"/>
<path class="s" d="{STELLA}"/>
</svg>
"""

QUADRATO = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="1024" height="1024">
<rect width="64" height="64" fill="#FAF7F0"/>
<g transform="translate(6.4 6.4) scale(.8)">
<path d="{VIA}" fill="none" stroke="#1E1B17" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{STELLA}" fill="#D99A1E"/>
</g>
</svg>
"""

if __name__ == "__main__":
    (SITO / "img" / "icona.svg").write_text(ICONA)
    (SITO / "_lavoro" / "disegni" / "marchio-quadrato-2.svg").write_text(QUADRATO)
    print("img/icona.svg e _lavoro/disegni/marchio-quadrato-2.svg")
