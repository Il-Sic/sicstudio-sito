"""La carta del viaggio di Argo, vera: le coste di coste.json (Natural Earth, pubblico dominio), il reticolo dei gradi,
il fiume Fasi, i sei approdi nei loro luoghi, la rotta che passa per il mare e la barca che va da un approdo all'altro.
Scrive la figura nelle due pagine del mito (fra <!-- carta:inizio --> e <!-- carta:fine -->) e i fotogrammi della
barca, della scia e dello spostamento della carta al telefono in style.css (fra /* carta:inizio */ e /* carta:fine */).

    python3 -I _lavoro/disegni/carta.py            scrive pagine e foglio di stile
    python3 -I _lavoro/disegni/carta.py --prova F  scrive solo un SVG di prova, con i colori, nel file F
"""
import json, math, pathlib, re, sys

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
C = json.loads((QUI / "coste.json").read_text(encoding="utf-8"))
LON0, LON1, LAT0, LAT1 = C["riquadro"]
LARGO, ALTO, SCALA, COS = C["largo"], C["alto"], C["scala"], C["coseno"]


def proietta(lon, lat):
    return ((lon - LON0) * COS * SCALA, (LAT1 - lat) * SCALA)


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# Gli approdi, nei luoghi di oggi (gradi decimali, est e nord).
APPRODI = [
    ("pagase", 22.95, 39.33),    # Pagase, vicino a Volo
    ("lemno", 25.07, 39.87),     # Mirina, sull'isola di Lemno
    ("cizico", 27.88, 40.39),    # Cizico, sull'istmo della penisola di Kapıdağ
    ("simplegadi", 29.12, 41.23),  # l'imbocco del Bosforo dal mar Nero
    ("colchide", 41.67, 42.15),  # la foce del Fasi (il Rioni), a Poti
    ("vello", 42.70, 42.27),     # risalendo il Fasi
]
# La rotta per mare, approdo per approdo (gli approdi sono i punti con il nome).
ROTTA = [
    "pagase", (23.00, 39.24), (23.02, 39.07), (23.23, 39.06), (23.40, 39.08), (23.90, 39.30), (24.50, 39.62), "lemno",
    (25.30, 39.80), (25.85, 39.98), (26.20, 40.06), (26.42, 40.20), (26.62, 40.36), (26.85, 40.47), (27.25, 40.48),
    (27.62, 40.42), "cizico",
    (28.02, 40.40), (28.25, 40.58), (28.60, 40.78), (28.92, 40.95), (29.01, 41.03), (29.06, 41.13), "simplegadi",
    (29.70, 41.32), (30.60, 41.30), (31.50, 41.40), (32.40, 41.90), (33.40, 42.10), (34.60, 42.20), (35.30, 42.18),
    (36.20, 41.82), (37.10, 41.30), (38.30, 41.18), (39.50, 41.18), (40.50, 41.42), (41.20, 41.85), "colchide",
    (41.95, 42.19), (42.25, 42.21), (42.52, 42.24), "vello",
]
# Il fiume Fasi (il Rioni): la stessa curva della rotta dalla foce al vello, poi verso la sorgente.
FIUME_OLTRE = [(42.95, 42.32), (43.25, 42.45)]
SOSTA = 3.0      # per cento della strada: la barca resta ferma a ogni approdo
CAMPIONI = 44    # i fotogrammi della barca in viaggio


def punti_rotta():
    nomi = {a[0]: proietta(a[1], a[2]) for a in APPRODI}
    pts, approdi = [], []
    for r in ROTTA:
        if isinstance(r, str):
            approdi.append(len(pts))
            pts.append(nomi[r])
        else:
            pts.append(proietta(*r))
    return pts, approdi


def catmull(pts):
    """Una curva liscia che passa per tutti i punti: Catmull-Rom in Bézier cubiche."""
    segmenti = []
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segmenti.append((p1, c1, c2, p2))
    return segmenti


def bezier(seg, t):
    p1, c1, c2, p2 = seg
    u = 1 - t
    return (u ** 3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p2[0],
            u ** 3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p2[1])


def d_curva(segmenti):
    d = f"M{n(segmenti[0][0][0])} {n(segmenti[0][0][1])}"
    for _, c1, c2, p2 in segmenti:
        d += f"C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}"
    return d


def misura(segmenti, passi=40):
    """Per ogni segmento, i punti fitti e la lunghezza percorsa fino a lì."""
    fitti = [(0.0, segmenti[0][0], 0)]
    totale = 0.0
    prima = segmenti[0][0]
    for i, seg in enumerate(segmenti):
        for k in range(1, passi + 1):
            q = bezier(seg, k / passi)
            totale += math.hypot(q[0] - prima[0], q[1] - prima[1])
            fitti.append((totale, q, i))
            prima = q
    return fitti, totale


