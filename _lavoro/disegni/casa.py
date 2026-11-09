"""La casa dello studio, in tre misure, e le cose della bottega. Scrive i disegni dentro le pagine, fra i segni
<!-- nome:inizio --> e <!-- nome:fine -->, così le tre case restano la stessa casa:
- cielo-fronte: le stelle, il sole e la luna dell'apertura della home (gli stessi della soglia);
- colle: la collina dell'apertura con il laghetto, il sentiero e la casa piccola (un quinto della casa grande);
- soglia: la casa da vicino, con la porta che si apre, sopra l'apertura della home;
- bottega-studio: la casa a metà strada, nell'apertura della pagina dello studio;
- finestra (con la pianta sul davanzale), matita (il libro del gioco), lampada: le cose dentro la bottega, nella home.

    python3 -I _lavoro/disegni/casa.py

I colori sono in style.css (classi cs-, sg-, bs-, fn-, og-). La casa grande è disegnata con il centro della facciata a
x 730 e la base a y 760 (viewBox 1440×900, come il frontespizio); la casa piccola è la stessa scalata di 0,2 con la base
a y 552, il punto dove stava la casetta di prima.

Nell'apertura animata la terra, il sentiero e la luce continuano sotto il bordo del viewBox: al telefono la scena copre
anche la striscia dietro la barra di Safari, che si vede quando la barra si rimpicciolisce (style.css, 100lvh - 100svh).
"""
import math, pathlib, random, re, sys

SITO = pathlib.Path(__file__).resolve().parents[2]


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def luna(cx, cy, R, r, d, gradi=28):
    """La falce della luna crescente: il cerchio di raggio R meno il cerchio di raggio r spostato di d verso il lato
    buio (a sinistra, ruotato di «gradi» in senso orario), con il baricentro della parte chiara in (cx, cy), dove sta
    il centro del sole. Il tracciato è in coordinate assolute, perché le animazioni usano transform-box: fill-box."""
    a = math.radians(180 + gradi)
    ux, uy = math.cos(a), math.sin(a)            # dal centro del cerchio grande verso il lato buio
    vx, vy = -uy, ux
    x = (d * d + R * R - r * r) / (2 * d)        # la corda comune, a x dal centro grande
    h = math.sqrt(R * R - x * x)

    def segmento(raggio, distanza):
        """Area di un segmento circolare con la corda a «distanza» dal centro, e la distanza del suo baricentro."""
        t = math.acos(distanza / raggio)
        area = raggio * raggio * (t - math.sin(t) * math.cos(t))
        return area, 4 * raggio * math.sin(t) ** 3 / (3 * (2 * t - math.sin(2 * t)))

    # La parte comune ai due cerchi è il segmento del grande oltre la corda più quello del piccolo al di qua.
    a1, g1 = segmento(R, x)
    a2, g2 = segmento(r, d - x)
    comune = a1 + a2
    g = (a1 * g1 + a2 * (d - g2)) / comune
    sposta = g * comune / (math.pi * R * R - comune)
    ox, oy = cx + sposta * ux, cy + sposta * uy  # il centro del cerchio grande
    p = (ox + x * ux + h * vx, oy + x * uy + h * vy)
    q = (ox + x * ux - h * vx, oy + x * uy - h * vy)
    return (f"M{n(p[0])} {n(p[1])}A{n(R)} {n(R)} 0 1 1 {n(q[0])} {n(q[1])}"
            f"A{n(r)} {n(r)} 0 0 0 {n(p[0])} {n(p[1])}Z")


def astro(classe, cx, cy, alone, lume, sole, falce):
    """Il sole (di giorno) e la luna (di notte) nello stesso posto, con il loro alone caldo: .solo-giorno e
    .solo-notte in style.css ne mostrano uno con prefers-color-scheme. falce: R, r, d per luna()."""
    return (f'<g class="{classe}-astro"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(alone)}" fill="url(#{lume})"/>'
            f'<circle class="{classe}-sole solo-giorno" cx="{n(cx)}" cy="{n(cy)}" r="{n(sole)}"/>'
            f'<path class="{classe}-falce solo-notte" d="{luna(cx, cy, *falce)}"/></g>')


def stelline(seme, x0, y0, x1, y1, quante, rmin=0.8, rmax=1.9, sposta=None):
    rnd = random.Random(seme)
    stelle = [(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(rmin, rmax)) for _ in range(quante)]
    if sposta:
        stelle = sposta(stelle, seme)
    return "".join(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}"/>' for x, y, r in stelle)


# Le parole del frontespizio (la frase e il titolo) nelle coordinate del cielo, riga per riga: dove passano per tutto lo
# scorrimento, da quando le stelle cominciano ad accendersi a quando le parole se ne vanno, con 6 px di margine sullo
# schermo. Le ha misurate controlli/stelle.js al telefono (390×844 e 375×667) e sul computer (1440×900); se cambiano le
# parole o le loro misure in style.css, si rimisurano e si riscrivono qui.
PAROLE_FRONTE = [
    # 390×844
    (566, 123, 857, 232), (832, 123, 874, 232), (556, 158, 884, 264), (563, 192, 877, 295), (581, 227, 859, 327),
    (628, 261, 812, 359), (571, 332, 869, 480), (565, 424, 875, 508),
    # 375×667
    (524, 123, 893, 245), (862, 123, 916, 245), (512, 167, 928, 285), (521, 211, 919, 325), (544, 254, 896, 366),
    (603, 298, 837, 406), (531, 376, 909, 564), (521, 492, 919, 600),
    # 1440×900
    (455, 167, 985, 305), (404, 232, 1036, 365), (433, 297, 1007, 423), (301, 361, 1139, 483), (451, 450, 989, 671),
    (546, 607, 894, 689),
]
# Dove stanno il sole e la luna: sul computer, e al telefono, dove style.css li porta 390 più a sinistra e 110 più in
# alto. Le stelle spostate ne restano lontane, anche dalla parte buia della falce.
ASTRI = ((1300, 210), (910, 100))
# Le strisce del cielo che si vedono al telefono, largo 390 e 375 px; sul computer (1440×900) il cielo si vede da y 56
# in giù, sotto la testata.
STRISCE = ((497, 943), (444, 996))


