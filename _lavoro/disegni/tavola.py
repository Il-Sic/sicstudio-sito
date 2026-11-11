"""La tavola del giorno: la home che cambia con la data.

La mano e la coreografia della home restano quelle di casa.py e di style.css. Cambia ciò che la scena mostra:
- di sera, il cielo verso sud due ore dopo il tramonto, visto dal centro della Calabria: le stelle con il loro
  colore, le figure e i nomi delle costellazioni, i pianeti, la Via Lattea, due nebulose, due ammassi, una galassia, e
  la luna con la fase di quella notte (anche nella finestra della bottega);
- di giorno, il sole più basso d'inverno e più alto d'estate, e le rondini da fine marzo a settembre;
- sempre, i colori della stagione (classi tv- su <main>, in style.css): il faggio che arrossa, la nebbia di novembre,
  la neve, i fiori, le lucciole;
- in testa alla scena, la data della tavola.
Nel browser non gira niente: tutto è calcolato qui e scritto nell'HTML.

Le pagine in git restano quelle di sempre, senza data: questo script non le tocca. Scrive la tavola in una copia del
sito già costruito, ed è il lavoro giornaliero (.github/workflows/tavola.yml), quando è acceso, a pubblicarla.

    python3 -I _lavoro/disegni/tavola.py <cartella> [AAAA-MM-GG]   la tavola in <cartella>/index.html e /en/index.html
    python3 -I _lavoro/disegni/tavola.py --prova [AAAA-MM-GG]      la scrive in _lavoro/prove/tavola/, da guardare con
                                                                   servi.py (http://127.0.0.1:8765/_lavoro/prove/tavola/)
    python3 -I _lavoro/disegni/tavola.py --verifica                rifà i conti su date note (esce con 1 se non tornano)
    python3 -I _lavoro/disegni/tavola.py --estrai <bsc5.dat.gz>    rifà stelle.tsv dal catalogo (serve una volta)

Che cosa è vero e che cosa no:
- le stelle: posizione, grandezza e colore vengono dal Bright Star Catalogue (vedi «Le stelle», più sotto); sono
  tutte quelle fino alla grandezza 4,7 (al telefono 4,1), più quelle delle figure: il cielo di un posto abbastanza buio;
- le linee e la scelta delle stelle sono un disegno; i pianeti (Venere, Marte, Giove, Saturno) sono calcolati dalle
  orbite medie del JPL, entro mezzo grado; la Via Lattea sta dov'è davvero, ma il suo chiarore e la polvere di stelle
  minute sono disegnati, non misurati; quando c'è la luna in cielo la Via Lattea si spegne, come accade;
- la luna ha la fase vera, ma sta dove la mette il disegno della home, non dove sta in cielo; è ingrandita;
- il luogo è un punto convenzionale (39,3° N, 16,3° E), non la casa di nessuno;
- le date delle stagioni (quando nevica, quando il faggio arrossa) sono stimate, da correggere con chi ci vive.

Le stelle non cadono mai sulle parole del frontespizio (sembrerebbero accenti): quelle che ci cadrebbero, le linee e i
nomi compaiono quando le parole se ne sono andate (.tv-dopo in style.css). Le righe delle parole sono quelle misurate
per casa.py (PAROLE_FRONTE).
"""
import datetime
import math
import pathlib
import random
import re
import sys
import zoneinfo

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(QUI))
LAT, LON = 39.3, 16.3
ROMA = zoneinfo.ZoneInfo("Europe/Rome")
MESI = {"it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
        "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}
PAGINE = {"index.html": "it", "en/index.html": "en"}

# I nomi nel cielo sono scritti in italiano qui sotto; nella pagina inglese diventano questi (le costellazioni in
# latino, come si usa). Quelli che mancano restano uguali.
IN_INGLESE = {
    "Orione": "Orion", "il Cane Maggiore": "Canis Major", "il Cane Minore": "Canis Minor", "i Gemelli": "Gemini", "il Toro": "Taurus",
    "l’Auriga": "Auriga", "il Leone": "Leo", "il Cancro": "Cancer", "la Vergine": "Virgo", "Boote": "Boötes", "la Corona Boreale": "Corona Borealis",
    "Ercole": "Hercules", "Ofiuco": "Ophiuchus", "il Serpente": "Serpens", "la Bilancia": "Libra", "lo Scorpione": "Scorpius",
    "il Sagittario": "Sagittarius", "il Capricorno": "Capricornus", "l’Acquario": "Aquarius", "i Pesci": "Pisces", "la Balena": "Cetus",
    "l’Ariete": "Aries", "il Triangolo": "Triangulum", "Pegaso": "Pegasus", "il Cigno": "Cygnus", "la Lira": "Lyra", "l’Aquila": "Aquila",
    "il Delfino": "Delphinus", "la Freccia": "Sagitta", "l’Idra": "Hydra", "il Corvo": "Corvus", "la Coppa": "Crater", "la Lepre": "Lepus",
    "la Colomba": "Columba", "Eridano": "Eridanus", "la Poppa": "Puppis", "Perseo": "Perseus", "Cassiopea": "Cassiopeia",
    "l’Orsa Maggiore": "Ursa Major", "il Pesce Australe": "Piscis Austrinus",
    "Sirio": "Sirius", "Arturo": "Arcturus", "Spiga": "Spica", "Procione": "Procyon", "Regolo": "Regulus", "Castore": "Castor", "Polluce": "Pollux",
    "le Pleiadi": "the Pleiades", "Venere": "Venus", "Marte": "Mars", "Giove": "Jupiter", "Saturno": "Saturn",
    "la nebulosa di Orione": "the Orion Nebula", "la nebulosa Laguna": "the Lagoon Nebula", "il Presepe": "the Beehive",
    "la galassia di Andromeda": "the Andromeda Galaxy", "la Via Lattea": "the Milky Way",
}
# La riga in testa alla scena: la data e la luna.
CON_LA_LUNA = {
    "it": {"nuova": "con la luna nuova", "crescente": "con la luna crescente", "primo": "con la luna al primo quarto", "piena": "con la luna piena",
           "calante": "con la luna calante", "ultimo": "con la luna all’ultimo quarto"},
    "en": {"nuova": "with a new moon", "crescente": "with a waxing moon", "primo": "with the moon at first quarter", "piena": "with a full moon",
           "calante": "with a waning moon", "ultimo": "with the moon at last quarter"},
}

# Le righe delle parole del frontespizio nelle coordinate del cielo, misurate per casa.py: prima al telefono (390×844
# e 375×667), poi sul computer (1440×900). Se casa.py non le ha più, nessuna stella viene spostata.
try:
    from casa import PAROLE_FRONTE
except Exception:
    PAROLE_FRONTE = []
PAROLE = {True: PAROLE_FRONTE[:16], False: PAROLE_FRONTE[16:]} if len(PAROLE_FRONTE) == 22 else {True: PAROLE_FRONTE, False: PAROLE_FRONTE}


def n(v):
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


# ---------- I conti ----------

def giuliano(quando):
    """Il giorno giuliano di un istante (con il suo fuso)."""
    u = quando.astimezone(datetime.timezone.utc)
    return 2440587.5 + u.timestamp() / 86400


def sole_e_luna(jd):
    """Longitudine del sole e della luna (formule a bassa precisione dell'Astronomical Almanac: entro mezzo grado),
    la loro distanza in cielo (0 luna nuova, 180 piena) e la declinazione del sole."""
    d = jd - 2451545.0
    t = d / 36525
    s = math.sin
    r = math.radians
    g = r(357.528 + 0.9856003 * d)
    sole = (280.460 + 0.9856474 * d + 1.915 * s(g) + 0.020 * s(2 * g)) % 360
    luna = (218.32 + 481267.881 * t + 6.29 * s(r(135.0 + 477198.87 * t)) - 1.27 * s(r(259.3 - 413335.36 * t)) + 0.66 * s(r(235.7 + 890534.22 * t))
            + 0.21 * s(r(269.9 + 954397.74 * t)) - 0.19 * s(r(357.5 + 35999.05 * t)) - 0.11 * s(r(186.5 + 966404.03 * t))) % 360
    declinazione = math.degrees(math.asin(s(r(23.439 - 0.0000004 * d)) * s(r(sole))))
    return sole, luna, (luna - sole) % 360, declinazione


def tempo_siderale(jd):
    """Il tempo siderale locale, in gradi."""
    return (280.46061837 + 360.98564736629 * (jd - 2451545.0) + LON) % 360


def in_cielo(ar_ore, dec, siderale):
    """Altezza e azimut (da nord verso est), in gradi, di un punto del cielo."""
    h = math.radians(siderale - ar_ore * 15)
    d, f = math.radians(dec), math.radians(LAT)
    alt = math.asin(math.sin(f) * math.sin(d) + math.cos(f) * math.cos(d) * math.cos(h))
    az = math.atan2(-math.cos(d) * math.sin(h), math.sin(d) * math.cos(f) - math.cos(d) * math.sin(f) * math.cos(h))
    return math.degrees(alt), math.degrees(az) % 360


def tramonto(giorno):
    """L'ora del tramonto (il lembo del sole all'orizzonte, con la rifrazione), come istante con il fuso di Roma."""
    mezzodi = datetime.datetime(giorno.year, giorno.month, giorno.day, 12, 0, tzinfo=datetime.timezone.utc)
    jd = giuliano(mezzodi)
    d = jd - 2451545.0
    sole, _, _, dec = sole_e_luna(jd)
    media = (280.460 + 0.9856474 * d) % 360
    eps = math.radians(23.439 - 0.0000004 * d)
    retta = math.degrees(math.atan2(math.cos(eps) * math.sin(math.radians(sole)), math.cos(math.radians(sole)))) % 360
    equazione = ((media - retta + 180) % 360 - 180) * 4                      # in minuti: il sole vero rispetto a quello medio
    f, de = math.radians(LAT), math.radians(dec)
    arco = math.degrees(math.acos((math.sin(math.radians(-0.833)) - math.sin(f) * math.sin(de)) / (math.cos(f) * math.cos(de))))
    return (mezzodi + datetime.timedelta(minutes=-LON * 4 - equazione + arco * 4)).astimezone(ROMA)


def a_notte_fatta(giorno):
    """L'ora della tavola: due ore dopo il tramonto, quando il cielo è buio in ogni stagione."""
    return tramonto(giorno) + datetime.timedelta(hours=2)


def precessa(ar, dec, anni):
    """Dalle coordinate J2000 (in gradi) a quelle dell'anno: la precessione, alla buona (basta al disegno)."""
    a, d = math.radians(ar), math.radians(dec)
    return ar + anni * (0.012812 + 0.005567 * math.sin(a) * math.tan(d)), dec + anni * 0.005567 * math.cos(a)


# I pianeti che si vedono a occhio nudo: gli elementi medi delle orbite (JPL, «Approximate Positions of the Planets»,
# validi dal 1800 al 2050) e quanto cambiano in un secolo. a, e, inclinazione, longitudine media, del perielio, del nodo.
ORBITE = {
    "terra": ((1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0), (0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0)),
    "Venere": ((0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255), (0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418)),
    "Marte": ((1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891), (0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343)),
    "Giove": ((5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909), (-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106)),
    "Saturno": ((9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448), (-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794)),
}
SPLENDORE = {"Venere": -4.4, "Marte": -1.52, "Giove": -9.4, "Saturno": -8.88}


def intorno_al_sole(nome, t):
    """Dove sta un pianeta intorno al sole (eclittica J2000, unità astronomiche)."""
    (a, e, i, lm, lp, ln) = (x + v * t for x, v in zip(*ORBITE[nome]))
    i, lp_, ln_ = math.radians(i), math.radians(lp), math.radians(ln)
    w = lp_ - ln_
    m = math.radians((lm - lp + 180) % 360 - 180)
    ecc = m
    for _ in range(12):
        ecc = ecc - (ecc - e * math.sin(ecc) - m) / (1 - e * math.cos(ecc))
    x, y = a * (math.cos(ecc) - e), a * math.sqrt(1 - e * e) * math.sin(ecc)
    cw, sw, cn, sn, ci, si = math.cos(w), math.sin(w), math.cos(ln_), math.sin(ln_), math.cos(i), math.sin(i)
    return ((cw * cn - sw * sn * ci) * x + (-sw * cn - cw * sn * ci) * y, (cw * sn + sw * cn * ci) * x + (-sw * sn + cw * cn * ci) * y, sw * si * x + cw * si * y)


def pianeta(nome, jd):
    """Ascensione retta e declinazione J2000 (gradi), longitudine eclittica vista dalla Terra, e grandezza."""
    t = (jd - 2451545.0) / 36525
    px, py, pz = intorno_al_sole(nome, t)
    tx, ty, tz = intorno_al_sole("terra", t)
    x, y, z = px - tx, py - ty, pz - tz
    eps = math.radians(23.43928)
    ye, ze = y * math.cos(eps) - z * math.sin(eps), y * math.sin(eps) + z * math.cos(eps)
    lontano_dal_sole, lontano_da_noi = math.sqrt(px * px + py * py + pz * pz), math.sqrt(x * x + y * y + z * z)
    grandezza = SPLENDORE[nome] + 5 * math.log10(lontano_dal_sole * lontano_da_noi)
    return math.degrees(math.atan2(ye, x)) % 360, math.degrees(math.atan2(ze, math.hypot(x, ye))), math.degrees(math.atan2(y, x)) % 360, grandezza


def galattiche(l, b):
    """Dalle coordinate galattiche a quelle equatoriali J2000, in gradi."""
    l, b = math.radians(l), math.radians(b)
    ag, dg, ln = math.radians(192.85948), math.radians(27.12825), math.radians(122.93192)
    dec = math.asin(math.sin(dg) * math.sin(b) + math.cos(dg) * math.cos(b) * math.cos(ln - l))
    ar = ag + math.atan2(math.cos(b) * math.sin(ln - l), math.cos(dg) * math.sin(b) - math.sin(dg) * math.cos(b) * math.cos(ln - l))
    return math.degrees(ar) % 360, math.degrees(dec)


# Lo sguardo: verso sud, alzato di 32 gradi, largo quasi 140 gradi sui 1440 del disegno e alto fin quasi allo
# zenit. L'orizzonte, a sud, cade a y = 790, dietro i monti quando la terra è scesa. È la proiezione stereografica
# delle carte del cielo: le figure tengono la loro forma anche ai bordi.
FUOCO, ALZO, CX = 520.0, math.radians(32), 720.0
CY = 790 - 2 * FUOCO * math.tan(ALZO / 2)


# Al telefono del disegno si vede solo la fascia di mezzo (circa 550 su 1440): lì il cielo è disegnato una seconda
# volta, più in piccolo, così in quella fascia entra tutto il sud, da sud-est a sud-ovest e fin oltre lo zenit.
FUOCO_STRETTO = 300.0


def sul_foglio(alt, az, fuoco=FUOCO):
    a, z = math.radians(alt), math.radians(az)
    est, nord, su = math.cos(a) * math.sin(z), math.cos(a) * math.cos(z), math.sin(a)
    avanti = -nord * math.cos(ALZO) + su * math.sin(ALZO)
    if avanti < -0.2:
        return None
    k = 2 * fuoco / (1 + avanti)
    return CX - k * est, 790 - 2 * fuoco * math.tan(ALZO / 2) - k * (nord * math.sin(ALZO) + su * math.cos(ALZO))


# ---------- Le stelle ----------
# Vengono dal Bright Star Catalogue (quinta edizione riveduta: Hoffleit e Warren, 1991; al CDS è il catalogo V/50).
# Il file intero (bsc5.dat.gz, 590 KB: al CDS di Strasburgo, o sul mirror del Telescope Data Center di Harvard,
# http://tdc-www.harvard.edu/catalogs/bsc5.dat.gz) non sta nel sito e serve una volta sola: si scarica in una cartella
# a parte e «tavola.py --estrai <file>» ne ricava stelle.tsv, con le sole stelle che si vedono a occhio nudo.

ESTRATTO = QUI / "stelle.tsv"


def estrai(catalogo):
    """Dal catalogo a stelle.tsv: chiave, ascensione retta e declinazione J2000 (gradi), grandezza, indice di colore
    B-V, altri nomi. Le componenti di una stessa stella doppia (più vicine di 0,02 gradi) diventano una stella sola,
    con la luce di tutte: a occhio nudo si vedono così."""
    import gzip
    righe = []
    for r in gzip.open(catalogo, "rt", encoding="latin-1"):
        if len(r) < 107 or not r[75:77].strip():
            continue
        bayer, indice, cost = r[7:10].strip().lower(), r[10:11].strip(), r[11:14].strip().lower()
        ar = (int(r[75:77]) + int(r[77:79]) / 60 + float(r[79:83]) / 3600) * 15
        dec = (int(r[84:86]) + int(r[86:88]) / 60 + int(r[88:90]) / 3600) * (-1 if r[83] == "-" else 1)
        colore = float(r[109:114]) if r[109:114].strip() else 0.5
        righe.append((float(r[102:107]), ar, dec, colore, f"{bayer}{indice} {cost}" if bayer else f"hr{int(r[0:4])}"))
    righe.sort()
    unite, griglia = [], {}
    for v, ar, dec, colore, chiave in righe:
        cella = (round(dec / 0.03), round(ar * math.cos(math.radians(dec)) / 0.03))
        vicina = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for i in griglia.get((cella[0] + dy, cella[1] + dx), ()):
                    u = unite[i]
                    if math.hypot((u[1] - ar) * math.cos(math.radians(dec)), u[2] - dec) < 0.02:
                        vicina = i
        if vicina is None:
            griglia.setdefault(cella, []).append(len(unite))
            unite.append([10 ** (-0.4 * v), ar, dec, colore, chiave, []])
        else:
            unite[vicina][0] += 10 ** (-0.4 * v)
            if chiave != unite[vicina][4]:
                unite[vicina][5].append(chiave)
    fuori = ["# Dal Bright Star Catalogue, 5th Revised Ed. (Hoffleit e Warren, 1991). chiave, AR e Dec J2000 in gradi, V, B-V, altri nomi"]
    for luce, ar, dec, colore, chiave, altri in unite:
        v = -2.5 * math.log10(luce)
        if v <= 5.2:
            fuori.append(f"{chiave}\t{ar:.4f}\t{dec:.4f}\t{v:.2f}\t{colore:.2f}\t{','.join(a for a in altri if not a.startswith('hr'))}")
    ESTRATTO.write_text("\n".join(fuori) + "\n", encoding="utf-8")
    print(f"stelle.tsv: {len(fuori) - 1} stelle fino alla grandezza 5,2, da {len(righe)} del catalogo")


def carica_stelle():
    stelle, nomi = {}, {}
    if not ESTRATTO.exists():
        sys.exit("manca _lavoro/disegni/stelle.tsv: si rifà con «tavola.py --estrai <bsc5.dat.gz>»")
    for riga in ESTRATTO.read_text(encoding="utf-8").splitlines():
        if riga.startswith("#"):
            continue
        chiave, ar, dec, v, colore, altri = (riga.split("\t") + [""])[:6]
        stelle[chiave] = (float(ar), float(dec), float(v), float(colore))
        for nome in [chiave] + [a for a in altri.split(",") if a]:
            nomi.setdefault(nome, chiave)
    return stelle, nomi


STELLE, NOMI = carica_stelle() if "--estrai" not in sys.argv else ({}, {})   # l'estratto si può rifare anche se manca


def trova(designazione):
    """La chiave di una stella dal suo nome di Bayer («alp ori», «gam leo»): quando le lettere sono numerate
    (gam1, gam2) e il numero non è detto, la più luminosa."""
    if designazione in NOMI:
        return NOMI[designazione]
    lettera, cost = designazione.split()
    simili = [NOMI[k] for k in NOMI if re.fullmatch(re.escape(lettera) + r"\d " + cost, k)]
    return min(simili, key=lambda k: STELLE[k][2]) if simili else None


# Le figure: il nome da scrivere, la sigla della costellazione, le linee (una stella di un'altra costellazione si
# scrive lettera_sigla). Le linee sono un disegno, come in tutte le carte: il cielo non ne ha.
DISEGNI = [
    ("Orione", "ori", ["alp gam del eps zet kap bet del", "alp zet", "alp lam gam", "alp mu xi", "gam pi3", "pi1 pi2 pi3 pi4 pi5 pi6"]),
    ("il Cane Maggiore", "cma", ["bet alp omi2 del eta", "del eps", "alp iot the gam iot"]),
    ("il Cane Minore", "cmi", ["alp bet"]),
    ("i Gemelli", "gem", ["alp tau eps mu eta", "bet ups del zet gam", "alp bet", "del lam xi", "eps nu", "tau the", "ups kap"]),
    ("il Toro", "tau", ["zet alp the2 gam del1 eps bet", "gam lam xi omi"]),
    ("l’Auriga", "aur", ["alp bet the bet_tau iot eta alp", "alp eps"]),
    ("il Leone", "leo", ["alp eta gam zet mu eps", "alp the bet del gam", "del the"]),
    ("il Cancro", "cnc", ["alp del gam iot", "del bet"]),
    ("la Vergine", "vir", ["bet eta gam del eps", "gam the alp", "del zet"]),
    ("Boote", "boo", ["eta alp eps del bet gam rho alp", "alp zet"]),
    ("la Corona Boreale", "crb", ["the bet alp gam del eps iot"]),
    ("Ercole", "her", ["gam bet zet eta pi eps zet", "eta sig tau", "pi rho the", "eps del lam mu", "del alp"]),
    ("Ofiuco", "oph", ["alp kap del eps zet eta bet alp", "eta xi the"]),
    ("il Serpente", "ser", ["kap gam bet del alp eps mu", "bet kap", "xi eta the"]),
    ("la Bilancia", "lib", ["alp2 bet gam alp2", "alp2 sig"]),
    ("lo Scorpione", "sco", ["nu bet del pi rho", "del sig alp tau eps mu1 zet2 eta the iot1 kap lam ups"]),
    ("il Sagittario", "sgr", ["gam2 del eps zet tau sig phi del lam phi zet", "gam2 eps", "lam mu", "sig omi pi"]),
    ("il Capricorno", "cap", ["alp2 bet psi ome zet eps del gam iot the alp2"]),
    ("l’Acquario", "aqr", ["eps bet alp gam zet eta", "alp pi zet", "alp the lam del"]),
    ("i Pesci", "psc", ["gam kap lam iot the gam", "iot ome del eps zet mu nu alp omi eta"]),
    ("la Balena", "cet", ["alp lam mu xi2 gam alp", "gam del omi zet the eta iot bet tau zet"]),
    ("l’Ariete", "ari", ["gam bet alp"]),
    ("il Triangolo", "tri", ["alp bet gam alp"]),
    ("Andromeda", "and", ["alp del bet gam", "bet mu nu"]),
    ("Pegaso", "peg", ["alp bet alp_and gam alp", "alp xi zet the eps", "bet mu lam iot kap", "bet eta pi"]),
    ("il Cigno", "cyg", ["alp gam eta bet", "zet eps gam del iot kap"]),
    ("la Lira", "lyr", ["alp zet bet gam del2 zet", "alp eps1"]),
    ("l’Aquila", "aql", ["gam alp bet", "alp del lam", "zet del eta the"]),
    ("il Delfino", "del", ["eps bet alp gam del bet"]),
    ("la Freccia", "sge", ["alp del bet", "del gam"]),
    ("l’Idra", "hya", ["del sig eta rho eps zet del", "zet the iot alp ups1 lam mu nu xi bet gam pi"]),
    ("il Corvo", "crv", ["alp eps gam del bet eps"]),
    ("la Coppa", "crt", ["alp bet gam del alp", "del eps", "gam zet"]),
    ("la Lepre", "lep", ["mu alp bet eps mu", "alp zet eta", "bet gam del"]),
    ("la Colomba", "col", ["eps alp bet gam", "bet eta"]),
    ("Eridano", "eri", ["bet ome mu nu omi1 gam pi del eps eta"]),
    ("la Poppa", "pup", ["xi rho zet sig pi nu"]),
    ("Perseo", "per", ["eta gam alp del eps xi zet", "alp bet rho"]),
    ("Cassiopea", "cas", ["bet alp gam del eps"]),
    ("l’Orsa Maggiore", "uma", ["eta zet eps del alp bet gam del"]),
    ("il Pesce Australe", "psa", ["alp eps the iot mu bet gam del alp"]),
]
# Le stelle che meritano il nome anche da sole, quando la loro figura non è scritta.
SOLE_ = {"alp psa": "Fomalhaut", "alp cma": "Sirio", "alp sco": "Antares", "alp boo": "Arturo", "alp vir": "Spiga", "alp tau": "Aldebaran",
         "eta tau": "le Pleiadi", "alp aql": "Altair", "alp cmi": "Procione", "alp leo": "Regolo", "alp lyr": "Vega", "alp aur": "Capella",
         "alp cyg": "Deneb", "alp gem": "Castore", "bet gem": "Polluce", "alp hya": "Alphard"}


def _risolvi():
    figure, mancano = [], []
    for titolo, cost, catene in DISEGNI:
        risolte = []
        for catena in catene:
            chiavi = []
            for pezzo in catena.split():
                lettera, sigla = pezzo.split("_") if "_" in pezzo else (pezzo, cost)
                chiave = trova(f"{lettera} {sigla}")
                if chiave is None:
                    mancano.append(f"{lettera} {sigla}")
                else:
                    chiavi.append(chiave)
            risolte.append(chiavi)
        figure.append((titolo, risolte))
    if mancano:
        print("stelle delle figure che non trovo nel catalogo:", ", ".join(mancano))
    return figure, {trova(k): v for k, v in SOLE_.items() if trova(k)}


FIGURE, SOLE = _risolvi() if STELLE else ([], {})
DELLE_FIGURE = {s for _, catene in FIGURE for catena in catene for s in catena}

# Ciò che in cielo non è una stella e si vede senza telescopio: tipo, nome, ascensione retta (ore), declinazione, raggio.
PROFONDI = [("rosa", "la nebulosa di Orione", 5 + 35.3 / 60, -5.38, 12), ("rosa", "la nebulosa Laguna", 18 + 3.7 / 60, -24.38, 10),
            ("blu", None, 3 + 47.4 / 60, 24.12, 17), ("ammasso", "il Presepe", 8 + 40.4 / 60, 19.67, 10),
            ("galassia", "la galassia di Andromeda", 42.7 / 60, 41.27, 0)]   # si vede solo nel cielo del telefono, che arriva oltre lo zenit


def splendore_via(l):
    """Quanto è luminosa la Via Lattea lungo il suo equatore: di più verso il centro (nel Sagittario) e nel Cigno."""
    d = min(l % 360, 360 - l % 360)
    return 0.22 + 0.78 * math.exp(-(d / 40) ** 2) + 0.2 * math.exp(-(((l % 360) - 76) / 24) ** 2)


def larga_via(l):
    d = min(l % 360, 360 - l % 360)
    return 6.5 + 6 * math.exp(-(d / 32) ** 2)


def luna_alta(jd):
    """L'altezza della luna sull'orizzonte, in gradi (serve solo a sapere se rischiara il cielo)."""
    t = (jd - 2451545.0) / 36525
    r, s = math.radians, math.sin
    lam = r(sole_e_luna(jd)[1])
    bet = r(5.13 * s(r(93.3 + 483202.02 * t)) + 0.28 * s(r(228.2 + 960400.89 * t)) - 0.28 * s(r(318.3 + 6003.15 * t)) - 0.17 * s(r(217.6 - 407332.21 * t)))
    eps = r(23.439)
    dec = math.asin(s(bet) * math.cos(eps) + math.cos(bet) * s(eps) * s(lam))
    ar = math.atan2(s(lam) * math.cos(eps) - math.tan(bet) * s(eps), math.cos(lam))
    return in_cielo(math.degrees(ar) / 15, math.degrees(dec), tempo_siderale(jd))[0]


def cielo_di_sera(giorno, stretto=False, lingua="it"):
    """Il cielo due ore dopo il tramonto, verso sud: le stelle, le figure, i pianeti, la Via Lattea, le nebulose, i nomi."""
    def dire(nome):
        return IN_INGLESE.get(nome, nome) if lingua == "en" else nome

    jd = giuliano(a_notte_fatta(giorno))
    fuoco = FUOCO_STRETTO if stretto else FUOCO
    sin_, des_ = (200, 1240) if stretto else (0, 1440)          # ciò che si disegna
    nomi_sin, nomi_des = (476, 964) if stretto else (0, 1440)   # dove un nome si legge per intero
    siderale = tempo_siderale(jd)
    anni = (jd - 2451545.0) / 365.25

    def vede(ar, dec, basso=1.5):
        """Dove cade sul foglio un punto del cielo (coordinate J2000, in gradi), o niente se è sotto l'orizzonte."""
        ar, dec = precessa(ar, dec, anni)
        alt, az = in_cielo(ar / 15, dec, siderale)
        return sul_foglio(alt, az, fuoco) if alt > basso else None

    def nel_foglio(q, margine=0):
        return q is not None and sin_ - margine <= q[0] <= des_ + margine and -margine <= q[1] <= 790

    def sotto_la_luna(q):
        return math.hypot(q[0] - (900 if stretto else 1290), q[1] - (90 if stretto else 200)) < 62

    # le stelle: tutte quelle del catalogo fino a una certa grandezza (al telefono un po' meno), più quelle delle figure
    posti = {}
    for chiave, (ar, dec, grandezza, colore) in STELLE.items():
        if grandezza > (4.1 if stretto else 4.7) and chiave not in DELLE_FIGURE:
            continue
        q = vede(ar, dec)
        if nel_foglio(q, 120) and not sotto_la_luna(q):
            posti[chiave] = (q[0], q[1], grandezza, colore)

    def dentro(nome):
        return nome in posti and nel_foglio(posti[nome])

    linee, nomi, scritte = [], [], set()
    for titolo, catene in FIGURE:
        sue = {s for catena in catene for s in catena}
        viste = [s for s in sue if dentro(s)]
        for catena in catene:
            for a, b in zip(catena, catena[1:]):
                if a in posti and b in posti and (dentro(a) or dentro(b)):
                    linee.append(f"M{round(posti[a][0])} {round(posti[a][1])}L{round(posti[b][0])} {round(posti[b][1])}")
        if len(viste) >= max(2, math.ceil(len(sue) * 0.6)):
            xs, ys = [posti[s][0] for s in viste], [posti[s][1] for s in viste]
            mx = sum(xs) / len(xs)
            # il nome sta sotto la figura; se lì ci sono già i monti, o un altro nome, sopra o di lato
            sotto, sopra = (mx, max(ys) + 24), (mx, min(ys) - 14)
            lati = [(max(xs) + 14 + 4.2 * len(titolo), sum(ys) / len(ys)), (min(xs) - 14 - 4.2 * len(titolo), sum(ys) / len(ys))]
            luce = sum(10 ** (-0.4 * posti[s][2]) for s in viste)
            titolo = dire(titolo)
            nomi.append(([sotto, sopra] + lati if max(ys) < 610 else [sopra] + lati + [sotto], titolo, 2 + min(40, luce * 14)))
            scritte |= sue
    for s, titolo in SOLE.items():
        if dentro(s) and s not in scritte:
            nomi.append(([(posti[s][0], posti[s][1] - 13), (posti[s][0], posti[s][1] + 24)], dire(titolo), 18 if titolo == "le Pleiadi" else 1))

    # i pianeti: fermi come le stelle, ma ogni sera un po' più in là
    pianeti = []
    for nome in ("Venere", "Marte", "Giove", "Saturno"):
        ar, dec, _, grandezza = pianeta(nome, jd)
        q = vede(ar, dec, basso=3)
        if nel_foglio(q):
            pianeti.append((q[0], q[1], grandezza, nome))
            nomi.append(([(q[0], q[1] - 15), (q[0], q[1] + 26)], dire(nome), 50))

    # la Via Lattea: una fila di chiarori lungo il suo equatore, e la sua polvere di stelle. La luna la spegne.
    vista_luna = (1 - math.cos(math.radians(sole_e_luna(jd)[2]))) / 2
    buio = 1 - 0.8 * vista_luna if luna_alta(jd) > 0 else 1.0
    via, migliore = [], None
    for l in range(0, 360, 6):
        centro, bordo = vede(*galattiche(l, 0), basso=-4), vede(*galattiche(l, larga_via(l)), basso=-30)
        if centro and bordo and nel_foglio(centro, 160):
            raggio = math.hypot(centro[0] - bordo[0], centro[1] - bordo[1]) * 1.15
            via.append((centro[0], centro[1], raggio * 1.12, 0.12 * splendore_via(l) * buio))
            if nomi_sin + 90 < centro[0] < nomi_des - 90 and 170 < centro[1] < 560 and (migliore is None or splendore_via(l) > migliore[2]):
                migliore = (centro[0], centro[1], splendore_via(l))
    if migliore and buio > 0.45 and migliore[2] > 0.3:
        nomi.append(([(migliore[0], migliore[1]), (migliore[0], migliore[1] - 60), (migliore[0], migliore[1] + 60)], dire("la Via Lattea"), 15))
    r = random.Random(4242)   # sempre la stessa polvere: è attaccata al cielo e gira con lui
    polvere = []
    for _ in range(900):
        l = r.uniform(0, 360)
        if r.random() < splendore_via(l) / 1.25:
            q = vede(*galattiche(l, r.gauss(0, larga_via(l) / 2.3)), basso=2)
            if nel_foglio(q):
                polvere.append(q)

    profondi = []
    for tipo, titolo, ore, dec, raggio in PROFONDI:
        q = vede(ore * 15, dec, basso=4)
        if nel_foglio(q):
            gira = 0.0
            if tipo == "galassia":
                # l'asse lungo della galassia punta a nord-est (35 gradi dal nord): due punti lungo l'asse danno
                # la sua lunghezza e la sua inclinazione sul foglio
                a, b = vede(ore * 15 + 1.1 / math.cos(math.radians(dec)), dec + 1.55, basso=-90), vede(ore * 15 - 1.1 / math.cos(math.radians(dec)), dec - 1.55, basso=-90)
                raggio, gira = math.hypot(a[0] - b[0], a[1] - b[1]) / 2, math.degrees(math.atan2(a[1] - b[1], a[0] - b[0]))
            profondi.append((tipo, q[0], q[1], raggio, gira))
            if titolo:
                titolo = dire(titolo)
                nomi.append(([(q[0] + raggio + 6 + 4.2 * len(titolo), q[1] + 5), (q[0] - raggio - 6 - 4.2 * len(titolo), q[1] + 5), (q[0], q[1] - raggio - 7), (q[0], q[1] + raggio + 16)], titolo, 20))

    # due nomi non devono cadere uno sull'altro: per ognuno, il primo dei suoi posti che è libero e sta nel foglio
    messi = []
    for scelte, titolo, peso in sorted(nomi, key=lambda q: -q[2]):
        largo = 4.3 * len(titolo) + 8
        # prima si cerca un posto libero che non copra stelle; nebulose e Via Lattea, se non c'è, si accontentano
        for esigente in (True, False):
            if not esigente and peso not in (50, 20, 18, 15):
                break
            for x, y in scelte:
                libero = all(abs(x - mx) > largo + 4.3 * len(mt) + 8 or abs(y - my) > 27 for mx, my, mt, _ in messi)
                pulito = all(abs(x - sx) > largo or abs(y - 5 - sy) > 11 for sx, sy, g, _ in posti.values() if g < 3.7)
                if libero and (pulito or not esigente) and nomi_sin + largo < x < nomi_des - largo and 30 < y < 700:
                    messi.append((x, y, titolo, peso))
                    break
            else:
                continue
            break
    return {"stelle": {k: v for k, v in posti.items() if nel_foglio(v, 6)}, "linee": linee, "nomi": messi[:8 if stretto else 10], "pianeti": pianeti,
            "via": via, "polvere": polvere, "profondi": profondi, "buio": buio}


# ---------- La luna e la stagione ----------

def fase(giorno):
    """La luna di quella sera: quanta se ne vede (da 0 a 1), se cresce, e come si chiama."""
    _, _, distanza, _ = sole_e_luna(giuliano(a_notte_fatta(giorno)))
    vista = (1 - math.cos(math.radians(distanza))) / 2
    if distanza < 12 or distanza > 348:
        nome = "nuova"
    elif distanza < 80 or 100 <= distanza < 168:
        nome = "crescente"
    elif distanza < 100:
        nome = "primo"
    elif distanza < 192:
        nome = "piena"
    elif distanza < 260 or distanza >= 280:
        nome = "calante"
    else:
        nome = "ultimo"
    return vista, distanza < 180, nome


# Le classi della stagione che in style.css cambiano dei colori; le altre dicono solo a questo script che cosa disegnare.
DI_COLORE = {"tv-primavera", "tv-estate", "tv-autunno", "tv-inverno", "tv-foglie", "tv-monti-neve", "tv-neve"}


def stagione(giorno):
    """La stagione e ciò che porta con sé: classi per style.css (DI_COLORE) e cose da disegnare."""
    g = (giorno.month, giorno.day)
    if (3, 20) <= g < (6, 21):
        classi = ["tv-primavera"]
    elif (6, 21) <= g < (9, 23):
        classi = ["tv-estate"]
    elif (9, 23) <= g < (12, 21):
        classi = ["tv-autunno"]
    else:
        classi = ["tv-inverno"]
    if (10, 10) <= g < (12, 8):
        classi.append("tv-foglie")       # il faggio arrossa
    if (10, 25) <= g < (12, 15):
        classi.append("tv-nebbia")       # la nebbia nelle valli
    if g >= (11, 22) or g < (4, 8):
        classi.append("tv-monti-neve")   # la prima neve, sui monti
    if g >= (12, 15) or g < (3, 6):
        classi.append("tv-neve")         # la neve fino a casa
    if (4, 5) <= g < (6, 10):
        classi.append("tv-fiori")
    if (6, 1) <= g < (7, 12):
        classi.append("tv-lucciole")
    if (8, 9) <= g <= (8, 14):
        classi.append("tv-perseidi")     # le stelle cadenti d'agosto
    if (12, 12) <= g <= (12, 15):
        classi.append("tv-geminidi")     # e quelle di dicembre
    return classi


# ---------- Il disegno ----------

def luna_svg(vista, cresce, dove="translate(1290 200)"):
    r = 25
    if vista < 0.012:
        forma = ""
    elif vista > 0.988:
        forma = f'<circle class="volta-falce" r="{r}"/>'
    else:
        semi = n(r * abs(1 - 2 * vista))
        forma = f'<path class="volta-falce" d="M0 {-r}A{r} {r} 0 0 1 0 {r}A{semi} {r} 0 0 {0 if vista < 0.5 else 1} 0 {-r}Z"/>'
    gira = f"rotate({-24 if cresce else 24})" + ("" if cresce else " scale(-1 1)")
    return f'<g class="solo-notte" transform="{dove} {gira}"><circle class="tv-luna-ombra" r="{r}"/>{forma}</g>'


def disegna_cielo(giorno, stretto, lingua):
    """Il cielo di una sera, per il computer o (stretto) per il telefono, dove i punti sono un po' più grandi.
    In due gruppi: il primo si vede con le parole del frontespizio; il secondo, tv-dopo (ciò che cadrebbe sulle parole, le linee
    delle figure, i nomi) compare quando le parole se ne sono andate."""
    c = cielo_di_sera(giorno, stretto, lingua)
    ingrandisci = 1.3 if stretto else 1.0

    def dopo(x, y, margine=0):
        return any(x0 - margine <= x <= x1 + margine and y0 - margine <= y <= y1 + margine for x0, y0, x1, y1 in PAROLE[stretto])

    f = {False: [], True: []}
    f[False].append("".join(f'<circle cx="{round(x)}" cy="{round(y)}" r="{round(r)}" fill="url(#tv-g)" opacity="{op:.2f}"/>' for x, y, r, op in c["via"]))
    for quando in (False, True):
        punti = "".join(f"M{round(x)} {round(y)}h0" for x, y in c["polvere"][::2 if stretto else 1] if dopo(x, y) == quando)
        if punti:
            f[quando].append(f'<path class="tv-polvere" opacity="{0.35 + 0.65 * c["buio"]:.2f}" d="{punti}"/>')
    for tipo, x, y, r, gira in c["profondi"]:
        quando = dopo(x, y, r)
        if tipo == "ammasso":
            caso = random.Random(44)
            f[quando].append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="url(#tv-g)" opacity=".3"/><path class="tv-polvere" d="'
                             + "".join(f"M{n(x + caso.gauss(0, 3.6))} {n(y + caso.gauss(0, 3.6))}h0" for _ in range(9)) + '"/>')
        elif tipo == "galassia":
            f[quando].append("".join(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * k)}" ry="{n(r * k * 0.3)}" transform="rotate({n(gira)} {n(x)} {n(y)})" fill="url(#tv-g)" opacity="{op}"/>'
                                     for k, op in ((1, ".5"), (0.42, ".6"))))
        else:
            f[quando].append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="url(#tv-{"r" if tipo == "rosa" else "b"})" opacity=".8"/>')
    f[True].append(f'<path class="tv-linea" d="{"".join(c["linee"])}"/>')
    # le stelle: punti tondi (tratti lunghi niente), raccolti per misura e per colore, così ognuna costa pochi caratteri
    gruppi = {}
    for x, y, g, colore in c["stelle"].values():
        misura = 0 if g < 0.5 else 1 if g < 1.5 else 2 if g < 2.5 else 3 if g < 3.3 else 4 if g < 4.0 else 5
        tinta = " tv-calda" if colore >= 1.0 else " tv-fredda" if colore <= 0.02 else ""
        quando = dopo(x, y, 5 - misura)
        if g < 0.95:
            f[quando or dopo(x, y, 14)].append(f'<circle cx="{round(x)}" cy="{round(y)}" r="{n((3.5 - 0.8 * g) * 4.4 * ingrandisci)}" fill="url(#tv-g)" opacity=".3"/>')
        gruppi.setdefault((quando, misura, tinta), []).append(f"M{round(x)} {round(y)}h0")
    for (quando, misura, tinta), punti in sorted(gruppi.items()):
        f[quando].append(f'<path class="tv-s{misura}{tinta}" d="{"".join(punti)}"/>')
    for x, y, g, nome in c["pianeti"]:
        r = max(2.3, 3.6 - 0.75 * g) * ingrandisci
        f[dopo(x, y, r * 4)].append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 4)}" fill="url(#tv-g)" opacity=".34"/><circle class="tv-{nome.lower()}" cx="{n(x)}" cy="{n(y)}" r="{n(r)}"/>')
    f[True].append("".join(f'<text class="tv-nome{" tv-nome-pianeta" if peso == 50 else ""}" x="{n(x)}" y="{n(y)}">{t}</text>' for x, y, t, peso in c["nomi"]))
    if {"tv-perseidi", "tv-geminidi"} & set(stagione(giorno)):
        f[True].append('<path class="tv-cadente" d="M612 150l-74 58M846 338l-52 42M360 260l-40 30"/>')
    return f'<g>{"".join(f[False])}</g><g class="tv-dopo">{"".join(f[True])}</g>'


def volta(giorno, alone, quale=0, lingua="it"):
    """Il cielo della tavola. La prima scena lo disegna, in due misure; la seconda lo riprende tale e quale."""
    vista, cresce, _ = fase(giorno)
    declinazione = sole_e_luna(giuliano(datetime.datetime(giorno.year, giorno.month, giorno.day, 12, 0, tzinfo=ROMA)))[3]
    sole_y = 330 - (90 - LAT + declinazione - 27) / 47 * 180
    if quale == 0:
        sfumi = "".join(f'<radialGradient id="tv-{nome}"><stop offset="0" stop-color="{colore}" stop-opacity="{forza}"/><stop offset="1" stop-color="{colore}" stop-opacity="0"/></radialGradient>'
                        for nome, colore, forza in (("g", "#DCE6F6", 1), ("r", "#E98FB2", 0.9), ("b", "#8DB7F2", 0.8)))
        cielo = (f'<defs>{sfumi}</defs><g id="tv-cielo-largo" class="tv-largo">{disegna_cielo(giorno, False, lingua)}</g>'
                 f'<g id="tv-cielo-stretto" class="tv-stretto">{disegna_cielo(giorno, True, lingua)}</g>')
    else:
        cielo = '<use href="#tv-cielo-largo"/><use href="#tv-cielo-stretto"/>'
    rondini = ""
    if (3, 25) <= (giorno.month, giorno.day) <= (9, 20):
        caso = random.Random(giorno.toordinal())
        voli = []
        for _ in range(caso.randint(3, 6)):
            x, y, s = caso.uniform(96, 372), caso.uniform(236, 392), caso.uniform(0.8, 1.35)   # sotto la riga della data
            voli.append(f"M{n(x)} {n(y)}q{n(3.5 * s)} {n(-4.6 * s)} {n(7 * s)} {n(-0.6 * s)}q{n(3.8 * s)} {n(-4 * s)} {n(7.4 * s)} {n(0.8 * s)}")
        rondini = f'<path class="tv-rondini solo-giorno" d="{"".join(voli)}"/>'
    astro = (f'<circle cx="1300" cy="{n(sole_y)}" r="80" fill="url(#{alone})" class="solo-giorno"/><circle cx="1290" cy="200" r="80" fill="url(#{alone})" class="solo-notte"/>'
             f'<circle class="volta-sole solo-giorno" cx="1300" cy="{n(sole_y)}" r="18"/>' + luna_svg(vista, cresce))
    return f'<g class="volta"><g class="volta-stelle">{cielo}</g>{rondini}<g class="volta-astro">{astro}</g></g>'


def stagionali(giorno):
    """Ciò che la stagione aggiunge al paesaggio lontano: dietro il colle (la nebbia) e sopra il prato."""
    classi = stagione(giorno)
    r = random.Random(giorno.toordinal() + 7)
    dietro = sopra = ""
    if "tv-nebbia" in classi:
        dietro = '<path class="tv-velo" d="M-20 606Q250 574 566 600Q300 628 -20 634ZM890 600Q1170 566 1460 594V622Q1180 606 890 616ZM300 560Q520 544 760 556Q520 572 300 572Z"/>'
    if "tv-fiori" in classi:
        bianchi, gialli = [], []
        for _ in range(64):
            x = r.uniform(20, 1420)
            y = r.uniform(640, 880) if 500 < x < 960 else r.uniform(730, 890)
            (gialli if r.random() < 0.32 else bianchi).append(f"M{n(x)} {n(y)}h0")
        sopra = f'<path class="tv-fiore" d="{"".join(bianchi)}"/><path class="tv-fiore tv-fiore-giallo" d="{"".join(gialli)}"/>'
    if "tv-lucciole" in classi:
        sopra += '<path class="tv-lucciola" d="' + "".join(f"M{n(r.uniform(380, 1080))} {n(r.uniform(600, 860))}h0" for _ in range(16)) + '"/>'
    return dietro, sopra


def riga_della_data(giorno, lingua):
    """«Tavola dell’11 novembre 2026, con la luna crescente.»"""
    luna = CON_LA_LUNA[lingua][fase(giorno)[2]]
    mese = MESI[lingua][giorno.month - 1]
    if lingua == "en":
        return f"Plate for {giorno.day} {mese} {giorno.year}, {luna}."
    del_ = "dell’" if giorno.day in (1, 8, 11) else "del "
    return f"Tavola {del_}{'1º' if giorno.day == 1 else giorno.day} {mese} {giorno.year}, {luna}."


def tavola(pagina, giorno, lingua):
    """La home (il testo di index.html o di en/index.html) con la tavola di quel giorno."""
    conta = []

    def cambia(schema, nuovo, quante=1, flags=0):
        nonlocal pagina
        pagina, fatte = re.subn(schema, nuovo, pagina, count=quante, flags=flags)
        conta.append((schema[:40], fatte == quante))

    # il cielo: nel frontespizio lo si disegna, nella soglia lo si riprende
    copie = iter((0, 1))
    cambia(r'<g class="volta">.*?</g></g>', lambda m: volta(giorno, re.search(r'url\(#([a-z-]+)\)', m.group(0)).group(1), next(copie), lingua), 2, re.S)
    # anche la luna che si vede dalla finestra della bottega ha la fase di quella notte
    vista, cresce, _ = fase(giorno)
    cambia(r'<path class="fn-falce solo-notte"[^>]*/>', lambda m: luna_svg(vista, cresce, "translate(214 72) scale(0.56)"))
    cambia(r'<div class="frontespizio-parole">', lambda m: f'<p class="tv-tiratura">{riga_della_data(giorno, lingua)}</p>\n      ' + m.group(0))
    cambia(r'<main id="contenuto" class="pagina-casa">', f'<main id="contenuto" class="pagina-casa {" ".join(c for c in stagione(giorno) if c in DI_COLORE)}">')
    dietro, sopra = stagionali(giorno)
    cambia(r'<!-- colle:inizio -->(<path class="fr-collina"[^>]*/>)', lambda m: dietro + "<!-- colle:inizio -->" + m.group(1) + sopra)
    mancano = [schema for schema, fatto in conta if not fatto]
    if mancano:
        sys.exit(f"tavola.py: nella pagina ({lingua}) non trovo: {mancano}. La home è cambiata: va aggiornato tavola().")
    return pagina


def scrivi(da, a, giorno):
    """Legge le due home in «da» e scrive le loro tavole in «a» (la stessa cartella, per il sito già costruito)."""
    for nome, lingua in PAGINE.items():
        testo = tavola((da / nome).read_text(encoding="utf-8"), giorno, lingua)
        (a / nome).parent.mkdir(parents=True, exist_ok=True)
        (a / nome).write_text(testo, encoding="utf-8")
        print(f"{a / nome}: {len(testo.encode('utf-8')) / 1024:.0f} KB")


def racconta(giorno):
    c = cielo_di_sera(giorno)
    vista, cresce, _ = fase(giorno)
    luna = CON_LA_LUNA["it"][fase(giorno)[2]]
    return (f"{giorno.isoformat()}, cielo delle {a_notte_fatta(giorno):%H:%M}: {' '.join(stagione(giorno))}; {luna} ({vista:.0%}), cielo buio {c['buio']:.0%}; {len(c['stelle'])} stelle, "
            f"{len(c['polvere'])} di polvere, {len(c['via'])} chiarori; " + ", ".join(t for _, _, t, _ in c["nomi"]))


def verifica():
    """I conti rifatti su date note. Ritorna quanti non tornano."""
    utc = datetime.timezone.utc
    sbagliati = 0

    def prova(che_cosa, trovato, atteso, entro):
        nonlocal sbagliati
        bene = abs(trovato - atteso) <= entro
        sbagliati += not bene
        print(f"{'ok ' if bene else 'NO '} {che_cosa}: {trovato:.2f} (atteso {atteso:.2f}, entro {entro})")

    def distanza(a1, d1, a2, d2):
        a1, d1, a2, d2 = map(math.radians, (a1, d1, a2, d2))
        return math.degrees(math.acos(min(1, math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2))))

    d = sole_e_luna(giuliano(datetime.datetime(2024, 4, 8, 18, 21, tzinfo=utc)))[2]
    prova("eclissi di sole dell'8 aprile 2024, 18:21 UT: gradi fra luna e sole", min(d, 360 - d), 0, 0.5)
    prova("luna piena del 18 settembre 2024, 02:34 UT: gradi fra luna e sole", sole_e_luna(giuliano(datetime.datetime(2024, 9, 18, 2, 34, tzinfo=utc)))[2], 180, 0.5)
    prova("solstizio d'estate 2026: declinazione del sole", sole_e_luna(giuliano(datetime.datetime(2026, 6, 21, 12, 0, tzinfo=utc)))[3], 23.44, 0.02)
    prova("tempo siderale di Greenwich il 1º gennaio 2000 a mezzogiorno, in ore",
          (tempo_siderale(giuliano(datetime.datetime(2000, 1, 1, 12, 0, tzinfo=utc))) - LON) / 15, 18.6974, 0.001)
    for giorno, ora in ((datetime.date(2026, 6, 21), 20 + 24 / 60), (datetime.date(2026, 12, 21), 16 + 36 / 60)):
        t = tramonto(giorno)
        prova(f"tramonto del {giorno.day}/{giorno.month}, in ore", t.hour + t.minute / 60, ora, 0.15)
    jd = giuliano(datetime.datetime(2020, 12, 21, 18, 0, tzinfo=utc))
    g, s = pianeta("Giove", jd), pianeta("Saturno", jd)
    prova("grande congiunzione del 21 dicembre 2020: gradi fra Giove e Saturno", distanza(g[0], g[1], s[0], s[1]), 0.10, 0.1)
    prova("  e ascensione retta di Giove, in ore", g[0] / 15, 20.17, 0.05)
    for nome, quando in (("Marte", (2020, 10, 13, 23)), ("Giove", (2023, 11, 3, 5)), ("Saturno", (2024, 9, 8, 4))):
        jd = giuliano(datetime.datetime(*quando, tzinfo=utc))
        prova(f"opposizione di {nome} del {quando[2]}/{quando[1]}/{quando[0]}: gradi dal sole", (pianeta(nome, jd)[2] - sole_e_luna(jd)[0]) % 360, 180, 0.8)
    jd = giuliano(datetime.datetime(2022, 1, 9, 1, 0, tzinfo=utc))
    prova("congiunzione inferiore di Venere del 9 gennaio 2022: gradi dal sole", ((pianeta("Venere", jd)[2] - sole_e_luna(jd)[0] + 180) % 360) - 180, 0, 0.8)
    ar, dec = galattiche(0, 0)
    prova("centro della galassia: ascensione retta, in ore", ar / 15, 17.761, 0.005)
    prova("  e declinazione", dec, -28.94, 0.02)
    sirio = STELLE[trova("alp cma")]
    alt, az = in_cielo(sirio[0] / 15, sirio[1], sirio[0])
    prova("Sirio al meridiano: altezza", alt, 90 - LAT - 16.716, 0.01)
    prova("stelle nell'estratto del catalogo, in migliaia", len(STELLE) / 1000, 2.06, 0.1)
    return sbagliati


def main():
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    date = [a for a in argomenti if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)]
    giorno = datetime.date.fromisoformat(date[0]) if date else datetime.datetime.now(ROMA).date()
    altri = [a for a in argomenti if a not in date]
    if "--estrai" in sys.argv:
        if len(altri) != 1:
            sys.exit("tavola.py --estrai <bsc5.dat.gz>")
        return estrai(altri[0])
    if "--verifica" in sys.argv:
        return 1 if verifica() else 0
    if "--prova" in sys.argv:
        scrivi(SITO, SITO / "_lavoro" / "prove" / "tavola", giorno)
    elif len(altri) == 1:
        cartella = pathlib.Path(altri[0]).resolve()
        if (cartella / ".git").exists():
            sys.exit("tavola.py: questa è la cartella del sito in git, dove le pagine restano senza data. Per guardarla: --prova.")
        scrivi(cartella, cartella, giorno)
    else:
        print(__doc__)
        return 2
    print(racconta(giorno))
    return 0


if __name__ == "__main__":
    sys.exit(main())