def a_distanza(fitti, s):
    for (s0, q0, _), (s1, q1, _) in zip(fitti, fitti[1:]):
        if s1 >= s:
            t = 0 if s1 == s0 else (s - s0) / (s1 - s0)
            return (q0[0] + (q1[0] - q0[0]) * t, q0[1] + (q1[1] - q0[1]) * t)
    return fitti[-1][1]


def fotogrammi():
    """(percentuale dello scorrimento, frazione della rotta, x, y): la barca si ferma un poco a ogni approdo e fra due
    approdi va a velocità costante; il tempo di ogni tratto è proporzionale alla sua lunghezza."""
    pts, approdi = punti_rotta()
    segmenti = catmull(pts)
    fitti, totale = misura(segmenti)
    # La distanza di ogni approdo lungo la rotta (l'approdo i è all'inizio del segmento approdi[i]).
    dist = []
    for a in approdi:
        if a == 0:
            dist.append(0.0)
        else:
            dist.append(max(s for s, _, seg in fitti if seg == a - 1))
    soste = len(approdi) - 2
    viaggio = 100 - SOSTA * soste - 2 * 1.5
    tappe = [(0.0, 0.0)]
    t = 1.5
    tappe.append((t, 0.0))
    for k in range(1, len(approdi)):
        t += viaggio * (dist[k] - dist[k - 1]) / totale
        tappe.append((t, dist[k]))
        if k < len(approdi) - 1:
            t += SOSTA
            tappe.append((t, dist[k]))
    tappe[-1] = (98.5, totale)
    tappe.append((100.0, totale))
    # I fotogrammi: le tappe, più punti in mezzo ai tratti in viaggio.
    righe = []
    for (t0, s0), (t1, s1) in zip(tappe, tappe[1:]):
        if s1 == s0:
            righe.append((t0, s0))
            continue
        quanti = max(2, round(CAMPIONI * (s1 - s0) / totale))
        for k in range(quanti):
            righe.append((t0 + (t1 - t0) * k / quanti, s0 + (s1 - s0) * k / quanti))
    righe.append(tappe[-1])
    out, visti = [], set()
    for t, s in righe:
        chiave = round(t, 2)
        if chiave in visti:
            continue
        visti.add(chiave)
        x, y = a_distanza(fitti, s)
        out.append((t, s / totale, x, y))
    return segmenti, out, pts, approdi


def d_terre():
    d = []
    for anello in C["anelli"]:
        pts = anello["punti"]
        parti = [f"M{n(pts[0][0])} {n(pts[0][1])}"]
        px, py = pts[0]
        for x, y in pts[1:]:
            parti.append(f"l{n(x - px)} {n(y - py)}")
            px, py = x, y
        d.append("".join(parti).replace(" -", "-") + "z")
    return "".join(d)


def d_reticolo():
    d = []
    for lon in range(22, 44, 2):
        x, _ = proietta(lon, LAT0)
        if 0 < x < LARGO:
            d.append(f"M{n(x)} 0V{n(ALTO)}")
    for lat in range(38, 47, 2):
        _, y = proietta(LON0, lat)
        d.append(f"M0 {n(y)}H{LARGO:.0f}")
    return "".join(d)


def d_fiume(segmenti, approdi):
    fine = segmenti[approdi[-2]:]
    d = d_curva(fine)
    for lon, lat in FIUME_OLTRE:
        x, y = proietta(lon, lat)
        d += f"L{n(x)} {n(y)}"
    return d


# I nomi sulla carta: dove stanno rispetto al punto (sopra, sotto, a sinistra, a destra) e i mari.
POSTI = {"pagase": "sopra-destra", "lemno": "sopra", "cizico": "sotto", "simplegadi": "sopra", "colchide": "sotto",
         "vello": "sopra"}
MARI = [("egeo", 24.7, 38.2), ("nero", 34.2, 43.7)]


