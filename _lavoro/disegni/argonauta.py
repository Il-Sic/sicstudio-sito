"""Il guscio dell'argonauta (Argonauta argo) visto di fianco: un giro di spirale che si allarga in fretta fino
all'apertura, con le coste a raggiera e i tubercoli lungo la carena, come nelle tavole di storia naturale. Disegno
semplice, fatto qui. Scrive img/argonauta.svg."""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "img" / "argonauta.svg"
A, B = 10.5, 0.30                 # la spirale r = A·e^(Bθ)
TS, TE = 0.0, 2.25 * math.pi     # da dove parte a dove finisce il bordo esterno
GIRO = 0.62                      # il bordo interno è il giro di prima, un poco più largo
RUOTA = math.radians(-35)
CX, CY = 96, 112

def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")

def punto(t, interno=False):
    r = A * math.exp(B * t)
    if interno:
        r = A * math.exp(B * (t - 2 * math.pi)) if t > 2 * math.pi else r * GIRO * (t / (2 * math.pi)) ** 1.6
    a = t + RUOTA
    return CX + r * math.cos(a), CY - r * math.sin(a)

N = 140
ts = [TS + (TE - TS) * i / N for i in range(N + 1)]
esterno = [punto(t) for t in ts]
interno = [punto(t, True) for t in reversed(ts)]
# L'apertura non è un taglio dritto: il labbro curva in avanti, nel verso in cui il guscio cresce.
(ax1, ay1), (ax2, ay2) = esterno[-1], interno[0]
tx, ty = ax1 - punto(TE - 0.05)[0], ay1 - punto(TE - 0.05)[1]
lt = math.hypot(tx, ty)
largo = math.hypot(ax2 - ax1, ay2 - ay1)
cx, cy = (ax1 + ax2) / 2 + tx / lt * largo * 0.42, (ay1 + ay2) / 2 + ty / lt * largo * 0.42
guscio = ("M" + " L".join(f"{f(x)},{f(y)}" for x, y in esterno) + f" Q{f(cx)},{f(cy)} {f(ax2)},{f(ay2)}"
          + " L" + " L".join(f"{f(x)},{f(y)}" for x, y in interno[1:]) + "Z")
coste, tubercoli = [], []
for i in range(10, N + 1, 6):
    t = ts[i]
    (x1, y1), (x2, y2) = punto(t), punto(t, True)
    mx, my = (x1 + x2) / 2 + (y2 - y1) * 0.08, (y1 + y2) / 2 - (x2 - x1) * 0.08
    coste.append(f'<path class="costa" d="M{f(x2)},{f(y2)} Q{f(mx)},{f(my)} {f(x1)},{f(y1)}"/>')
for i in range(16, N + 1, 6):
    x, y = punto(ts[i])
    tubercoli.append(f'<circle class="tubercolo" cx="{f(x)}" cy="{f(y)}" r="{f(1 + 2.2 * i / N)}"/>')
# Il labbro dell'apertura, un poco più scuro.
labbro = f'<path class="labbro" d="M{f(ax1)},{f(ay1)} Q{f(cx)},{f(cy)} {f(ax2)},{f(ay2)}"/>'
style = (".guscio{fill:#F4EBDA;stroke:#8C7050;stroke-width:2.2;stroke-linejoin:round}"
         ".costa{fill:none;stroke:#CBB797;stroke-width:1.3;stroke-linecap:round}.tubercolo{fill:#8C7050}"
         ".labbro{fill:none;stroke:#8C7050;stroke-width:3;stroke-linecap:round}"
         "@media (prefers-color-scheme:dark){.guscio{fill:#D9CDB6;stroke:#6E5A40}.costa{stroke:#B3A285}"
         ".tubercolo{fill:#6E5A40}.labbro{stroke:#6E5A40}}")
curva = [((1 - u) ** 2 * ax1 + 2 * (1 - u) * u * cx + u * u * ax2, (1 - u) ** 2 * ay1 + 2 * (1 - u) * u * cy + u * u * ay2)
         for u in (i / 20 for i in range(21))]
xs = [x for x, _ in esterno + interno + curva]; ys = [y for _, y in esterno + interno + curva]
m = 8
vb = f"{f(min(xs) - m)} {f(min(ys) - m)} {f(max(xs) - min(xs) + 2 * m)} {f(max(ys) - min(ys) + 2 * m)}"
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" '
       'aria-label="Il guscio dell\'argonauta, visto di fianco: una spirale sottile con le coste a raggiera">'
       f"<style>{style}</style>"
       f'<path class="guscio" d="{guscio}"/>' + "".join(coste) + labbro + "".join(tubercoli) + "</svg>\n")
OUT.write_text(svg, encoding="utf-8")
xs = [x for x, _ in esterno + interno]; ys = [y for _, y in esterno + interno]
print(OUT.name, len(svg), "byte; ingombro", f(min(xs)), f(max(xs)), f(min(ys)), f(max(ys)))