def fuori_dalle_parole(stelle, seme):
    """Le stelle della volta che cadrebbero sulle parole del frontespizio (o sulla luna) vanno in un altro punto del
    cielo, libero, che si vede dagli stessi schermi: la stessa striscia del telefono, o fuori, dallo stesso lato. Così
    ogni telefono ha le stelle che aveva, nessuna su una lettera; le altre restano dove sono.
    Nella striscia del telefono il computer copre di parole quasi tutto il cielo sotto la frase, e lì resta libera solo
    la fascia in alto: per non ammucchiarle, ci vanno anche dove il computer ha la testata. Fuori dalla striscia
    restano dove il computer le vede. Il posto è il migliore di 12 punti liberi a caso, quello più lontano dalle altre
    stelle, così si spargono senza fare mucchi."""
    def libero(x, y, r):
        return (all(not (a - r <= x <= c + r and b - r <= y <= d + r) for a, b, c, d in PAROLE_FRONTE)
                and all(math.hypot(x - ax, y - ay) > 40 + r for ax, ay in ASTRI))

    def schermi(x, y):
        striscia = tuple(a <= x <= b for a, b in STRISCE)
        return striscia + (x < 720,) + (() if any(striscia) else (y >= 56,))

    def lontano_dai_bordi(x, y):
        return all(abs(x - b) > 8 for s in STRISCE for b in s) and abs(y - 56) > 6 and y > 6

    fuori = [s for s in stelle if libero(*s)]
    nuove = []
    for k, (x, y, r) in enumerate(stelle):
        if not libero(x, y, r):
            rnd = random.Random(seme * 1000 + k)
            punti = []
            while len(punti) < 12:
                x1, y1 = rnd.uniform(0, 1440), rnd.uniform(0, 520)
                if schermi(x1, y1) == schermi(x, y) and lontano_dai_bordi(x1, y1) and libero(x1, y1, r):
                    punti.append((x1, y1))
            x, y = max(punti, key=lambda p: min(math.hypot(p[0] - a, p[1] - b) for a, b, _ in fuori))
            fuori.append((x, y, r))
        nuove.append((x, y, r))
    return nuove


def cielo(prefisso):
    """Il cielo lontano dell'apertura (la «volta»: la classe «cielo» è già della sezione del mito), nel frontespizio e
    nella soglia: le stelle e il sole o la luna con il loro alone. Scorrendo si allarga piano intorno alla casa, meno
    del paesaggio, ed esce dall'alto dello schermo.
    Le stelle sono le stesse nei due cieli, ma nel frontespizio quelle che cadrebbero sulle parole sono spostate. Nella
    soglia restano tutte al loro posto: lì le parole non ci sono più (se ne vanno prima che la soglia compaia), e il
    cielo che si vede, più grande, è proprio quello in mezzo, che senza di loro al telefono resterebbe vuoto."""
    sposta = fuori_dalle_parole if prefisso == "fr" else None
    return (f'<g class="volta"><g class="volta-stelle">{stelline(17, 0, 0, 1440, 520, 80, sposta=sposta)}</g>'
            f'{astro("volta", 1300, 210, 80, f"{prefisso}-lume", 18, (26, 23, 13))}</g>')