def figura(lingua, prova=False):
    segmenti, fot, pts, approdi = fotogrammi()
    rotta = d_curva(segmenti)
    cerchi = "".join(
        f'<circle{" class=\"carta-vello\"" if i == len(approdi) - 1 else ""} cx="{n(pts[a][0])}" cy="{n(pts[a][1])}" r="{7 if i == len(approdi) - 1 else 5}"/>'
        for i, a in enumerate(approdi))
    stile = ""
    if prova:
        stile = ('<style>.carta-mare{fill:#DCE6E8}.carta-reticolo{fill:none;stroke:#7FA3AE;stroke-width:.6;opacity:.5}'
                 '.carta-costa{fill:#C9DBE0;stroke:#C9DBE0;stroke-width:5;fill-rule:evenodd}'
                 '.carta-terre{fill:#F6F1E6;stroke:#8C857A;stroke-width:.8;fill-rule:evenodd}.carta-fiume{fill:none;stroke:#5E95A8;stroke-width:1.6}'
                 '.carta-rotta{fill:none;stroke:#8C857A;stroke-width:1.5;stroke-dasharray:4 5}.carta-scia{fill:none;stroke:#08739A;stroke-width:3}'
                 '.carta-approdi circle{fill:#FAF7F0;stroke:#08739A;stroke-width:2.5}.carta-approdi .carta-vello{fill:#D99A1E;stroke:#8F5B00}</style>')
    t = TESTI[lingua]
    svg = (f'<svg class="carta" viewBox="0 0 {LARGO:.0f} {n(ALTO)}" role="img" aria-labelledby="carta-titolo">'
           f'{stile}<title id="carta-titolo">{t["titolo"]}</title>'
           f'<defs><path id="carta-forma" d="{d_terre()}"/></defs>'
           f'<rect class="carta-mare" width="{LARGO:.0f}" height="{n(ALTO)}"/>'
           f'<path class="carta-reticolo" d="{d_reticolo()}"/>'
           '<use href="#carta-forma" class="carta-costa"/><use href="#carta-forma" class="carta-terre"/>'
           f'<path class="carta-fiume" d="{d_fiume(segmenti, approdi)}"/>'
           f'<path class="carta-rotta" d="{rotta}"/>'
           f'<path class="carta-scia" pathLength="1" d="{rotta}"/>'
           f'<g class="carta-approdi">{cerchi}</g>'
           '<g class="carta-barca"><path d="M-12 -1H12L8 6H-8Z"/><path d="M-1.5 -1V-19L10 -4Z"/></g>'
           '</svg>')
    if prova:
        return svg
    nomi = []
    for (chiave, lon, lat), nome in zip(APPRODI, t["approdi"]):
        x, y = proietta(lon, lat)
        nomi.append(f'<li class="carta-nome carta-{POSTI[chiave]} cn-{chiave}">{nome}</li>')
    for (chiave, lon, lat), nome in zip(MARI, t["mari"]):
        x, y = proietta(lon, lat)
        nomi.append(f'<li class="carta-mare-nome cn-{chiave}">{nome}</li>')
    return svg, nomi


TESTI = {
    "it": {"titolo": "La carta del viaggio di Argo: da Pagase, in Tessaglia, a Lemno, a Cizico e alle Simplegadi, "
                     "all’ingresso del mar Nero; poi lungo la costa dell’Anatolia fino alla Colchide e su per il fiume "
                     "Fasi fino al vello d’oro.",
           "approdi": ["Pagase", "Lemno", "Cizico", "Simplegadi", "Colchide", "Vello d’oro"],
           "mari": ["Mar Egeo", "Mar Nero"],
           "fonte": 'Le coste vengono da <span lang="en">Natural Earth</span>, di pubblico dominio, semplificate. '
                    "Gli approdi sono nei luoghi di oggi: Pagase vicino a Volo, Cizico sul mar di Marmara, le "
                    "Simplegadi all’imbocco del Bosforo; il Fasi è il fiume Rioni, in Georgia."},
    "en": {"titolo": "The chart of the Voyage of Argo: from Pagasae, in Thessaly, to Lemnos, Cyzicus and the Clashing "
                     "Rocks at the mouth of the Black Sea; then along the coast of Anatolia to Colchis and up the river "
                     "Phasis to the golden fleece.",
           "approdi": ["Pagasae", "Lemnos", "Cyzicus", "Clashing Rocks", "Colchis", "Golden Fleece"],
           "mari": ["Aegean Sea", "Black Sea"],
           "fonte": "The coastlines come from Natural Earth, in the public domain, simplified. The landfalls are at "
                    "today’s places: Pagasae near Volos, Cyzicus on the Sea of Marmara, the Clashing Rocks at the mouth "
                    "of the Bosphorus; the Phasis is the river Rioni, in Georgia."},
}
PAGINE = {"it": "argonauta/il-mito/index.html", "en": "en/argonauta/the-myth/index.html"}


