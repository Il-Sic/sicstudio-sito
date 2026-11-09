"""I fotogrammi della barca sulla carta del viaggio (il mito, italiano e inglese): la barca segue la rotta in 30 tratti
misurati sulla sua lunghezza, come la scia che si disegna. Si usa una traslazione per fotogramma invece di
offset-path, che dentro un SVG non va dappertutto. Stampa la regola @keyframes naviga da mettere in style.css al posto
di quella che c'è. Se cambia la rotta (il «d» di .carta-rotta e .carta-scia), si cambia SEGMENTI e si rilancia.

    python3 -I _lavoro/strumenti/barca.py
"""
import math

SEGMENTI = [((26, 96), (54.6, 96), (54.6, 60), (83.2, 60)), ((83.2, 60), (111.8, 60), (111.8, 96), (140.4, 96)),
            ((140.4, 96), (169, 96), (169, 60), (197.6, 60)), ((197.6, 60), (226.2, 60), (226.2, 96), (254.8, 96)),
            ((254.8, 96), (283.4, 96), (283.4, 60), (312, 60))]
TRATTI = 30


def bezier(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
            u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


punti = [bezier(s, i / 200) for s in SEGMENTI for i in range(200)] + [SEGMENTI[-1][3]]
lunghezze = [0.0]
for a, b in zip(punti, punti[1:]):
    lunghezze.append(lunghezze[-1] + math.dist(a, b))
fotogrammi, j = [], 0
for k in range(TRATTI + 1):
    obiettivo = lunghezze[-1] * k / TRATTI
    while j < len(lunghezze) - 1 and lunghezze[j + 1] < obiettivo:
        j += 1
    if j >= len(punti) - 1:
        x, y = punti[-1]
    else:
        f = (obiettivo - lunghezze[j]) / max(lunghezze[j + 1] - lunghezze[j], 1e-9)
        x = punti[j][0] + f * (punti[j + 1][0] - punti[j][0])
        y = punti[j][1] + f * (punti[j + 1][1] - punti[j][1])
    fotogrammi.append(f"{round(100 * k / TRATTI, 2):g}% {{ transform: translate({x:.1f}px, {y:.1f}px); }}")
print("@keyframes naviga { " + " ".join(fotogrammi) + " }")