def casa(cx=730.0, base=760.0, s=1.0, porta="chiusa"):
    """La casa del bosco: pareti di tronchi con le teste agli angoli, timpano di assi, tetto di scandole, comignolo di
    pietra con un filo di fumo, un po' di muschio, due finestre accese, la lanterna, la porta ad arco di assi e la legna
    accatastata sotto la gronda.
    porta: «chiusa» (una forma sola) o «mobile» (due metà che si aprono, con il vano acceso dietro)."""
    X = lambda x: n(cx + (x - 730) * s)
    Y = lambda y: n(base + (y - 760) * s)
    L = lambda v: n(v * s)
    p = [f'<path class="cs-fumo" stroke-width="{L(7)}" d="M{X(639)} {Y(446)}C{X(652)} {Y(426)} {X(624)} {Y(414)} {X(638)} {Y(394)}C{X(650)} {Y(378)} {X(628)} {Y(364)} {X(636)} {Y(346)}"/>',
         f'<rect class="cs-camino" x="{X(624)}" y="{Y(458)}" width="{L(30)}" height="{L(76)}"/>',
         f'<path class="cs-giunti" stroke-width="{L(2)}" d="M{X(624)} {Y(472)}H{X(654)}M{X(624)} {Y(488)}H{X(654)}M{X(639)} {Y(458)}V{Y(472)}M{X(647)} {Y(472)}V{Y(488)}M{X(631)} {Y(488)}V{Y(500)}"/>',
         f'<rect class="cs-camino-cima" x="{X(619)}" y="{Y(452)}" width="{L(40)}" height="{L(9)}"/>',
         f'<path class="cs-tetto" d="M{X(552)} {Y(578)}L{X(730)} {Y(428)}L{X(908)} {Y(578)}Z"/>']
    scandole = "".join(f"M{X(730 - (y - 428) * 1.1867)} {Y(y)}H{X(730 + (y - 428) * 1.1867)}" for y in (468, 500, 532, 564))
    p.append(f'<path class="cs-scandole" stroke-width="{L(2.5)}" d="{scandole}"/>')
    # Un po' di muschio sulle scandole, dove il timpano non lo copre.
    p.append('<g class="cs-muschio">' + "".join(f'<ellipse cx="{X(x)}" cy="{Y(y)}" rx="{L(rx)}" ry="{L(ry)}"/>'
             for x, y, rx, ry in ((588, 564, 13, 4.2), (606, 548, 8, 3), (872, 566, 12, 4), (700, 471, 8, 3), (760, 482, 9, 3.2))) + '</g>')
    p.append(f'<path class="cs-timpano" d="M{X(594)} {Y(574)}L{X(730)} {Y(458)}L{X(866)} {Y(574)}Z"/>')
    listelli = "".join(f"M{X(x)} {Y(574 - (min(x, 1460 - x) - 594) * 116 / 136)}V{Y(574)}" for x in (650, 690, 770, 810))
    p.append(f'<path class="cs-listelli" stroke-width="{L(3)}" d="{listelli}"/>')
    p.append(f'<rect class="cs-muro" x="{X(596)}" y="{Y(572)}" width="{L(268)}" height="{L(168)}"/>')
    p.append(f'<path class="cs-tronchi" stroke-width="{L(2.2)}" d="' + "".join(f"M{X(596)} {Y(y)}H{X(864)}" for y in range(587, 740, 15)) + '"/>')
    teste = [(x, 579.5 + 15 * k) for k in range(11) for x in (598, 862)]
    p.append('<g class="cs-teste">' + "".join(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{L(7.4)}"/>' for x, y in teste) + '</g>')
    p.append('<g class="cs-anelli">' + "".join(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{L(2.6)}"/>' for x, y in teste) + '</g>')
    p.append(f'<rect class="cs-pietra" x="{X(586)}" y="{Y(738)}" width="{L(288)}" height="{L(22)}"/>')
    p.append(f'<path class="cs-giunti" stroke-width="{L(2)}" d="M{X(586)} {Y(749)}H{X(874)}' + "".join(
        f"M{X(x)} {Y(738 if k % 2 else 749)}V{Y(749 if k % 2 else 760)}" for k, x in enumerate(range(606, 874, 22))) + '"/>')
    p.append(f'<circle class="cs-cornice" cx="{X(730)}" cy="{Y(528)}" r="{L(15)}"/>')
    p.append(f'<circle class="cs-vetro" cx="{X(730)}" cy="{Y(528)}" r="{L(10.5)}"/>')
    for x0 in (612, 796):
        p.append(f'<rect class="cs-cornice" x="{X(x0 - 5)}" y="{Y(601)}" width="{L(62)}" height="{L(70)}" rx="{L(3)}"/>')
        p.append(f'<rect class="cs-vetro" x="{X(x0)}" y="{Y(606)}" width="{L(52)}" height="{L(60)}"/>')
        p.append(f'<path class="cs-croce" stroke-width="{L(3.5)}" d="M{X(x0 + 26)} {Y(606)}V{Y(666)}M{X(x0)} {Y(634)}H{X(x0 + 52)}"/>')
        p.append(f'<rect class="cs-davanzale" x="{X(x0 - 8)}" y="{Y(670)}" width="{L(68)}" height="{L(7)}" rx="{L(2)}"/>')
    p.append(f'<path class="cs-staffa" stroke-width="{L(2.4)}" d="M{X(770)} {Y(650)}H{X(782)}V{Y(656)}"/>'
             f'<rect class="cs-lanterna" x="{X(776)}" y="{Y(656)}" width="{L(12)}" height="{L(18)}" rx="{L(2)}"/>'
             f'<rect class="cs-lanterna-luce" x="{X(778.5)}" y="{Y(659)}" width="{L(7)}" height="{L(12)}"/>')
    p.append(f'<path class="cs-stipite" d="M{X(690)} {Y(760)}V{Y(670)}A{L(40)} {L(40)} 0 0 1 {X(770)} {Y(670)}V{Y(760)}Z"/>')
    vano = f'M{X(700)} {Y(760)}V{Y(670)}A{L(30)} {L(30)} 0 0 1 {X(760)} {Y(670)}V{Y(760)}Z'
    if porta == "chiusa":
        p.append(f'<path class="cs-anta" d="{vano}"/>')
    else:
        # Il vano acceso, con uno scaffale e i suoi libri che si intravedono dentro.
        p.append(f'<path class="cs-vano" d="{vano}"/>')
        libri = [(705, 692, 6, 1), (712, 688, 7, 2), (720, 694, 5, 3), (726, 690, 6, 4)]
        p.append('<g class="cs-dentro">' + "".join(
            f'<rect class="cs-libro-{c}" x="{X(x)}" y="{Y(y)}" width="{L(w)}" height="{L(716 - y)}"/>' for x, y, w, c in libri)
            + f'<rect class="cs-libro-1" x="{X(734)}" y="{Y(693)}" width="{L(6)}" height="{L(23)}" transform="rotate(16 {X(740)} {Y(716)})"/>'
            + f'<rect class="cs-mensola" x="{X(701)}" y="{Y(716)}" width="{L(50)}" height="{L(4)}"/></g>')
        assi_su = f'M{X(715)} {Y(700)}V{Y(644)}M{X(730)} {Y(700)}V{Y(640)}M{X(745)} {Y(700)}V{Y(644)}'
        assi_giu = f'M{X(715)} {Y(700)}V{Y(760)}M{X(730)} {Y(700)}V{Y(760)}M{X(745)} {Y(700)}V{Y(760)}'
        su = f'M{X(700)} {Y(700.5)}V{Y(670)}A{L(30)} {L(30)} 0 0 1 {X(760)} {Y(670)}V{Y(700.5)}Z'
        p.append('<g class="cs-porta">'
                 f'<g class="cs-porta-su"><path class="cs-anta" d="{su}"/><path class="cs-assi" stroke-width="{L(2)}" d="{assi_su}"/>'
                 f'<path class="cs-anta-ombra" d="{su}"/></g>'
                 f'<g class="cs-porta-giu"><rect class="cs-anta" x="{X(700)}" y="{Y(699.5)}" width="{L(60)}" height="{L(60.5)}"/>'
                 f'<path class="cs-assi" stroke-width="{L(2)}" d="{assi_giu}"/><circle class="cs-pomello" cx="{X(751)}" cy="{Y(709)}" r="{L(3.2)}"/>'
                 f'<rect class="cs-anta-ombra" x="{X(700)}" y="{Y(699.5)}" width="{L(60)}" height="{L(60.5)}"/></g>'
                 '</g>')
    p.append(f'<rect class="cs-soglia" x="{X(684)}" y="{Y(760)}" width="{L(92)}" height="{L(9)}" rx="{L(2)}"/>')
    return "".join(p)


def legna(cx=730.0, base=760.0, s=1.0):
    """La legna accatastata sotto la gronda destra e un ceppo accanto al sentiero."""
    X = lambda x: n(cx + (x - 730) * s)
    Y = lambda y: n(base + (y - 760) * s)
    L = lambda v: n(v * s)
    teste = [(x, y) for y, xs in ((753, range(886, 960, 14)), (739, range(893, 953, 14)), (725, range(900, 946, 14)))
             for x in xs]
    return (f'<path class="cs-legna-fondo" d="M{X(878)} {Y(760)}V{Y(735)}L{X(904)} {Y(716)}H{X(944)}L{X(966)} {Y(735)}V{Y(760)}Z"/>'
            '<g class="cs-legna">' + "".join(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{L(7)}"/>' for x, y in teste) + '</g>'
            '<g class="cs-legna-anelli">' + "".join(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{L(2.4)}"/>' for x, y in teste) + '</g>'
            f'<rect class="cs-ceppo" x="{X(620)}" y="{Y(786)}" width="{L(38)}" height="{L(18)}"/>'
            f'<ellipse class="cs-ceppo-cima" cx="{X(639)}" cy="{Y(786)}" rx="{L(19)}" ry="{L(5.5)}"/>'
            f'<ellipse class="cs-legna-anelli" cx="{X(639)}" cy="{Y(786)}" rx="{L(9)}" ry="{L(2.6)}"/>')


def abete(x, base, h, larghezza=0.46):
    """Un abete piatto, a quattro palchi, con il suo tronco: una forma sola."""
    w = h * larghezza
    tronco = h * 0.1
    alto = h - tronco
    dx, sx = [], []
    for k in range(4):
        y = base - h + alto * (k + 1) / 4
        mezzo = w / 2 * (k + 1) / 4
        dx.append((x + mezzo, y))
        if k < 3:
            dx.append((x + mezzo * 0.42, y - alto / 4 * 0.18))
    sx = [(2 * x - px, py) for px, py in reversed(dx)]
    chioma = "M" + "L".join(f"{n(px)} {n(py)}" for px, py in [(x, base - h)] + dx + sx) + "Z"
    fusto = f"M{n(x - w * 0.05)} {n(base - tronco - 1)}H{n(x + w * 0.05)}V{n(base)}H{n(x - w * 0.05)}Z"
    return chioma, fusto


def faggio(x, base, h):
    """Un faggio: il tronco e la chioma tonda di tre cerchi."""
    def cerchio(cx, cy, r):
        return f"M{n(cx - r)} {n(cy)}a{n(r)} {n(r)} 0 1 0 {n(2 * r)} 0a{n(r)} {n(r)} 0 1 0 {n(-2 * r)} 0Z"
    chioma = (cerchio(x, base - h * 0.64, h * 0.3) + cerchio(x - h * 0.2, base - h * 0.5, h * 0.22)
              + cerchio(x + h * 0.2, base - h * 0.52, h * 0.22))
    fusto = f"M{n(x - h * 0.035)} {n(base - h * 0.38)}H{n(x + h * 0.035)}V{n(base)}H{n(x - h * 0.035)}Z"
    return chioma, fusto


def pino(x, base, h):
    """Un pino laricio: il tronco alto e la chioma piatta, a ombrello."""
    def ellisse(cx, cy, rx, ry):
        return f"M{n(cx - rx)} {n(cy)}a{n(rx)} {n(ry)} 0 1 0 {n(2 * rx)} 0a{n(rx)} {n(ry)} 0 1 0 {n(-2 * rx)} 0Z"
    chioma = ellisse(x, base - h * 0.74, h * 0.34, h * 0.12) + ellisse(x - h * 0.08, base - h * 0.86, h * 0.22, h * 0.09)
    fusto = f"M{n(x - h * 0.03)} {n(base - h * 0.76)}H{n(x + h * 0.03)}V{n(base)}H{n(x - h * 0.03)}Z"
    return chioma, fusto


def bosco(cx=730.0, base=760.0, s=1.0):
    """Il bosco intorno alla casa, misurato come la casa: due abeti alti alle spalle, più alti del tetto, che restano
    nell'inquadratura fino alla porta; intorno altri abeti, un faggio e un pino laricio."""
    X = lambda x: cx + (x - 730) * s
    Y = lambda y: base + (y - 760) * s
    gruppi = {"cs-abete": [], "cs-abete-lontano": [], "cs-faggio": [], "cs-pino": []}
    fusti = []
    for tipo, x, b, h in (("abete", 262, 818, 150), ("abete", 1222, 822, 160), ("abete", 336, 806, 185),
                          ("pino", 1138, 812, 235), ("faggio", 420, 794, 215), ("abete", 1052, 798, 250),
                          ("abete", 512, 752, 300), ("abete", 960, 754, 330), ("abete", 612, 612, 370),
                          ("abete", 858, 608, 400)):
        forma = {"abete": abete, "faggio": faggio, "pino": pino}[tipo]
        chioma, fusto = forma(X(x), Y(b), h * s)
        classe = {"abete": "cs-abete" if h >= 230 else "cs-abete-lontano", "faggio": "cs-faggio", "pino": "cs-pino"}[tipo]
        gruppi[classe].append(chioma)
        fusti.append(fusto)
    return (f'<path class="cs-tronco" d="{"".join(fusti)}"/>'
            + "".join(f'<path class="{c}" d="{"".join(v)}"/>' for c, v in gruppi.items() if v))


def fila(cresta, seme, hmin, hmax, passo, classe, simbolo):
    """Una fila di alberi piccoli lungo il crinale di una collina (una spezzata di punti): abeti, faggi e pini (alti
    100, nei defs con gli id simbolo-ab, simbolo-fg, simbolo-pn) ripetuti con <use>, spostati e scalati."""
    rnd = random.Random(seme)
    usi = []
    for (x0, y0), (x1, y1) in zip(cresta, cresta[1:]):
        x = x0 + rnd.uniform(0, passo)
        while x < x1:
            y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            h = rnd.uniform(hmin, hmax)
            caso = rnd.random()
            tipo = "ab" if caso < 0.6 else "fg" if caso < 0.85 else "pn"
            usi.append(f'<use href="#{simbolo}-{tipo}" transform="translate({n(x)} {n(y + h * 0.12)}) scale({h / 100:.3f})"/>')
            x += passo * rnd.uniform(0.7, 1.3)
    return f'<g class="{classe}">{"".join(usi)}</g>'


def abete_tipo(simbolo):
    """I tre alberi delle file, alti 100, ognuno con il suo tronco nella stessa forma."""
    forme = {"ab": abete(0, 0, 100, 0.5), "fg": faggio(0, 0, 100), "pn": pino(0, 0, 100)}
    return "".join(f'<path id="{simbolo}-{k}" d="{c}{f}"/>' for k, (c, f) in forme.items())


def cespugli(cx=730.0, base=760.0, s=1.0):
    X = lambda x: n(cx + (x - 730) * s)
    Y = lambda y: n(base + (y - 760) * s)
    L = lambda v: n(v * s)
    return ('<g class="cs-cespugli">'
            f'<circle cx="{X(566)}" cy="{Y(752)}" r="{L(30)}"/><circle cx="{X(598)}" cy="{Y(760)}" r="{L(22)}"/>'
            f'<circle cx="{X(984)}" cy="{Y(764)}" r="{L(18)}"/></g>')


# La collina e il sentiero dell'apertura (coordinate del frontespizio prima che la terra scenda), con la casa piccola
# in cima: il sentiero sale a tornanti dal basso a sinistra. Tutti e due scendono sotto il bordo (y 900), fino alla
# striscia dietro la barra di Safari: il primo tratto del sentiero continua dritto verso il basso a sinistra.
COLLINA = "M0 712C210 700 420 650 560 598C640 568 690 552 730 552C790 552 870 576 960 614C1100 674 1300 704 1440 712V1400H0Z"
SENTIERO = "M167 1100L828 814Q860 800 836 780L668 726Q638 715 664 700L782 652Q803 642 785 631L716 598Q700 590 716 578L730 566"


def lago():
    """Il laghetto nella conca del primo tornante, fra i due tratti più bassi del sentiero: l'acqua che riflette il
    cielo, la riva di sassi e i giunchi a sinistra; di notte nell'acqua le stelle e il riflesso caldo delle finestre
    accese."""
    cx, cy = 702.0, 802.0
    P = lambda dx, dy: f"{n(cx + dx)} {n(cy + dy)}"
    acqua = (f"M{P(-62, 2)}C{P(-60, -12)} {P(-20, -17)} {P(8, -16)}C{P(40, -15)} {P(64, -9)} {P(62, 2)}"
             f"C{P(60, 13)} {P(30, 18)} {P(-4, 17)}C{P(-36, 16)} {P(-64, 12)} {P(-62, 2)}Z")
    luce = f"M{P(-46, -6)}C{P(-20, -12)} {P(30, -12)} {P(50, -5)}C{P(30, -2)} {P(-20, -2)} {P(-46, -6)}Z"
    rnd = random.Random(9)
    sassi = "".join(f'<ellipse cx="{n(cx + 64 * math.cos(a))}" cy="{n(cy + 3 + 17 * math.sin(a))}" rx="{n(rnd.uniform(3.6, 5.6))}" ry="{n(rnd.uniform(2.2, 3.2))}"/>'
                    for a in (math.radians(g) for g in (4, 22, 40, 58, 76, 96, 116, 136, 156, 176, -12)))
    giunchi = "".join(f"M{P(dx, dy)}l{n(dx * 0.04)} {n(-h)}" for dx, dy, h in
                      ((-70, 6, 22), (-66, 8, 28), (-62, 5, 18), (-58, 9, 25), (-54, 7, 15), (-50, 10, 20)))
    teste = "".join(f'<ellipse cx="{n(cx + dx * 1.04)}" cy="{n(cy + dy - h + 4)}" rx="1.5" ry="3.6"/>'
                    for dx, dy, h in ((-66, 8, 28), (-58, 9, 25), (-50, 10, 20)))
    stelle = "".join(f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy)}" r="{r}"/>'
                     for dx, dy, r in ((-38, 1, 1), (-18, 8, .8), (20, -4, 1.1), (44, 6, .9), (-2, 12, .8)))
    finestre = 730 + (638 - 730) * 0.2, 730 + (822 - 730) * 0.2
    # Il riflesso di una luce sull'acqua: una colonna rotta in trattini, sempre più stretti verso di noi.
    riflesso = "".join(f'<rect x="{n(x - w / 2)}" y="{n(cy + dy)}" width="{w}" height="{h}" rx="{h / 2}"/>'
                       for x in finestre for dy, w, h in ((-10, 6, 3), (-5.5, 4.6, 2.6), (-1.5, 3.4, 2.2), (2.2, 2.2, 1.8)))
    return (f'<g class="lago"><path class="lg-acqua" d="{acqua}"/><path class="lg-luce" d="{luce}"/>'
            f'<g class="lg-stelle">{stelle}</g><g class="lg-riflesso">{riflesso}</g><g class="lg-sassi">{sassi}</g>'
            f'<path class="lg-giunchi" d="{giunchi}"/><g class="lg-teste">{teste}</g></g>')


def colle():
    """La collina dell'apertura della home con quello che c'è sopra: il laghetto, il sentiero, la luce intorno alla
    casa piccola e la casa con i suoi alberi, a un quinto della casa grande della soglia."""
    return (f'<path class="fr-collina" d="{COLLINA}"/>{lago()}<path class="fr-sentiero" d="{SENTIERO}"/>'
            '<circle cx="730" cy="532" r="66" fill="url(#fr-lume)"/>'
            f'{bosco(base=552, s=0.2)}<g class="cs">{casa(base=552, s=0.2)}{legna(base=552, s=0.2)}</g>')


# I crinali delle colline della soglia, per le file di abeti (da -760 a 2200: quello che si vede quando si avvicina).
MONTI = [(-760, 666), (-400, 650), (0, 662), (220, 640), (420, 628), (640, 640), (820, 622), (980, 616), (1160, 632),
         (1450, 644), (1700, 648), (2200, 646)]
COLLI = [(-760, 737), (-200, 730), (160, 738), (340, 722), (520, 712), (700, 716), (880, 708), (1060, 708), (1300, 730),
         (1700, 746), (2200, 756)]
# Il crinale dei colli del frontespizio (dentro .fr-terra).
COLLI_FRONTE = [(0, 604), (120, 585), (240, 580), (360, 578), (470, 562), (600, 540), (760, 527), (900, 550),
                (1040, 575), (1180, 590), (1320, 572), (1440, 568)]


def soglia():
    """La casa da vicino. Fuori dai gruppi che si avvicinano resta il cielo, uguale a quello del frontespizio; sopra
    tutto, la luce che riempie lo schermo. Terra, sentiero e luce scendono fino a y 1800: la casa compare a 0,406 della
    sua misura, e la striscia sotto il bordo, a quella misura, arriva quasi a y 1400."""
    return (
        '<svg class="soglia-disegno" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">'
        '<defs>'
        '<linearGradient id="sg-notte" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04070C"/><stop offset=".6" stop-color="#0A1322"/><stop offset="1" stop-color="#172741"/></linearGradient>'
        '<linearGradient id="sg-alba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="sg-alba-0"/><stop offset="1" class="sg-alba-1"/></linearGradient>'
        '<radialGradient id="sg-lume"><stop offset="0" stop-color="#FFC85A" stop-opacity=".7"/><stop offset=".45" stop-color="#FFC85A" stop-opacity=".2"/><stop offset="1" stop-color="#FFC85A" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="sg-tappeto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFC85A" stop-opacity=".8"/><stop offset="1" stop-color="#FFC85A" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="sg-alone-g"><stop offset="0" class="sg-alone-0"/><stop offset=".55" class="sg-alone-1"/><stop offset="1" class="sg-alone-2"/></radialGradient>'
        f'{abete_tipo("sg")}'
        '</defs>'
        '<rect class="sg-cielo" width="1440" height="900"/>'
        f'{cielo("sg")}'
        '<g class="sg-avvicina"><g class="sg-entra">'
        '<rect class="sg-alba" x="-1500" y="470" width="4440" height="260" fill="url(#sg-alba)"/>'
        '<path class="sg-monti" d="M-1500 700C-900 650-400 640 0 662S420 610 640 640S980 600 1160 632S1700 650 2940 640V1800H-1500Z"/>'
        f'{fila(MONTI, 21, 22, 40, 40, "cs-bosco-lontanissimo", "sg")}'
        '<path class="sg-colli" d="M-1500 760C-800 730-200 720 160 738S520 700 700 716S1060 704 1300 730S2200 760 2940 750V1800H-1500Z"/>'
        f'{fila(COLLI, 22, 40, 75, 44, "cs-bosco-lontano", "sg")}'
        '<path class="sg-terra" d="M-1500 900C-700 870-60 820 300 790C470 776 560 768 640 765H820C900 768 990 776 1160 790C1520 820 2140 870 2940 900V1800H-1500Z"/>'
        f'{bosco()}'
        '<path class="sg-sentiero" d="M520 1800L560 1400C590 1100 640 980 700 900C716 870 722 820 714 769H746C752 820 760 880 800 940C860 1020 900 1120 930 1400L970 1800Z"/>'
        '<path class="sg-tappeto" d="M700 768H760L846 920H612Z" fill="url(#sg-tappeto)"/>'
        '<g class="sg-lumi"><circle cx="638" cy="636" r="74" fill="url(#sg-lume)"/><circle cx="822" cy="636" r="74" fill="url(#sg-lume)"/>'
        '<circle class="sg-lume-porta" cx="730" cy="712" r="96" fill="url(#sg-lume)"/></g>'
        f'<g class="cs">{casa(porta="mobile")}{legna()}</g>'
        f'{cespugli()}'
        '<circle class="sg-alone" cx="730" cy="705" r="150" fill="url(#sg-alone-g)"/>'
        '<path class="sg-raggio" d="M700 760V670A30 30 0 0 1 760 670V760Z"/>'
        '</g></g>'
        '<rect class="sg-luce" x="-10" y="-10" width="1460" height="1820"/>'
        '</svg>')


def bosco_fronte():
    """Il bosco sui colli dell'apertura della home, con il suo abete nei defs."""
    return f'<defs>{abete_tipo("fr")}</defs>{fila(COLLI_FRONTE, 31, 10, 20, 18, "cs-bosco-lontano", "fr")}'


def bottega_studio():
    """La casa a metà strada, per l'apertura dello studio: largo 1200×460, la casa al centro, il sentiero che sale."""
    s, cx, base = 0.56, 600.0, 356.0
    return (
        '<svg class="bottega" viewBox="0 0 1200 460" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">'
        '<defs>'
        '<linearGradient id="bs-notte" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080D"/><stop offset="1" stop-color="#1A2B48"/></linearGradient>'
        '<radialGradient id="bs-lume"><stop offset="0" stop-color="#FFC85A" stop-opacity=".75"/><stop offset=".45" stop-color="#FFC85A" stop-opacity=".2"/><stop offset="1" stop-color="#FFC85A" stop-opacity="0"/></radialGradient>'
        f'{abete_tipo("bs")}'
        '</defs>'
        '<rect class="bs-cielo" width="1200" height="460"/>'
        f'<g class="bs-stelle">{stelline(11, 0, 0, 1200, 250, 46, 0.7, 1.6)}</g>'
        f'{astro("bs", 820, 81, 44, "bs-lume", 10.5, (14.5, 12.8, 7.2))}'
        '<path class="bs-monti" d="M0 286C140 252 260 262 380 276S600 236 760 258S1020 270 1200 250V460H0Z"/>'
        '<path class="bs-colli" d="M0 330C160 306 300 316 420 322S620 300 760 310S1020 330 1200 318V460H0Z"/>'
        f'{fila([(0, 330), (160, 312), (300, 316), (420, 320), (560, 306), (760, 310), (900, 318), (1020, 326), (1200, 318)], 41, 14, 26, 20, "cs-bosco-lontano", "bs")}'
        '<path class="bs-terra" d="M0 420C160 400 330 372 470 358C520 354 560 352 600 352C660 352 720 356 790 364C930 380 1080 402 1200 414V460H0Z"/>'
        '<path class="bs-sentiero" pathLength="1" d="M330 470C380 450 470 432 520 420Q556 410 530 396L486 386Q470 380 492 374L560 362Q600 356 600 354"/>'
        f'<g class="bs-lume"><circle cx="{n(cx - 92 * s)}" cy="{n(base - 124 * s)}" r="46" fill="url(#bs-lume)"/>'
        f'<circle cx="{n(cx + 92 * s)}" cy="{n(base - 124 * s)}" r="46" fill="url(#bs-lume)"/></g>'
        f'{bosco(cx=cx, base=base, s=s)}'
        f'<g class="cs">{casa(cx=cx, base=base, s=s)}{legna(cx=cx, base=base, s=s)}</g>'
        f'{cespugli(cx=cx, base=base, s=s)}'
        '</svg>')


def finestra():
    """La finestra della bottega, più alta che larga come in una casa di tronchi: fuori il cielo di prima, con il sole
    o la luna e le colline; sul davanzale, dentro, la pianta."""
    return (
        '<svg class="finestra-disegno" viewBox="-12 0 324 404" aria-hidden="true" focusable="false">'
        '<defs><linearGradient id="fn-notte" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080D"/><stop offset="1" stop-color="#1A2B48"/></linearGradient>'
        '<linearGradient id="fn-alba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="fn-alba-0"/><stop offset="1" class="fn-alba-1"/></linearGradient>'
        '<radialGradient id="fn-lume"><stop offset="0" stop-color="#FFC85A" stop-opacity=".6"/><stop offset=".45" stop-color="#FFC85A" stop-opacity=".18"/><stop offset="1" stop-color="#FFC85A" stop-opacity="0"/></radialGradient></defs>'
        '<rect class="fn-telaio" x="0" y="0" width="300" height="390" rx="5"/>'
        '<rect class="fn-cielo" x="13" y="13" width="274" height="364"/>'
        '<rect x="13" y="200" width="274" height="177" fill="url(#fn-alba)"/>'
        f'<g class="fn-stelle">{stelline(5, 16, 16, 284, 250, 34, 0.6, 1.4)}</g>'
        f'{astro("fn", 222, 76, 38, "fn-lume", 10, (14, 12.4, 7))}'
        '<path class="fn-monti" d="M13 316C60 300 100 304 140 310S210 290 250 302S280 306 287 304V377H13Z"/>'
        '<path class="fn-colli" d="M13 342C70 328 120 336 170 331S250 338 287 333V377H13Z"/>'
        '<path class="fn-abeti" d="' + "".join(abete(x, y, h, 0.5)[0] for x, y, h in ((40, 342, 38), (64, 348, 52), (92, 340, 30), (206, 340, 34), (232, 348, 54), (262, 343, 40))) + '"/>'
        '<path class="fn-montanti" d="M150 13V377M13 196H287"/>'
        '<rect class="fn-davanzale" x="-10" y="386" width="320" height="14" rx="3"/>'
        f'<g transform="translate(212 278)">{pianta()}</g>'
        '</svg>')


def matita():
    """Il libro del gioco: un libro vero, tutto a matita, quasi alto come Argonauta. Il dorso con le sue fasce, lo
    spessore delle pagine in cima e sul taglio, la cornice della copertina e il tratteggio lasciati a metà, due righe
    per un titolo che non c'è ancora; accanto, appoggiata al libro, una matita. Niente nomi, segni o disegni del gioco."""
    rnd = random.Random(3)
    def tratto(x0, y0, x1, y1, passi=6, j=1.4):
        pts = [(x0 + (x1 - x0) * k / passi + rnd.uniform(-j, j), y0 + (y1 - y0) * k / passi + rnd.uniform(-j, j))
               for k in range(passi + 1)]
        return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts)
    # La copertina va da x 0 a 196 e da y 12 a 300; le pagine sporgono dietro di 6 in alto a destra.
    contorno = " ".join([tratto(1, 12, 196, 12), tratto(196, 11, 197, 300), tratto(197, 299, 1, 300), tratto(0, 300, 1, 12),
                         tratto(2, 13, 195, 14, j=2), tratto(195, 12, 196, 298, j=2)])
    pagine = "M1 12L7 6H202L196 12ZM196 12L202 6V294L196 300Z"
    righe_pagine = (tratto(10, 9.5, 197, 9.5, 5, 0.4) + tratto(14, 7.8, 199, 7.8, 5, 0.4)
                    + tratto(198, 11, 198, 296, 6, 0.4) + tratto(200, 9, 200, 295, 6, 0.4))
    dorso = (tratto(15, 13, 15, 299, 8, 0.8) + tratto(17.5, 13, 17.5, 299, 8, 0.8)
             + "".join(tratto(1, y, 15, y, 2, 0.6) for y in (38, 43, 268, 273)))
    # La cornice della copertina: tre lati e mezzo, l'ultimo lasciato a metà.
    cornice = (tratto(32, 34, 180, 33, 6, 1) + tratto(180, 33, 181, 276, 7, 1) + tratto(181, 277, 32, 277, 6, 1)
               + tratto(31, 277, 32, 170, 4, 1))
    # Il tratteggio: righe a 45° dall'angolo in alto a sinistra, che la mano ha lasciato sempre più corte verso il
    # centro della copertina; vicino all'angolo un tratteggio incrociato, più fitto.
    tratteggio = []
    for k in range(32):
        c = 76 + 7 * k + rnd.uniform(-1.2, 1.2)               # la riga x + y = c, dentro la cornice
        xa, ya = (34.0, c - 34) if c - 34 <= 274 else (c - 274, 274.0)
        xb, yb = (c - 37, 37.0) if c - 37 <= 177 else (177.0, c - 177)
        quanto = min(1.0, max(0.18, 1 - (c - 210) / 110)) + rnd.uniform(-0.07, 0.07)
        xa, ya = xb + (xa - xb) * quanto, yb + (ya - yb) * quanto
        if xb - xa > 3:
            tratteggio.append(f"M{n(xa)} {n(ya)}L{n(xb)} {n(yb)}")
    croce = "".join(f"M{n(37 + 6.5 * k)} 37L{n(71 + 2.5 * k)} {n(71 - 4 * k)}" for k in range(8))
    titolo = tratto(86, 226, 166, 224, 5, 1.6) + " " + tratto(98, 240, 154, 239, 4, 1.4)
    # La matita, appoggiata al taglio del libro: la gomma sul ripiano, la punta in alto contro il libro.
    bx, by, tx, ty = 219.0, 299.0, 200.0, 70.0
    lx, ly = tx - bx, ty - by
    lung = math.hypot(lx, ly)
    ux, uy = lx / lung, ly / lung
    nx, ny = -uy, ux
    def pezzo(d0, d1, m0, m1):
        a = (bx + ux * d0 + nx * m0, by + uy * d0 + ny * m0)
        b = (bx + ux * d1 + nx * m1, by + uy * d1 + ny * m1)
        c = (bx + ux * d1 - nx * m1, by + uy * d1 - ny * m1)
        d = (bx + ux * d0 - nx * m0, by + uy * d0 - ny * m0)
        return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in (a, b, c, d)) + "Z"
    lati = f"M{n(bx + ux * 24)} {n(by + uy * 24)}L{n(bx + ux * (lung - 30))} {n(by + uy * (lung - 30))}"
    return ('<svg class="matita-disegno" viewBox="0 0 226 302" aria-hidden="true" focusable="false">'
            '<path class="mt-ombra" d="M8 20H204V302H8Z"/>'
            f'<path class="mt-pagine" d="{pagine}"/><path class="mt-carta" d="M0 12H196V300H0Z"/>'
            f'<path class="mt-righe" d="{righe_pagine}{"".join(tratteggio)}{croce}"/>'
            f'<path class="mt-contorno" d="{contorno} {cornice} {dorso}"/><path class="mt-schizzo" d="{titolo}"/>'
            f'<path class="mt-gomma" d="{pezzo(0, 13, 4.6, 4.6)}"/><path class="mt-ghiera" d="{pezzo(13, 24, 4.9, 4.9)}"/>'
            f'<path class="mt-matita" d="{pezzo(24, lung - 30, 4.6, 4.6)}"/><path class="mt-legno" d="{pezzo(lung - 30, lung - 8, 4.6, 1.6)}"/>'
            f'<path class="mt-mina" d="{pezzo(lung - 8, lung, 1.6, 0.2)}"/><path class="mt-lato" d="{lati}"/>'
            '</svg>')


def pianta():
    """La pianta nel vaso, da mettere dentro un altro disegno (larga 80, alta 110, il fondo del vaso a y 108): oggi sul
    davanzale della finestra della bottega."""
    return ('<path class="og-foglia" d="M40 66C26 54 14 50 6 54C14 66 26 70 40 70Z"/>'
             '<path class="og-foglia" d="M40 62C40 44 46 28 58 20C62 36 56 52 40 66Z"/>'
             '<path class="og-foglia-2" d="M40 64C34 46 24 34 12 30C12 46 22 58 40 68Z"/>'
             '<path class="og-foglia-2" d="M41 66C54 56 66 54 76 58C68 70 56 72 41 70Z"/>'
             '<path class="og-vaso" d="M20 70H60L55 108H25Z"/><rect class="og-orlo" x="17" y="66" width="46" height="9" rx="2"/>')


def lampada():
    """La lampada a olio dello scrittoio, alta come si deve accanto al quaderno: il serbatoio, il becco e il vetro alto
    con la fiamma, la base e l'ansa."""
    return ('<svg class="lampada-disegno" viewBox="0 0 80 150" aria-hidden="true" focusable="false">'
            '<defs><radialGradient id="og-alone"><stop offset="0" stop-color="#FFC85A" stop-opacity=".55"/><stop offset="1" stop-color="#FFC85A" stop-opacity="0"/></radialGradient></defs>'
            '<circle cx="40" cy="66" r="44" fill="url(#og-alone)"/>'
            '<path class="og-vetro" d="M29 96C21 84 21 64 31 52C34 47 35 41 35 33H45C45 41 46 47 49 52C59 64 59 84 51 96Z"/>'
            '<path class="og-fiamma" d="M40 58C46 66 47 75 40 82C33 75 34 66 40 58Z"/>'
            '<path class="og-corpo" d="M33 28H47V33H33ZM26 96H54V103H26ZM22 103H58C66 110 66 124 57 130H23C14 124 14 110 22 103Z"/>'
            '<path class="og-manico" d="M60 110C75 110 77 127 61 127"/><rect class="og-base" x="14" y="130" width="52" height="10" rx="3"/>'
            '</svg>')


SEGNI = {"cielo-fronte": lambda: cielo("fr"), "colle": colle, "bosco-fronte": bosco_fronte, "soglia": soglia, "bottega-studio": bottega_studio, "finestra": finestra,
         "matita": matita, "lampada": lampada}
PAGINE = ["index.html", "en/index.html", "studio/index.html", "en/studio/index.html"]


def main():
    for f in PAGINE:
        p = SITO / f
        t = p.read_text(encoding="utf-8")
        cambiati = []
        for segno, fn in SEGNI.items():
            a, b = f"<!-- {segno}:inizio -->", f"<!-- {segno}:fine -->"
            if a not in t:
                continue
            t = re.sub(re.escape(a) + r".*?" + re.escape(b), lambda m: a + fn() + b, t, flags=re.S)
            cambiati.append(segno)
        p.write_text(t, encoding="utf-8")
        print(f, ", ".join(cambiati) or "niente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