def blocco(lingua):
    """La figura nella pagina. I nomi sulla carta sono nascosti ai lettori di schermo (14/11): il titolo della carta
    dice già tutti gli approdi, in ordine, e letti dopo il titolo sarebbero un secondo elenco con in più i mari."""
    svg, nomi = figura(lingua)
    return ('\n  <figure class="carta-viaggio">\n    <div class="carta-pista">\n      <div class="carta-palco">\n'
            '        <div class="carta-mappa">\n          ' + svg + '\n'
            '          <ol class="carta-nomi" aria-hidden="true">' + "".join(nomi) + '</ol>\n'
            '        </div>\n      </div>\n    </div>\n'
            f'    <figcaption class="fonte">{TESTI[lingua]["fonte"]}</figcaption>\n  </figure>\n  ')


def css():
    """Le posizioni dei nomi, la barca ferma all'arrivo e i fotogrammi di barca, scia e carta che scorre."""
    _, fot, pts, approdi = fotogrammi()
    righe = ["/* carta:inizio (scritto da _lavoro/disegni/carta.py: non cambiarlo a mano) */"]
    for chiave, lon, lat in APPRODI + [(m[0], m[1], m[2]) for m in MARI]:
        x, y = proietta(lon, lat)
        righe.append(f".cn-{chiave} {{ left: {x / LARGO * 100:.2f}%; top: {y / ALTO * 100:.2f}%; }}")
    xf, yf = fot[-1][2], fot[-1][3]
    righe.append(f".carta-barca {{ transform: translate({n(xf)}px, {n(yf)}px); }}")
    naviga = " ".join(f"{t:.2f}% {{ transform: translate({n(x)}px, {n(y)}px); }}" for t, s, x, y in fot)
    # La scia cresce con la strada fatta, che fra una sosta e l'altra va dritta col tempo: bastano le soste.
    fermi = [i for i in range(len(fot)) if i in (0, len(fot) - 1) or abs(fot[i][1] - fot[i - 1][1]) < 1e-9
             or abs(fot[i + 1][1] - fot[i][1]) < 1e-9]
    scia = " ".join(f"{fot[i][0]:.2f}% {{ stroke-dashoffset: {1 - fot[i][1]:.4f}; }}" for i in fermi)
    righe.append(f"@keyframes naviga {{ {naviga} }}")
    righe.append(f"@keyframes scia {{ {scia} }}")
    # La carta, al telefono, scorre con la barca: alla partenza si vede il suo bordo sinistro, all'arrivo il destro, e
    # in mezzo scorre di quanto la barca è andata verso est (la x cresce sempre lungo la rotta). Fino al 14/11 scorreva
    # della x della barca su tutta la larghezza: all'arrivo la barca stava a pochi pixel dal bordo dello schermo.
    x0, x1 = fot[0][2], fot[-1][2]
    soste = []
    for i, (t, s, x, y) in enumerate(fot):
        if i == 0 or i == len(fot) - 1 or abs(s - fot[i - 1][1]) < 1e-9 or (i + 1 < len(fot) and abs(fot[i + 1][1] - s) < 1e-9) or i % 4 == 0:
            soste.append((t, (x - x0) / (x1 - x0)))
    scorri = " ".join(f"{t:.2f}% {{ translate: calc({f:.4f} * (100cqw - 100%)) 0; }}" for t, f in soste)
    righe.append(f"@keyframes scorri {{ {scorri} }}")
    righe.append("/* carta:fine */")
    return "\n".join(righe)


def main():
    if "--prova" in sys.argv:
        f = pathlib.Path(sys.argv[sys.argv.index("--prova") + 1])
        f.write_text(figura("it", prova=True), encoding="utf-8")
        _, fot, _, _ = fotogrammi()
        print(f"prova: {f} ({f.stat().st_size} byte), {len(fot)} fotogrammi")
        return 0
    # Esce con 1, senza scrivere il file, se i segni della carta non ci sono una volta sola.
    problemi = 0
    for lingua, file in PAGINE.items():
        p = SITO / file
        testo = p.read_text(encoding="utf-8")
        a, b = "<!-- carta:inizio -->", "<!-- carta:fine -->"
        testo, quante = re.subn(re.escape(a) + r".*?" + re.escape(b), lambda m: a + blocco(lingua) + b, testo, flags=re.S)
        if quante != 1:
            print(f"{file}: i segni della carta ci sono {quante} volte invece di una")
            problemi += 1
            continue
        p.write_text(testo, encoding="utf-8")
        print(file, len(testo), "byte")
    p = SITO / "style.css"
    stile = p.read_text(encoding="utf-8")
    stile, quante = re.subn(r"/\* carta:inizio .*?/\* carta:fine \*/", lambda m: css(), stile, flags=re.S)
    if quante != 1:
        print(f"style.css: i segni della carta ci sono {quante} volte invece di una")
        problemi += 1
    else:
        p.write_text(stile, encoding="utf-8")
        print("style.css", len(stile), "byte")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
