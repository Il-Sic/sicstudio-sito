"""La nave Argo nel cielo: le 20 stelle più luminose di Carena, Poppa e Vele nelle loro posizioni vere.

Dati da riferimenti/mito-fonti.md, sezione 7: coordinate ICRS J2000 e magnitudini da SIMBAD (CDS), linee semplificate
da Stellarium («modern»). Proiezione gnomonica con centro in AR 128°, Dec −48°, il nord in alto e l'est a sinistra,
come si vede il cielo. Scrive img/argo-navis.svg (etichette in italiano) e img/argo-navis-en.svg (in inglese).
Il disegno non ha stelle inventate: solo queste venti, più la griglia delle coordinate.
"""
import math, pathlib

SITO = pathlib.Path(__file__).resolve().parents[2]

# nome, AR (°), Dec (°), magnitudine V
STELLE = {
    "aCar": ("Canopo", 95.9880, -52.6957, -0.74),
    "bCar": ("Miaplacidus", 138.2999, -69.7172, 1.69),
    "eCar": ("Avior", 125.6285, -59.5095, 1.86),
    "iCar": ("Aspidiske", 139.2725, -59.2752, 2.26),
    "thCar": ("θ Car", 160.7392, -64.3945, 2.76),
    "omCar": ("ω Car", 153.4343, -70.0379, 3.33),
    "zPup": ("Naos", 120.8960, -40.0031, 2.25),
    "piPup": ("π Pup", 109.2857, -37.0975, 2.70),
    "rPup": ("Tureis", 121.8860, -24.3043, 2.81),
    "nPup": ("ν Pup", 99.4403, -43.1959, 3.17),
    "xPup": ("Azmidi", 117.3236, -24.8598, 3.34),
    "tPup": ("τ Pup", 102.4840, -50.6145, 2.93),
    "sPup": ("σ Pup", 112.3076, -43.3014, 3.25),
    "g2Vel": ("γ² Vel", 122.3831, -47.3366, 1.83),
    "dVel": ("Alsephina", 131.1759, -54.7088, 1.96),
    "kVel": ("Markeb", 140.5284, -55.0107, 2.47),
    "lVel": ("Suhail", 136.9990, -43.4326, 2.21),
    "mVel": ("μ Vel", 161.6924, -49.4203, 2.69),
    "phVel": ("φ Vel", 149.2156, -54.5678, 3.45),
    "psVel": ("ψ Vel", 142.6750, -40.4667, 3.60),
}
LINEE = [
    # Poppa, anello di 7
    ("rPup", "xPup"), ("xPup", "piPup"), ("piPup", "nPup"), ("nPup", "tPup"), ("tPup", "sPup"), ("sPup", "zPup"),
    ("zPup", "rPup"),
    # Vele, anello di 7
    ("g2Vel", "dVel"), ("dVel", "kVel"), ("kVel", "phVel"), ("phVel", "mVel"), ("mVel", "psVel"), ("psVel", "lVel"),
    ("lVel", "g2Vel"),
    # Carena, catena di 5
    ("aCar", "eCar"), ("eCar", "iCar"), ("iCar", "thCar"), ("thCar", "omCar"), ("omCar", "bCar"),
    # Legami tra le parti
    ("aCar", "nPup"), ("zPup", "g2Vel"), ("dVel", "eCar"),
]
# 7 + 7 + 5 + 3 = 22 linee (mito-fonti.md dice «21», ma l'elenco che dà ne ha 22).
assert len(STELLE) == 20 and len(LINEE) == 22

A0, D0 = math.radians(128.0), math.radians(-48.0)


def proietta(ar, dec):
    a, d = math.radians(ar), math.radians(dec)
    c = math.sin(D0) * math.sin(d) + math.cos(D0) * math.cos(d) * math.cos(a - A0)
    x = -math.cos(d) * math.sin(a - A0) / c
    y = (math.cos(D0) * math.sin(d) - math.sin(D0) * math.cos(d) * math.cos(a - A0)) / c
    return x, -y  # in SVG la y cresce verso il basso


SCALA = 700  # unità SVG per radiante di proiezione
punti = {k: tuple(v * SCALA for v in proietta(ar, dec)) for k, (_, ar, dec, _) in STELLE.items()}
xs = [p[0] for p in punti.values()]
ys = [p[1] for p in punti.values()]
MARGINE = 46
x0, x1 = min(xs) - MARGINE, max(xs) + MARGINE
y0, y1 = min(ys) - MARGINE, max(ys) + MARGINE
L, H = x1 - x0, y1 - y0


def xy(p):
    return round(p[0] - x0, 1), round(p[1] - y0, 1)


def raggio(v):
    # Più è bassa la magnitudine, più è grande il punto: Canopo il più grande.
    return round(1.6 + 0.95 * (3.8 - v), 2)


