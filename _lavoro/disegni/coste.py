"""Le coste della carta del viaggio di Argo, dalle terre emerse di Natural Earth (1:10m, pubblico dominio): ritaglio
sull'Egeo e il mar Nero, proiezione equirettangolare con il parallelo di 42°, semplificazione (Douglas-Peucker) e via
le isole più piccole. Scrive _lavoro/disegni/coste.json, che legge carta.py.

    python3 -I _lavoro/disegni/coste.py <ne_10m_land.geojson>

Il file di Natural Earth non sta nel sito: si scarica da
https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson
"""
import json, math, pathlib, sys

QUI = pathlib.Path(__file__).resolve().parent
# Il riquadro della carta, in gradi: dalla Grecia alla Colchide, da Creta in su fino alla costa nord del mar Nero.
LON0, LON1, LAT0, LAT1 = 21.6, 43.6, 37.0, 46.9
COS = math.cos(math.radians(42))
LARGO = 1000.0
SCALA = LARGO / ((LON1 - LON0) * COS)
ALTO = round((LAT1 - LAT0) * SCALA, 1)
TOLLERANZA = 0.65      # unità della carta (1000 di larghezza)
ISOLA_MINIMA = 5.0      # unità quadrate: le isole più piccole non si vedrebbero


def proietta(lon, lat):
    return ((lon - LON0) * COS * SCALA, (LAT1 - lat) * SCALA)


def taglia(anello, x0, y0, x1, y1):
    """Sutherland-Hodgman sul rettangolo, lato per lato."""
    def lato(punti, dentro, incrocio):
        fuori = []
        for i, p in enumerate(punti):
            q = punti[i - 1]
            if dentro(p):
                if not dentro(q):
                    fuori.append(incrocio(q, p))
                fuori.append(p)
            elif dentro(q):
                fuori.append(incrocio(q, p))
        return fuori
    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))
    def iy(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1]), yc)
    p = anello
    for dentro, incrocio in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                             (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not p:
            break
        p = lato(p, dentro, incrocio)
    return p


def dp(punti, tol):
    if len(punti) < 3:
        return punti
    a, b = punti[0], punti[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    lung = math.hypot(dx, dy) or 1e-9
    peggiore, indice = 0.0, 0
    for i in range(1, len(punti) - 1):
        p = punti[i]
        d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / lung
        if d > peggiore:
            peggiore, indice = d, i
    if peggiore <= tol:
        return [a, b]
    return dp(punti[:indice + 1], tol)[:-1] + dp(punti[indice:], tol)


def area(anello):
    return abs(sum(anello[i - 1][0] * p[1] - p[0] * anello[i - 1][1] for i, p in enumerate(anello))) / 2


def main():
    dati = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    margine = 2.0
    anelli = []
    for f in dati["features"]:
        g = f["geometry"]
        poligoni = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poligono in poligoni:
            for k, anello in enumerate(poligono):
                lons = [c[0] for c in anello]; lats = [c[1] for c in anello]
                if max(lons) < LON0 - 1 or min(lons) > LON1 + 1 or max(lats) < LAT0 - 1 or min(lats) > LAT1 + 1:
                    continue
                pts = taglia([proietta(lon, lat) for lon, lat in anello], -margine, -margine, LARGO + margine, ALTO + margine)
                if len(pts) < 3:
                    continue
                if area(pts) < ISOLA_MINIMA:
                    continue
                # Douglas-Peucker su un anello chiuso: lo si apre nel punto più lontano dal primo.
                lontano = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
                semplice = dp(pts[:lontano + 1], TOLLERANZA)[:-1] + dp(pts[lontano:] + [pts[0]], TOLLERANZA)[:-1]
                if len(semplice) >= 3 and area(semplice) >= ISOLA_MINIMA:
                    anelli.append({"buco": k > 0, "punti": [[round(x, 1), round(y, 1)] for x, y in semplice]})
    uscita = {"riquadro": [LON0, LON1, LAT0, LAT1], "coseno": COS, "scala": SCALA, "largo": LARGO, "alto": ALTO,
              "anelli": anelli}
    (QUI / "coste.json").write_text(json.dumps(uscita, separators=(",", ":")), encoding="utf-8")
    print(f"carta {LARGO:.0f}×{ALTO}: {len(anelli)} anelli, {sum(len(a['punti']) for a in anelli)} punti")


if __name__ == "__main__":
    main()