def griglia():
    """Le linee delle coordinate: declinazione ogni 10°, ascensione retta ogni ora."""
    tratti = []
    for dec in range(-20, -80, -10):
        pts = [xy(tuple(v * SCALA for v in proietta(ar, dec))) for ar in range(80, 181, 2)]
        tratti.append(pts)
    for ore in range(6, 12):
        ar = ore * 15
        pts = [xy(tuple(v * SCALA for v in proietta(ar, dec))) for dec in range(-18, -79, -2)]
        tratti.append(pts)
    out = []
    for pts in tratti:
        dentro = [p for p in pts if -40 <= p[0] <= L + 40 and -40 <= p[1] <= H + 40]
        if len(dentro) > 1:
            out.append("M" + " L".join(f"{x} {y}" for x, y in dentro))
    return out


ETICHETTE = {
    "it": {"Poppa": "Poppa", "Vele": "Vele", "Carena": "Carena", "Canopo": "Canopo",
           "titolo": "La nave Argo nel cielo: le stelle di Carena, Poppa e Vele"},
    "en": {"Poppa": "Stern", "Vele": "Sails", "Carena": "Keel", "Canopo": "Canopus",
           "titolo": "The ship Argo in the sky: the stars of Carina, Puppis and Vela"},
}


def etichetta_parte(nomi, dx=0, dy=0):
    cx = sum(punti[n][0] for n in nomi) / len(nomi) + dx
    cy = sum(punti[n][1] for n in nomi) / len(nomi) + dy
    return xy((cx, cy))


def svg(lingua):
    e = ETICHETTE[lingua]
    righe = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(L)} {round(H)}" '
             f'width="{round(L)}" height="{round(H)}" role="img" aria-label="{e["titolo"]}">',
             "<style>"
             ".cielo{fill:url(#notte)}"
             ".griglia{fill:none;stroke:#9FB8D9;stroke-opacity:.16;stroke-width:1}"
             ".linea{stroke:#BCD3F0;stroke-opacity:.55;stroke-width:1.6;stroke-linecap:round}"
             ".alone{fill:#FFF;fill-opacity:.16}"
             ".stella{fill:#FFF}"
             ".canopo{fill:#FFF4D6}"
             ".parte{font:600 23px ui-rounded,-apple-system,system-ui,sans-serif;letter-spacing:.14em;"
             "fill:#BCD3F0;text-anchor:middle;text-transform:uppercase;paint-order:stroke;stroke:#10213C;stroke-width:7px;stroke-linejoin:round}"
             ".nome{font:italic 22px ui-serif,Georgia,serif;fill:#FFE9B0;paint-order:stroke;stroke:#10213C;stroke-width:6px;stroke-linejoin:round}"
             "</style>",
             '<defs><linearGradient id="notte" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0B1B33"/><stop offset="1" stop-color="#16294A"/></linearGradient></defs>',
             f'<rect class="cielo" width="{round(L)}" height="{round(H)}"/>',
             '<path class="griglia" d="' + " ".join(griglia()) + '"/>']
    for a, b in LINEE:
        (xa, ya), (xb, yb) = xy(punti[a]), xy(punti[b])
        righe.append(f'<line class="linea" x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}"/>')
    for k, (nome, _, _, v) in STELLE.items():
        x, y = xy(punti[k])
        r = raggio(v)
        righe.append(f'<circle class="alone" cx="{x}" cy="{y}" r="{round(r * 2.4, 2)}"/>')
        righe.append(f'<circle class="{"canopo" if k == "aCar" else "stella"}" cx="{x}" cy="{y}" r="{r}"/>')
    # Le tre parti e Canopo
    # La Poppa è un anello stretto: l'etichetta va dove è più largo, a metà fra la linea ζ–ρ e la linea ξ–π.
    px, py = xy((123, -150))
    vx, vy = etichetta_parte(["g2Vel", "dVel", "kVel", "phVel", "mVel", "psVel", "lVel"], dx=6, dy=4)
    cx, cy = etichetta_parte(["eCar", "iCar", "thCar", "omCar", "bCar"], dx=0, dy=40)
    righe.append(f'<text class="parte" x="{px}" y="{py}">{e["Poppa"]}</text>')
    righe.append(f'<text class="parte" x="{vx}" y="{vy}">{e["Vele"]}</text>')
    righe.append(f'<text class="parte" x="{cx}" y="{cy}">{e["Carena"]}</text>')
    ax, ay = xy(punti["aCar"])
    righe.append(f'<text class="nome" x="{ax}" y="{round(ay + 36, 1)}" text-anchor="middle">{e["Canopo"]}</text>')
    righe.append("</svg>")
    return "\n".join(righe) + "\n"


(SITO / "img" / "argo-navis.svg").write_text(svg("it"), encoding="utf-8")
(SITO / "img" / "argo-navis-en.svg").write_text(svg("en"), encoding="utf-8")
print(f"argo-navis.svg e argo-navis-en.svg: {round(L)}×{round(H)}, {len(STELLE)} stelle, {len(LINEE)} linee")
