"""La tavola del giorno: la home che cambia con la data.

La mano e la coreografia della home restano quelle di casa.py e di style.css. Cambia ciò che la scena mostra:
- di sera, il cielo verso sud due ore dopo il tramonto, visto dal centro della Calabria: tutte le stelle che si
  vedono a occhio nudo, con il loro colore, le figure e i nomi delle costellazioni, i pianeti, la Via Lattea con la
  sua Grande Fenditura, due nebulose, due ammassi, una galassia, e la luna dove sta davvero quella sera, con la sua
  fase e la sua faccia (nella finestra della bottega resta il suo segno, con la fase di quella notte);
- di giorno, la luce di due ore dopo il mezzogiorno vero: la casa e gli alberi fanno ombra dalla parte opposta al
  sole, lunga quanto vuole la sua altezza; e quando le parole del frontespizio se ne vanno il foglio diventa una
  meridiana, con la strada che il sole fa quel giorno, le ore, le strade dei solstizi e degli equinozi, la luna se
  di giorno si vede, e il sole al suo posto. Finché ci sono le parole il sole sta in un angolo libero del foglio;
  da fine marzo a settembre ci sono le rondini. Di notte, con abbastanza luna, le ombre sono quelle della luna;
- sempre, i colori della stagione (classi tv- su <main>, in style.css): il faggio che arrossa, la nebbia di novembre,
  la neve, i fiori, le lucciole;
- in testa alla scena, la data della tavola: è un pulsante, e apre il lunario del giorno (il sole, la luna e le sue
  prossime sette sere, i pianeti, le stelle, le fonti), un foglio che si apre senza JavaScript (popover).
Nel browser non gira niente: tutto è calcolato qui e scritto nell'HTML.

Le pagine in git restano quelle di sempre, senza data: questo script non le tocca. Scrive la tavola in una copia del
sito già costruito, ed è il lavoro giornaliero (.github/workflows/tavola.yml), quando è acceso, a pubblicarla.

    python3 -I _lavoro/disegni/tavola.py <cartella> [AAAA-MM-GG]   la tavola nelle due home di <cartella>, e stagione
                                                                   e luna nelle due pagine dello studio
    python3 -I _lavoro/disegni/tavola.py --prova [AAAA-MM-GG]      la scrive in _lavoro/prove/tavola/, da guardare con
                                                                   servi.py (http://127.0.0.1:8765/_lavoro/prove/tavola/)
    python3 -I _lavoro/disegni/tavola.py --verifica                rifà i conti su date note (esce con 1 se non tornano)
    python3 -I _lavoro/disegni/tavola.py --uguali <a> <b>          esce con 0 se due pagine sono uguali a meno dei disegni
                                                                   del cielo e della luna (lo usa controlli/online.sh)
    python3 -I _lavoro/disegni/tavola.py --estrai <bsc5.dat.gz>    rifà stelle.tsv dal catalogo (serve una volta)

Che cosa è vero e che cosa no:
- le stelle: posizione, grandezza e colore vengono dal Bright Star Catalogue (vedi «Le stelle», più sotto); sono
  tutte quelle fino alla grandezza 6,1 (al telefono 5,4), più quelle delle figure: il cielo di un posto buio. Con
  la luna in cielo il limite scende, fino a una grandezza e mezza con la luna piena, come accade;
- le linee delle figure sono un disegno; i pianeti (Venere, Marte, Giove, Saturno) sono calcolati dalle orbite medie
  del JPL, entro mezzo grado;
- la Via Lattea sta dov'è davvero, e ha le sue forme note (le nubi di stelle del Sagittario, dello Scudo e del
  Cigno, la Grande Fenditura), ma quanto è chiara punto per punto è una stima a occhio mossa da una trama a caso, non
  una misura: è un disegno, e il lunario lo dice. Il suo chiarore è un'immagine PNG scritta dentro la pagina; con
  la luna in cielo si spegne;
- la luna sta dove sta in cielo (entro mezzo grado: formule a bassa precisione, con la parallasse), con la parte
  illuminata rivolta al sole e la faccia girata come quella sera (senza librazioni); è disegnata sette volte più
  grande del vero, e i suoi mari sono uno schizzo. Se a quell'ora è tramontata o è fuori dal foglio, nel cielo non
  c'è, e il lunario dice quando sorge o tramonta (ai cinque minuti);
- gli orari del sole nel lunario valgono per un orizzonte libero, entro un paio di minuti;
- la strada del sole e il suo posto sono calcolati (entro mezzo grado), con la stessa proiezione del cielo della
  notte ma in piccolo e più in alto sul foglio, perché ci stia la strada di ogni stagione; le ore sono quelle
  dell'orologio, con l'ora legale. Il sole dell'angolo, quello che si vede con le parole, è un segno: sale e scende
  con la stagione, ma non sta al suo posto vero;
- le ombre vanno dalla parte giusta e sono lunghe il giusto per l'altezza del sole (o della luna), viste di scorcio:
  ciò che viene verso chi guarda è accorciato di tre quarti (SCORCIO), a occhio. La casa fa ombra come una sagoma
  piatta, e i monti non ne fanno;
- il luogo è un punto convenzionale (39,3° N, 16,3° E), non la casa di nessuno;
- le date delle stagioni (quando nevica, quando il faggio arrossa) sono stimate, da correggere con chi ci vive.

Le stelle non cadono mai sulle parole del frontespizio (sembrerebbero punti o accenti): quelle che ci cadrebbero, le
linee e i nomi compaiono quando le parole se ne sono andate (.tv-dopo in style.css). Le righe delle parole le misura
strumenti/parole-fronte.mjs (parole-fronte.json), a una quarantina di misure di finestra e nelle due lingue; lo
stesso script, con --controlla, guarda nel browser che nessuna stella tocchi una parola. Dalle stesse righe viene il
posto del sole dell'angolo, di giorno (sole_dell_angolo).
"""
import base64
import datetime
import functools
import json
import math
import pathlib
import random
import re
import sys
import struct
import zlib
import zoneinfo

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
sys.dont_write_bytecode = True
LAT, LON = 39.3, 16.3
ROMA = zoneinfo.ZoneInfo("Europe/Rome")
MESI = {"it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
        "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}
# Le due home hanno la tavola intera. Le due pagine dello studio, dove la stessa casa si vede a metà strada, prendono
# la stessa stagione e la stessa luna, senza cielo vero e senza data.
PAGINE = {"index.html": "it", "en/index.html": "en"}
STUDIO = ["studio/index.html", "en/studio/index.html"]

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



def _parole():
    """Le righe delle parole del frontespizio nelle coordinate del disegno, misurate da strumenti/parole-fronte.mjs a
    tante misure di finestra e nelle due lingue. Il cielo stretto si vede nelle finestre più alte che larghe, quello
    largo nelle altre (style.css): a ognuno vanno le righe delle sue misure, tutte insieme, perché la pagina non sa
    su quale finestra verrà aperta."""
    righe = {}
    for lingua, misure in json.loads((QUI / "parole-fronte.json").read_text(encoding="utf-8"))["righe"].items():
        for misura, r in misure.items():
            larga, alta = (int(v) for v in misura.split("×"))
            righe.setdefault((larga <= alta, lingua), []).extend(tuple(q) for q in r)
    return righe


PAROLE = _parole()


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


def sole_del_giorno(giorno):
    """Quando il sole sorge e tramonta (il lembo all'orizzonte, con la rifrazione): due istanti con il fuso di Roma."""
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
    culmina = mezzodi + datetime.timedelta(minutes=-LON * 4 - equazione)
    return tuple((culmina + datetime.timedelta(minutes=verso * arco * 4)).astimezone(ROMA) for verso in (-1, 1))


def tramonto(giorno):
    return sole_del_giorno(giorno)[1]


def dove_sole(jd):
    """Ascensione retta e declinazione del sole alla data, in gradi."""
    lam, eps = math.radians(sole_e_luna(jd)[0]), math.radians(23.439 - 0.0000004 * (jd - 2451545.0))
    return math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360, math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def dove_luna(jd):
    """Ascensione retta e declinazione della luna alla data, in gradi, vista dal centro della Terra (formule a bassa
    precisione: entro mezzo grado)."""
    t = (jd - 2451545.0) / 36525
    r, s = math.radians, math.sin
    lam = r(sole_e_luna(jd)[1])
    bet = r(5.13 * s(r(93.3 + 483202.02 * t)) + 0.28 * s(r(228.2 + 960400.89 * t)) - 0.28 * s(r(318.3 + 6003.15 * t)) - 0.17 * s(r(217.6 - 407332.21 * t)))
    eps = r(23.439)
    dec = math.asin(s(bet) * math.cos(eps) + math.cos(bet) * s(eps) * s(lam))
    ar = math.atan2(s(lam) * math.cos(eps) - math.tan(bet) * s(eps), math.cos(lam))
    return math.degrees(ar) % 360, math.degrees(dec)


def luna_del_giorno(giorno):
    """Quando la luna sorge e quando tramonta fra il mezzogiorno di quel giorno e quello del giorno dopo: una lista di
    («sorge» o «tramonta», istante), in ordine. A passi di due minuti. Chi guarda dalla superficie vede la luna un
    grado più bassa che dal centro della Terra, e la rifrazione la rialza di mezzo: all'orizzonte il suo centro,
    visto dal centro della Terra, è alto un ottavo di grado."""
    inizio = datetime.datetime(giorno.year, giorno.month, giorno.day, 12, 0, tzinfo=ROMA)
    eventi, prima = [], None
    for passo in range(721):
        quando = inizio + datetime.timedelta(minutes=2 * passo)
        jd = giuliano(quando)
        ar, dec = dove_luna(jd)
        su = in_cielo(ar / 15, dec, tempo_siderale(jd))[0] > 0.125
        if prima is not None and su != prima:
            eventi.append(("sorge" if su else "tramonta", quando))
        prima = su
    return eventi


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


# In una finestra più alta che larga (un telefono, un tablet in piedi) del disegno si vede solo la fascia di mezzo
# (al telefono circa 550 su 1440): lì il cielo è disegnato una seconda volta, più in piccolo, così in quella fascia
# entra tutto il sud, da sud-est a sud-ovest e fin oltre lo zenit. Quale dei due si vede lo decide style.css.
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
        if v <= 6.5:
            fuori.append(f"{chiave}\t{ar:.4f}\t{dec:.4f}\t{v:.2f}\t{colore:.2f}\t{','.join(a for a in altri if not a.startswith('hr'))}")
    ESTRATTO.write_text("\n".join(fuori) + "\n", encoding="utf-8")
    print(f"stelle.tsv: {len(fuori) - 1} stelle fino alla grandezza 6,5, da {len(righe)} del catalogo")


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


# La Via Lattea della tavola è un disegno fatto con la testa, non una fotografia: una fascia lungo l'equatore della
# galassia, più chiara e più larga verso il centro (nel Sagittario), con le sue nubi di stelle più note e la Grande
# Fenditura, la striscia di polveri scure che dal Cigno al Sagittario la divide in due. Sta dov'è davvero nel cielo;
# quanto è chiara, punto per punto, è una stima a occhio, mossa da una trama a caso sempre uguale.
# Le nubi di stelle: longitudine e latitudine galattiche, quanto sono larghe nei due versi, quanto sono chiare.
NUBI = [(2, -3.5, 5.5, 3.2, 0.6),      # la grande nube del Sagittario
        (13, -0.6, 2.6, 1.8, 0.4),     # la piccola (M24)
        (27, -3, 5, 3, 0.5),           # la nube dello Scudo
        (44, -2.5, 9, 3.5, 0.22),      # l'Aquila
        (68, 1.8, 11, 3.6, 0.42),      # la nube del Cigno
        (108, 0, 16, 4, 0.14),         # Cefeo e Cassiopea
        (243, -3, 18, 5, 0.16),        # il Cane Maggiore e la Poppa
        (287, -1, 9, 4, 0.5)]          # la Carena, che dalla Calabria non si alza


# La Grande Fenditura: le polveri scure che dal Cigno al centro dividono la Via Lattea in due rami. Non è una riga:
# è una fila di nubi, una diversa dall'altra e ognuna messa di sbieco a modo suo, che si allarga verso Ofiuco (dove
# vela il ramo di ponente) e sale fino alle nubi scure sopra Antares. Longitudine, latitudine, quanto sono larghe
# nei due versi, di quanto sono girate, quanto sono fonde.
POLVERI = [(86, 2.0, 6, 2.0, 20, 0.7), (78, 0.5, 4, 1.4, -15, 0.6), (71, 3.0, 5, 1.8, 10, 0.75), (63, 1.5, 4.5, 1.5, 25, 0.6),
           (57, 4.5, 5, 2.2, -10, 0.85), (50, 2.0, 4, 1.4, 15, 0.7), (44, 5.5, 6, 2.6, 20, 0.9), (38, 2.5, 4, 1.8, -20, 0.8),
           (31, 6.0, 7, 3.0, 12, 0.9), (26, 2.2, 4, 1.6, 0, 0.75), (19, 5.5, 6, 3.2, -15, 0.9), (12, 3.0, 5, 2.0, 10, 0.85),
           (6, 6.5, 6, 3.4, 0, 0.8), (0, 3.5, 4.5, 2.0, -25, 0.8), (-5, 8.0, 6, 3.5, 30, 0.6), (-7, 15.0, 6, 4.5, 0, 0.5),
           (35, 10.0, 8, 2.5, 25, 0.5), (-13, 2.0, 5, 1.5, -10, 0.45), (-22, -1.0, 4, 1.2, 15, 0.35)]
POLVERI = [(l0, b0, dl, db, math.cos(math.radians(g)), math.sin(math.radians(g)), fonda) for l0, b0, dl, db, g, fonda in POLVERI]


def fenditura(l, b):
    """Quanta luce della Via Lattea lasciano passare le polveri della Grande Fenditura in un punto: 1 dove non ce ne
    sono. La trama sposta ogni punto di qualche grado, così i bordi delle nubi vengono frastagliati."""
    l = (l + 180) % 360 - 180
    if not -34 <= l <= 104 or not -8 < b < 28:
        return 1.0
    l, b = l + 6.0 * (trama(l * 2.3 + 60, b * 2.3 + 9) - 0.5), b + 4.4 * (trama(l * 2.9 + 17, b * 2.9 + 5) - 0.5)
    passa = 1.0
    for l0, b0, dl, db, coseno, seno, fonda in POLVERI:
        x, y = (l - l0) * coseno + (b - b0) * seno, (b - b0) * coseno - (l - l0) * seno
        passa *= 1 - fonda * math.exp(-(x / dl) ** 2 - (y / db) ** 2)
    return passa


def _trama():
    """Tre griglie di numeri a caso, a maglie di 8, 4 e 2 gradi: sommate, danno alla Via Lattea le sue macchie."""
    caso = random.Random(1610)
    return [(passo, peso, round(360 / passo), [[caso.random() for _ in range(round(360 / passo))] for _ in range(round(64 / passo) + 2)])
            for passo, peso in ((8.0, 0.5), (4.0, 0.3), (2.0, 0.2))]


TRAMA = _trama()


def trama(l, b):
    """Un numero fra 0 e 1 che cambia con dolcezza da un punto all'altro (e si richiude, nei due versi)."""
    v = 0.0
    for passo, peso, quante, griglia in TRAMA:
        x, y = (l % 360) / passo, ((b + 32) / passo) % len(griglia)
        i, j = int(x), int(y)
        fx, fy = x - i, y - j
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        sopra, sotto = griglia[j], griglia[(j + 1) % len(griglia)]
        a, c, d, e = sopra[i % quante], sopra[(i + 1) % quante], sotto[i % quante], sotto[(i + 1) % quante]
        v += peso * ((a + (c - a) * fx) * (1 - fy) + (d + (e - d) * fx) * fy)
    return v


def luce_via(l, b):
    """Quanto è chiara la Via Lattea in un punto (longitudine e latitudine galattiche), e quanta di quella luce è la
    luce calda del centro: due numeri, il primo da 0 a 2 circa, il secondo da 0 a 1."""
    l %= 360
    d = min(l, 360 - l)
    larga = (5.0 + 5.0 * math.exp(-(d / 38) ** 2)) * (0.72 + 0.56 * trama(l * 0.6 + 300, 25))     # una fascia che si stringe e si allarga
    disco = (0.2 + 0.5 * math.exp(-(d / 60) ** 2)) * math.exp(-((b + 0.6 - 2.2 * (trama(l * 0.8 + 150, -20) - 0.5)) / larga) ** 2)
    centro = 0.8 * math.exp(-(d / 13) ** 2 - ((b + 0.5) / 8.5) ** 2)
    nubi = sum(forza * math.exp(-(((l - l0 + 180) % 360 - 180) / dl) ** 2 - ((b - b0) / db) ** 2) for l0, b0, dl, db, forza in NUBI)
    # le macchie: la trama schiarisce e scurisce a chiazze, e dove una seconda trama sale troppo passa una nube scura
    macchie = 0.3 + 1.4 * trama(l, b)
    scure = max(0.0, min(1.0, (trama(l * 1.9 + 77, b * 1.9) - 0.5) / 0.3))
    scure = 1 - 0.5 * scure * scure * (3 - 2 * scure) * math.exp(-(b / 7) ** 2)
    luce = (disco + centro + nubi) * fenditura(l, b) * macchie * scure
    return luce, centro / (disco + centro + nubi + 1e-9)


@functools.lru_cache(maxsize=None)
def via_lattea():
    """Il disegno intero della Via Lattea, calcolato una volta: una tabella a passi di mezzo grado, da 30 gradi sotto
    a 30 sopra il suo equatore."""
    return [[luce_via(i / 2, j / 2 - 30) for i in range(721)] for j in range(121)]


def della_via(l, b):
    """La luce e il calore della Via Lattea in un punto, letti dalla tabella (fra le sue caselle, a metà strada)."""
    if not -30 < b < 30:
        return 0.0, 0.0
    tabella = via_lattea()
    x, y = (l % 360) * 2, (b + 30) * 2
    i, j = int(x), int(y)
    fx, fy = x - i, y - j
    a, c, d, e = tabella[j][i], tabella[j][i + 1], tabella[j + 1][i], tabella[j + 1][i + 1]
    return tuple((a[k] + (c[k] - a[k]) * fx) * (1 - fy) + (d[k] + (e[k] - d[k]) * fx) * fy for k in (0, 1))


def in_galattiche(ar, dec):
    """Dalle coordinate equatoriali J2000 a quelle galattiche, in gradi."""
    a, d = math.radians(ar), math.radians(dec)
    ag, dg, ln = math.radians(192.85948), math.radians(27.12825), math.radians(122.93192)
    b = math.asin(math.sin(d) * math.sin(dg) + math.cos(d) * math.cos(dg) * math.cos(a - ag))
    l = ln - math.atan2(math.cos(d) * math.sin(a - ag), math.sin(d) * math.cos(dg) - math.cos(d) * math.sin(dg) * math.cos(a - ag))
    return math.degrees(l) % 360, math.degrees(b)


def dal_cielo(alt, az, siderale):
    """Il contrario di in_cielo: ascensione retta e declinazione (alla data, in gradi) di un punto del cielo."""
    a, z, f = math.radians(alt), math.radians(az), math.radians(LAT)
    dec = math.asin(math.sin(f) * math.sin(a) + math.cos(f) * math.cos(a) * math.cos(z))
    h = math.atan2(-math.sin(z) * math.cos(a), math.sin(a) * math.cos(f) - math.cos(a) * math.sin(f) * math.cos(z))
    return (siderale - math.degrees(h)) % 360, math.degrees(dec)


def png(larga, alta, punti):
    """Un'immagine PNG a colori con la trasparenza, dai suoi punti (quattro byte l'uno, riga per riga)."""
    def pezzo(tipo, dati):
        return struct.pack(">I", len(dati)) + tipo + dati + struct.pack(">I", zlib.crc32(tipo + dati))
    righe, prima = [], bytes(larga * 4)
    for y in range(alta):
        riga = punti[y * larga * 4:(y + 1) * larga * 4]
        righe.append(b"\x02" + bytes((a - b) & 255 for a, b in zip(riga, prima)))     # ogni riga come differenza da quella sopra
        prima = riga
    return (b"\x89PNG\r\n\x1a\n" + pezzo(b"IHDR", struct.pack(">IIBBBBB", larga, alta, 8, 6, 0, 0, 0))
            + pezzo(b"IDAT", zlib.compress(b"".join(righe), 9)) + pezzo(b"IEND", b""))


@functools.lru_cache(maxsize=None)
def chiarore_della_via(giorno, stretto, buio):
    """Il chiarore della Via Lattea di quella sera, come immagine da stendere sul cielo: per ogni suo punto si risale
    dal foglio al cielo (il contrario di sul_foglio), poi alla galassia. Ritorna x, y, larghezza e altezza sul foglio
    e l'immagine, già scritta per stare dentro la pagina. Verso l'orizzonte sfuma, come fa nell'aria."""
    jd = giuliano(a_notte_fatta(giorno))
    siderale, anni = tempo_siderale(jd), (jd - 2451545.0) / 365.25
    fuoco = FUOCO_STRETTO if stretto else FUOCO
    x0, y0, larga, alta, passo = (160, -40, 280, 210, 4) if stretto else (-40, -40, 304, 168, 5)
    # Dal cielo di chi guarda (est, nord, su) alla galassia: è una rotazione, e la danno tre punti.
    assi = []
    for alt, az in ((0, 90), (0, 0), (90, 0)):
        ar, dec = dal_cielo(alt, az, siderale)
        a, d = math.radians(ar), math.radians(dec)
        ar, dec = ar - anni * (0.012812 + 0.005567 * math.sin(a) * math.tan(d)), dec - anni * 0.005567 * math.cos(a)   # precessa al contrario
        l, b = (math.radians(v) for v in in_galattiche(ar, dec))
        assi.append((math.cos(b) * math.cos(l), math.cos(b) * math.sin(l), math.sin(b)))
    (ex, ey, ez), (nx, ny, nz), (sx, sy, sz) = assi
    seno, coseno, alto = math.sin(ALZO), math.cos(ALZO), 790 - 2 * fuoco * math.tan(ALZO / 2)
    punti = bytearray(larga * alta * 4)
    for py in range(alta):
        yy = (alto - (y0 + (py + 0.5) * passo)) / (2 * fuoco)
        for px in range(larga):
            xx = (CX - (x0 + (px + 0.5) * passo)) / (2 * fuoco)
            avanti = (1 - xx * xx - yy * yy) / (1 + xx * xx + yy * yy)
            est, sopra = xx * (1 + avanti), yy * (1 + avanti)
            nord, su = -avanti * coseno + sopra * seno, avanti * seno + sopra * coseno
            if su <= 0.01:
                continue
            gz = est * ez + nord * nz + su * sz
            if abs(gz) > 0.49:
                continue
            luce, caldo = della_via(math.degrees(math.atan2(est * ey + nord * ny + su * sy, est * ex + nord * nx + su * sx)), math.degrees(math.asin(gz)))
            forza = (1 - math.exp(-1.25 * luce)) * 0.56 * buio * min(1.0, su / 0.2)
            i = (py * larga + px) * 4
            punti[i:i + 4] = (round(204 + 48 * caldo), round(220 + 8 * caldo), round(250 - 62 * caldo), round(255 * forza))
    return x0, y0, larga * passo, alta * passo, base64.b64encode(png(larga, alta, bytes(punti))).decode("ascii")


@functools.lru_cache(maxsize=None)
def cielo_di_sera(giorno, stretto=False, lingua="it"):
    """Il cielo due ore dopo il tramonto, verso sud: le stelle, le figure, i pianeti, la Via Lattea, le nebulose, i nomi."""
    def dire(nome):
        return IN_INGLESE.get(nome, nome) if lingua == "en" else nome

    jd = giuliano(a_notte_fatta(giorno))
    fuoco = FUOCO_STRETTO if stretto else FUOCO
    sin_, des_ = (200, 1240) if stretto else (0, 1440)          # ciò che si disegna
    # Dove un nome si legge per intero. Le stelle e i nomi stanno fermi mentre ci si avvicina alla casa (tv-ferme in
    # style.css), quindi conta solo la parte del cielo che si vede: nel cielo stretto la fascia del telefono più
    # alto (STRISCE in casa.py), in quello largo quasi tutto. I nomi vicini ai bordi del cielo largo hanno una classe
    # in più (tv-bordo) e spariscono nelle finestre poco più larghe che alte, dove cadrebbero fuori.
    nomi_sin, nomi_des = (505, 935) if stretto else (60, 1390)
    lettera = 5.5 if stretto else 4.3                           # quanto è larga, in media, una lettera di un nome
    siderale = tempo_siderale(jd)
    anni = (jd - 2451545.0) / 365.25

    def vede(ar, dec, basso=1.5):
        """Dove cade sul foglio un punto del cielo (coordinate J2000, in gradi), o niente se è sotto l'orizzonte."""
        ar, dec = precessa(ar, dec, anni)
        alt, az = in_cielo(ar / 15, dec, siderale)
        return sul_foglio(alt, az, fuoco) if alt > basso else None

    def versore(ar, dec):
        return (math.cos(math.radians(dec)) * math.cos(math.radians(ar)), math.cos(math.radians(dec)) * math.sin(math.radians(ar)), math.sin(math.radians(dec)))

    # La luna, dove sta davvero quella sera (se è nel cielo della tavola), con la parte illuminata rivolta al sole: un
    # punto poco più in là, lungo l'arco che va dalla luna al sole, dice da che parte sta la luce sul foglio.
    vista_luna = (1 - math.cos(math.radians(sole_e_luna(jd)[2]))) / 2
    luna_ar, luna_dec = dove_luna(jd)
    luna_alt, luna_az = in_cielo(luna_ar / 15, luna_dec, siderale)
    scende = 0.95 * math.cos(math.radians(luna_alt))            # dal centro della Terra alla superficie
    raggio_luna = 13.0 if stretto else 17.0
    luna = None
    q = sul_foglio(luna_alt - scende, luna_az, fuoco) if luna_alt - scende > 2 else None
    if q is not None and sin_ + raggio_luna <= q[0] <= des_ - raggio_luna and raggio_luna <= q[1] <= 780:
        m, s = versore(luna_ar, luna_dec), versore(*dove_sole(jd))
        prodotto = sum(a * b for a, b in zip(m, s))
        verso = [b - prodotto * a for a, b in zip(m, s)]
        lungo = math.sqrt(sum(v * v for v in verso)) or 1.0
        passo = math.radians(3)
        oltre = [a * math.cos(passo) + v / lungo * math.sin(passo) for a, v in zip(m, verso)]
        alt2, az2 = in_cielo(math.degrees(math.atan2(oltre[1], oltre[0])) / 15, math.degrees(math.asin(max(-1.0, min(1.0, oltre[2])))), siderale)
        q2 = sul_foglio(alt2 - scende, az2, fuoco)
        alt3, az3 = in_cielo(luna_ar / 15, luna_dec + 3, siderale)     # e un punto poco più a nord: da che parte è girata la sua faccia
        q3 = sul_foglio(alt3 - scende, az3, fuoco)
        if q2 is not None and q3 is not None:
            luna = (q[0], q[1], raggio_luna, vista_luna, math.degrees(math.atan2(q2[1] - q[1], q2[0] - q[0])),
                    math.degrees(math.atan2(q3[1] - q[1], q3[0] - q[0])) + 90)
    # Quando la luna è in cielo, le stelle più deboli e la Via Lattea non si vedono più: di più quanto più è piena.
    chiarore = vista_luna if luna_alt > 0 else 0.0
    buio = 1 - 0.8 * chiarore
    limite = (5.4 if stretto else 6.1) - 1.5 * chiarore

    def nel_foglio(q, margine=0):
        return q is not None and sin_ - margine <= q[0] <= des_ + margine and -margine <= q[1] <= 790

    def sotto_la_luna(q):
        return luna is not None and math.hypot(q[0] - luna[0], q[1] - luna[1]) < raggio_luna * 1.3

    # le stelle: tutte quelle che quella sera si vedono a occhio nudo da un posto buio (nel cielo del telefono, più
    # fitto, un po' meno), più quelle delle figure
    posti = {}
    for chiave, (ar, dec, grandezza, colore) in STELLE.items():
        if grandezza > limite and chiave not in DELLE_FIGURE:
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
            # il nome sta sotto la figura; se la figura è bassa, o lì c'è un altro nome, sopra o di lato
            sotto, sopra = (mx, max(ys) + 24), (mx, min(ys) - 14)
            luce = sum(10 ** (-0.4 * posti[s][2]) for s in viste)
            titolo = dire(titolo)
            lati = [(max(xs) + 14 + lettera * len(titolo), sum(ys) / len(ys)), (min(xs) - 14 - lettera * len(titolo), sum(ys) / len(ys))]
            nomi.append(([sotto, sopra] + lati if max(ys) < 440 else [sopra] + lati + [sotto], titolo, 2 + min(40, luce * 14)))
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

    # La Via Lattea: il suo chiarore è un'immagine (chiarore_della_via); qui la sua polvere di stelle, più fitta dove
    # il disegno è più chiaro, e il posto del suo nome. La luna la spegne.
    migliore = None
    for l in range(0, 360, 4):
        centro = vede(*galattiche(l, -1), basso=-4)
        if centro and nomi_sin + 90 < centro[0] < nomi_des - 90 and 170 < centro[1] < 560 and (migliore is None or della_via(l, -1)[0] > migliore[2]):
            migliore = (centro[0], centro[1], della_via(l, -1)[0])
    if migliore and buio > 0.45 and migliore[2] > 0.3:
        nomi.append(([(migliore[0], migliore[1]), (migliore[0], migliore[1] - 60), (migliore[0], migliore[1] + 60)], dire("la Via Lattea"), 15))
    r = random.Random(4242)   # sempre la stessa polvere: è attaccata al cielo e gira con lui
    polvere, velo = [], []
    for _ in range(60000 if stretto else 110000):
        l, b = r.uniform(0, 360), r.uniform(-22, 22)
        if r.random() < (della_via(l, b)[0] / 1.7) ** 1.6:
            q = vede(*galattiche(l, b), basso=2)
            if nel_foglio(q):
                (polvere if r.random() < 0.55 else velo).append(q)

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
                nomi.append(([(q[0] + raggio + 6 + lettera * len(titolo), q[1] + 5), (q[0] - raggio - 6 - lettera * len(titolo), q[1] + 5), (q[0], q[1] - raggio - 7), (q[0], q[1] + raggio + 16)], titolo, 20))

    # due nomi non devono cadere uno sull'altro: per ognuno, il primo dei suoi posti che è libero e sta nel foglio
    messi = []
    for scelte, titolo, peso in sorted(nomi, key=lambda q: -q[2]):
        largo = lettera * len(titolo) + 8
        # prima si cerca un posto libero che non copra stelle; nebulose e Via Lattea, se non c'è, si accontentano
        for esigente in (True, False):
            if not esigente and peso not in (50, 20, 18, 15):
                break
            for x, y in scelte:
                libero = all(abs(x - mx) > largo + lettera * len(mt) + 8 or abs(y - my) > 27 for mx, my, mt, _ in messi)
                pulito = all(abs(x - sx) > largo or abs(y - 5 - sy) > 11 for sx, sy, g, _ in posti.values() if g < 3.7)
                # né sopra la casa: lì, avvicinandosi, gli abeti tagliano il cielo prima che i nomi se ne vadano. (Ai
                # lati i nomi bassi restano: sono quelli dello Scorpione e del Sagittario, e i monti che salgono li
                # coprono come coprono le loro stelle.)
                sulla_casa = y > 575 and x + largo > 590 and x - largo < 870
                if libero and (pulito or not esigente) and not sulla_casa and nomi_sin + largo < x < nomi_des - largo and 30 < y < 700:
                    messi.append((x, y, titolo, peso))
                    break
            else:
                continue
            break
    return {"stelle": {k: v for k, v in posti.items() if nel_foglio(v, 6)}, "linee": linee, "nomi": messi[:8 if stretto else 10], "pianeti": pianeti,
            "polvere": polvere, "velo": velo, "profondi": profondi, "buio": buio, "luna": luna,
            "pianeti_alti": [(nome, *in_cielo(pianeta(nome, jd)[0] / 15, pianeta(nome, jd)[1], siderale)) for nome in ("Venere", "Marte", "Giove", "Saturno")],
            "luna_alta": (luna_alt - scende, luna_az), "chiarore": chiarore}


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


# ---------- Il giorno: la strada del sole ----------
# Di giorno il foglio è una meridiana: la strada che il sole fa quel giorno nel cielo del sud, con le ore, e il sole
# dov'è due ore dopo il mezzogiorno vero (come di notte il cielo è quello di due ore dopo il tramonto). La proiezione
# e lo sguardo sono quelli della notte (a sud, alzato di 32 gradi), ma in piccolo e più in alto sul foglio: così ci
# sta la strada di ogni stagione, dal solstizio d'inverno a quello d'estate, sopra i monti e sopra la casa, che con
# il colmo del tetto (x = 730) segna il sud.
FUOCO_GIORNO, CX_GIORNO, ORIZZONTE_GIORNO = 285.0, 730.0, 628.0
DOPO_MEZZOGIORNO = datetime.timedelta(hours=2)


def mezzogiorno(giorno):
    """Il mezzogiorno vero: l'istante in cui il sole passa a sud, a metà fra l'alba e il tramonto."""
    sorge, tramonta = sole_del_giorno(giorno)
    return sorge + (tramonta - sorge) / 2


def di_giorno(giorno):
    """L'ora della tavola di giorno: due ore dopo il mezzogiorno vero, con il sole a sud-ovest e le ombre di traverso."""
    return mezzogiorno(giorno) + DOPO_MEZZOGIORNO


def sole_a(quando):
    """Altezza e azimut del sole in un istante."""
    jd = giuliano(quando)
    ar, dec = dove_sole(jd)
    return in_cielo(ar / 15, dec, tempo_siderale(jd))


def sul_foglio_di_giorno(alt, az):
    p = sul_foglio(alt, az, FUOCO_GIORNO)
    return p and (p[0] + CX_GIORNO - CX, p[1] + ORIZZONTE_GIORNO - 790)


def strada(altezze):
    """Una strada del sole sul foglio, da una lista di (altezza, azimut): sopra l'orizzonte e un bel pezzo sotto, dove
    la coprono i monti e il prato (così non resta mai sospesa a mezz'aria), finché sta davanti a chi guarda."""
    punti = []
    for alt, az in altezze:
        p = sul_foglio_di_giorno(alt, az) if alt > -34 else None
        if p and -200 < p[0] < 1640 and p[1] < 960:
            punti.append(p)
    return punti


def strada_di(declinazione):
    """La strada del sole in un giorno in cui ha quella declinazione: dieci minuti alla volta intorno al mezzogiorno."""
    return strada(in_cielo(0, declinazione, passo * 2.5) for passo in range(-72, 73))


def strada_del(giorno):
    """La strada del sole di quel giorno, da tre ore prima dell'alba a tre ore dopo il tramonto."""
    sorge, tramonta = sole_del_giorno(giorno)
    passi = int((tramonta - sorge).total_seconds() // 600) + 37
    return strada(sole_a(sorge + datetime.timedelta(minutes=10 * (k - 18))) for k in range(passi))


def luna_di_giorno(giorno):
    """La luna all'ora della tavola di giorno, se si vede: (x, y, quanta se ne vede, gradi verso il sole sul foglio),
    oppure None. Di giorno si distingue quando è abbastanza illuminata e lontana dal sole, e non troppo bassa."""
    quando = di_giorno(giorno)
    jd = giuliano(quando)
    distanza = sole_e_luna(jd)[2]
    vista = (1 - math.cos(math.radians(distanza))) / 2
    ar, dec = dove_luna(jd)
    alt, az = in_cielo(ar / 15, dec, tempo_siderale(jd))
    alt -= 0.95 * math.cos(math.radians(alt))          # dalla superficie la luna è un po' più bassa
    if vista < 0.12 or alt < 6:
        return None
    p, s = sul_foglio_di_giorno(alt, az), sul_foglio_di_giorno(*sole_a(quando))
    if not p or not 40 < p[0] < 1400:
        return None
    return p[0], p[1], vista, math.degrees(math.atan2(s[1] - p[1], s[0] - p[0])), alt, az


def disegna_giorno(giorno, alone, lingua):
    """La carta del giorno: le strade dei solstizi e degli equinozi (punteggiate), il meridiano, la strada di oggi con
    le ore, la luna se di giorno si vede, e il sole dov'è all'ora della tavola. Compare quando le parole del
    frontespizio se ne sono andate, come le figure delle costellazioni di notte."""
    it = lingua == "it"
    ora_tavola = di_giorno(giorno)
    sorge, tramonta = sole_del_giorno(giorno)
    oggi = sole_e_luna(giuliano(mezzogiorno(giorno)))[3]
    f, scritte = [], []

    def scritta(x, y, testo, gira=0, classe=""):
        ruota = f' transform="rotate({n(gira)} {n(x)} {n(y)})"' if abs(gira) > 0.5 else ""
        scritte.append(f'<text class="tv-nome tv-scritta{classe}" x="{n(x)}" y="{n(y)}"{ruota}>{testo}</text>')

    def linea(punti):
        return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in punti)

    # le strade degli altri giorni dell'anno; quella troppo vicina alla strada di oggi si salta
    for declinazione, nome in ((23.44, "21 giugno" if it else "21 June"), (0, "equinozi" if it else "equinoxes"), (-23.44, "21 dicembre" if it else "21 December")):
        if abs(declinazione - oggi) < 3.4:
            continue
        punti = strada_di(declinazione)
        f.append(f'<path class="tv-strada tv-strada-altra" d="{linea(punti)}"/>')
        # il nome lungo la strada, due ore prima del mezzogiorno: dal lato opposto alla strada di oggi
        (x0, y0), (x, y), (x1, y1) = (sul_foglio_di_giorno(*in_cielo(0, declinazione, h)) for h in (-34, -30, -26))
        scritta(x, y + (16 if declinazione < oggi else -7), nome, math.degrees(math.atan2(y1 - y0, x1 - x0)))
    # il meridiano: la riga del sud, dal colmo del tetto fin sopra il sole di giugno
    f.append(f'<path class="tv-strada tv-meridiano" d="M{n(CX_GIORNO)} 806V{n(sul_foglio_di_giorno(90 - LAT + 23.44, 180)[1] - 16)}"/>')
    # la strada di oggi
    f.append(f'<path class="tv-strada" d="{linea(strada_del(giorno))}"/>')
    # le ore dell'orologio lungo la strada: un grano per ogni ora, con il suo numero sopra (non dove sta il sole)
    grani = []
    sole_x, sole_y = sul_foglio_di_giorno(*sole_a(ora_tavola))
    ora = sorge.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    while ora < tramonta:
        alt, az = sole_a(ora)
        p = sul_foglio_di_giorno(alt, az)
        if alt > 3 and p and 60 < p[0] < 1380 and math.hypot(p[0] - sole_x, p[1] - sole_y) > 27:
            grani.append(f"M{n(p[0])} {n(p[1])}h0")
            scritta(p[0], p[1] - 10, str(ora.hour if it else (ora.hour - 1) % 12 + 1))
        ora += datetime.timedelta(hours=1)
    f.append(f'<path class="tv-ora" d="{"".join(grani)}"/>')
    # la luna, quando di giorno si vede: solo la parte illuminata, girata verso il sole
    luna = luna_di_giorno(giorno)
    if luna:
        x, y, vista, verso, _, _ = luna
        r = 11
        forma = (f'<circle class="tv-luna-giorno" cx="{n(x)}" cy="{n(y)}" r="{r}"/>' if vista > 0.988 else
                 f'<path class="tv-luna-giorno" transform="translate({n(x)} {n(y)}) rotate({n(verso)})" '
                 f'd="M0 {-r}A{r} {r} 0 0 1 0 {r}A{n(r * abs(1 - 2 * vista))} {r} 0 0 {0 if vista < 0.5 else 1} 0 {-r}Z"/>')
        f.append(forma)
        scritta(x, y + r + 17, "la luna" if it else "the moon")
    # il sole, con l'ora in cui è lì
    x, y = sole_x, sole_y
    f.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="62" fill="url(#{alone})"/><circle class="volta-sole" cx="{n(x)}" cy="{n(y)}" r="13"/>')
    minuti = ora_tavola.hour * 60 + ora_tavola.minute + round(ora_tavola.second / 60)
    h, m = divmod(minuti, 60)
    scritta(x, y + 33, f"{h}:{m:02d}" if it else f"{(h - 1) % 12 + 1}:{m:02d} {'am' if h < 12 else 'pm'}")
    return "".join(f) + "".join(scritte)


# ---------- Le ombre ----------
# La casa e gli alberi fanno ombra dalla parte opposta al sole dell'ora della tavola, lunga quanto vuole la sua
# altezza: corta e di fianco d'estate, lunga e verso chi guarda d'inverno. Di notte, se c'è abbastanza luna, l'ombra
# è quella della luna. Le sagome si leggono dalla scena della soglia così com'è nella pagina; la scena del
# frontespizio è la stessa in piccolo e riprende lo stesso disegno. Chi guarda sta a nord e guarda a sud: l'est è a
# sinistra, e ciò che viene verso nord scende nel foglio, accorciato perché il prato è visto di scorcio.
SCORCIO = 0.26


def punti_di(d):
    """I poligoni di un percorso fatto solo di M, L, H, V e Z, con coordinate assolute."""
    poligoni, x, y = [], 0.0, 0.0
    for comando, numeri in re.findall(r"([MLHVZ])([^MLHVZ]*)", d):
        v = [float(q) for q in re.findall(r"-?\d+(?:\.\d+)?", numeri)]
        if comando == "M":
            poligoni.append([])
        if comando in "ML":
            for k in range(0, len(v), 2):
                x, y = v[k], v[k + 1]
                poligoni[-1].append((x, y))
        elif comando in "HV":
            for q in v:
                x, y = (q, y) if comando == "H" else (x, q)
                poligoni[-1].append((x, y))
    return [p for p in poligoni if len(p) > 2]


def tondo(cx, cy, rx, ry, lati=28):
    return [(cx + rx * math.cos(2 * math.pi * k / lati), cy + ry * math.sin(2 * math.pi * k / lati)) for k in range(lati)]


def cose_in_piedi(pagina, spoglio=False):
    """Ciò che sta in piedi sul prato nella scena della soglia, come lista di (sagoma, y del piede); e come quella
    scena sta in piccolo nel frontespizio: (scala, spostamento in x, spostamento in y). Con la neve il faggio è
    spoglio, e della sua chioma resta solo il tronco."""
    lontana, scena = pagina.split('<div class="soglia">')[:2]

    def percorso(classe, dove=scena):
        return re.search(rf'<path class="{classe}"[^>]*? d="([^"]*)"', dove).group(1)

    def rettangolo(classe, dove=scena):
        x, y, larga, alta = (float(v) for v in re.search(rf'<rect class="{classe}" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', dove).groups())
        return x, y, x + larga, y + alta

    cose = []
    # la casa: la facciata con il tetto e il camino, tutta d'un pezzo
    (sx, sy), (cx, cy), (dx, dy) = punti_di(percorso("cs-tetto"))[0]
    muro, pietra, camino, cima = rettangolo("cs-muro"), rettangolo("cs-pietra"), rettangolo("cs-camino"), rettangolo("cs-camino-cima")
    falda = lambda x: sy + (cy - sy) * (x - sx) / (cx - sx)        # l'altezza del tetto, sulla falda di sinistra
    piede = pietra[3]
    cose.append(([(pietra[0], piede), (pietra[0], pietra[1]), (muro[0], pietra[1]), (muro[0], sy), (sx, sy), (camino[0], falda(camino[0])), (camino[0], cima[3]),
                  (cima[0], cima[3]), (cima[0], cima[1]), (cima[2], cima[1]), (cima[2], cima[3]), (camino[2], cima[3]), (camino[2], falda(camino[2])), (cx, cy), (dx, dy),
                  (muro[2], dy), (muro[2], pietra[1]), (pietra[2], pietra[1]), (pietra[2], piede)], piede))
    # gli alberi: ogni chioma ha il piede in fondo al suo tronco; i tronchi nascosti dietro la casa arrivano a terra dietro il muro
    tronchi = []
    for q in punti_di(percorso("cs-tronco")):
        x0, x1, y0, y1 = min(x for x, _ in q), max(x for x, _ in q), min(y for _, y in q), max(y for _, y in q)
        tronchi.append([x0, y0, x1, muro[3] + 2 if y1 < muro[3] - 60 and sx < (x0 + x1) / 2 < dx else y1, False])
    for classe in ("cs-abete", "cs-abete-lontano"):
        for sagoma in punti_di(percorso(classe)):
            punta = min(sagoma, key=lambda p: p[1])[0]
            tronco = min(tronchi, key=lambda t: abs((t[0] + t[2]) / 2 - punta))
            tronco[4] = True
            cose.append((sagoma, tronco[3]))
    for classe in ("cs-pino",) if spoglio else ("cs-faggio", "cs-pino"):
        for x, y, rx, ry, largo in re.findall(r"M(-?[\d.]+) (-?[\d.]+)a([\d.]+) ([\d.]+) 0 1 0 (-?[\d.]+) 0", percorso(classe)):
            x, y, rx, ry, largo = float(x), float(y), float(rx), float(ry), float(largo)
            centro = x + largo / 2
            liberi = [t for t in tronchi if not t[4] and centro - rx < (t[0] + t[2]) / 2 < centro + rx] or tronchi
            cose.append((tondo(centro, y, rx, ry), min(liberi, key=lambda t: abs((t[0] + t[2]) / 2 - centro))[3]))
    cose += [([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], y1) for x0, y0, x1, y1, _ in tronchi]
    # la legnaia, il ceppo e i cespugli
    legnaia = punti_di(percorso("cs-legna-fondo"))[0]
    cose.append((legnaia, max(y for _, y in legnaia)))
    x0, y0, x1, y1 = rettangolo("cs-ceppo")
    cose.append(([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], y1))
    for x, y, r in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/>', re.search(r'<g class="cs-cespugli">(.*?)</g>', scena, re.S).group(1)):
        cose.append((tondo(float(x), float(y), float(r), float(r)), float(y) + 0.85 * float(r)))
    # la stessa scena, in piccolo, nel frontespizio: lo dice il muro della casa
    piccolo = rettangolo("cs-muro", lontana)
    scala = (piccolo[2] - piccolo[0]) / (muro[2] - muro[0])
    return cose, (scala, piccolo[0] - scala * muro[0], piccolo[1] - scala * muro[1])


def coricata(alt, az):
    """Di quanto si sposta sul foglio, in orizzontale e in verticale, l'ombra di un punto alto uno, con la luce a
    quell'altezza e a quell'azimut. Con la luce alle spalle di chi guarda le ombre andrebbero verso i monti: None."""
    lunga = min(1 / math.tan(math.radians(alt)), 3.0)
    kx, ky = math.sin(math.radians(az)) * lunga, -math.cos(math.radians(az)) * lunga * SCORCIO
    return (kx, ky) if ky >= 0 else None


def ombra(cose, verso, cifre=0):
    """Le ombre di quelle cose, in un solo percorso: ogni sagoma coricata sul prato intorno al suo piede. I pezzi
    girano tutti nello stesso verso, così dove si sovrappongono fanno un'ombra sola e non un buco."""
    kx, ky = verso
    pezzi = []
    for sagoma, piede in cose:
        q = [(x + kx * (piede - y), piede + ky * (piede - y)) for x, y in sagoma]
        if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(q, q[1:] + q[:1])) < 0:
            q.reverse()
        pezzi.append("M" + "L".join(f"{round(x, cifre):g} {round(y, cifre):g}" for x, y in q) + "Z")
    return "".join(pezzi)


# Gli alberi dei boschi lontani, alla buona, alti 100 con il piede in (0, 0): l'abete, il faggio, il pino.
ALBERI = {"ab": [[(-25, 0), (0, -100), (25, 0)]],
          "fg": [tondo(0, -60, 34, 34, 10), [(-4, 0), (-4, -40), (4, -40), (4, 0)]],
          "pn": [tondo(0, -78, 34, 13, 10), [(-3, 0), (-3, -70), (3, -70), (3, 0)]]}


def ombra_del_bosco(bosco, verso):
    """Le ombre degli alberi di un bosco lontano (un gruppo di <use> con il posto e la misura di ogni albero)."""
    cose = []
    for tipo, x, y, scala in re.findall(r'<use href="#[a-z]+-(ab|fg|pn)" transform="translate\((-?[\d.]+) (-?[\d.]+)\) scale\(([\d.]+)\)"/>', bosco):
        x, y, scala = float(x), float(y), float(scala)
        cose += [([(x + scala * a, y + scala * b) for a, b in sagoma], y) for sagoma in ALBERI[tipo]]
    return ombra(cose, verso, 1)


def luci(giorno):
    """Le luci che fanno ombra quel giorno: il sole dell'ora della tavola e, di notte, la luna, se è alta e ce n'è
    abbastanza. Una lista di (nome, classe di style.css che dice quando si vede, spostamento dell'ombra)."""
    sera = cielo_di_sera(giorno)
    alt, az = sera["luna_alta"]
    trovate = [("sole", "solo-giorno", coricata(*sole_a(di_giorno(giorno))))]
    if alt > 12 and sera["chiarore"] > 0.3:
        trovate.append(("luna", "solo-notte", coricata(alt, az)))
    return [luce for luce in trovate if luce[2]]


def ombre(pagina, giorno):
    """I tre pezzi da mettere nella pagina: le ombre nel frontespizio (in piccolo), nella soglia, e di nuovo nella
    soglia sopra il sentiero, che è disegnato dopo gli alberi (dentro un ritaglio a forma di sentiero)."""
    cose, (scala, x, y) = cose_in_piedi(pagina, "tv-neve" in stagione(giorno))
    prima = "".join(f'<g class="{quando}"><path id="tv-ombra-{nome}" class="tv-ombra" d="{ombra(cose, verso)}"/></g>' for nome, quando, verso in luci(giorno))
    riprese = "".join(f'<g class="{quando}"><use href="#tv-ombra-{nome}"/></g>' for nome, quando, _ in luci(giorno))
    sentiero = re.search(r'<path class="sg-sentiero" d="([^"]*)"/>', pagina).group(1)
    return (f'<!-- ombre:inizio --><g transform="translate({x:.4g} {y:.4g}) scale({scala:.4g})">{prima}</g><!-- ombre:fine -->',
            f'<!-- ombre:inizio -->{riprese}<!-- ombre:fine -->',
            f'<!-- ombre:inizio --><clipPath id="tv-sul-sentiero"><path d="{sentiero}"/></clipPath><g clip-path="url(#tv-sul-sentiero)">{riprese}</g><!-- ombre:fine -->')


def con_le_ombre_dei_boschi(pagina, giorno):
    """La pagina con, sotto ogni bosco lontano, le ombre dei suoi alberi: più leggere, perché sono lontane."""
    def sotto(m):
        return ("<!-- ombre:inizio -->" + "".join(f'<g class="{quando}"><path class="tv-ombra tv-ombra-lontana" d="{ombra_del_bosco(m.group(0), verso)}"/></g>'
                                                  for _, quando, verso in luci(giorno)) + "<!-- ombre:fine -->" + m.group(0))
    return re.sub(r'<g class="cs-bosco-lontan(?:issim)?o">.*?</g>', sotto, pagina, flags=re.S)


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


# I mari della luna, con il nord in alto e il lembo del Mare delle Crisi a destra (come la si vede dal nostro emisfero):
# centro, due raggi e inclinazione, in raggi lunari. Un disegno alla buona della sua faccia: le Piogge, la Serenità,
# la Tranquillità, le Crisi, la Fecondità, il Nettare, l'Oceano delle Tempeste, le Nubi, gli Umori.
MARI = [(-0.40, -0.42, 0.33, 0.27, -18), (0.13, -0.40, 0.19, 0.19, 0), (0.34, -0.15, 0.24, 0.18, 28), (0.69, -0.29, 0.10, 0.14, 0), (0.58, 0.10, 0.11, 0.18, 12),
        (0.37, 0.29, 0.11, 0.10, 0), (-0.68, -0.04, 0.21, 0.42, 8), (-0.24, 0.38, 0.22, 0.16, 0), (-0.52, 0.43, 0.13, 0.12, 0)]


def luna_vera(x, y, r, vista, verso_il_sole, nord):
    """La luna al suo posto nel cielo: il suo chiarore, il disco con i mari (girato come quella sera) e, sopra, la
    parte in ombra, dal lato opposto al sole. Quando è una falce l'ombra è appena più chiara del cielo: la luce
    cinerea, che viene dalla Terra."""
    alone = r * (3 + 4 * vista)
    mari = "".join(f'<ellipse cx="{n(a * r)}" cy="{n(b * r)}" rx="{n(c * r)}" ry="{n(d * r)}"' + (f' transform="rotate({e} {n(a * r)} {n(b * r)})"' if e else "") + "/>"
                   for a, b, c, d, e in MARI)
    cinerea = 1 - min(1.0, vista / 0.45)
    ombra_colore = "#" + "".join(f"{round(buio + (chiaro - buio) * cinerea):02X}" for buio, chiaro in ((0x0A, 0x27), (0x10, 0x36), (0x1B, 0x50)))
    if vista > 0.988:
        ombra = ""
    elif vista < 0.012:
        ombra = f'<circle r="{n(r)}" fill="{ombra_colore}"/>'
    else:
        ombra = (f'<path transform="rotate({n(verso_il_sole)})" fill="{ombra_colore}" '
                 f'd="M0 {n(-r)}A{n(r)} {n(r)} 0 0 0 0 {n(r)}A{n(r * abs(1 - 2 * vista))} {n(r)} 0 0 {0 if vista < 0.5 else 1} 0 {n(-r)}Z"/>')
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(alone)}" fill="url(#tv-l)" opacity="{0.4 + 0.5 * vista:.2f}"/>'
            f'<g transform="translate({n(x)} {n(y)})"><circle class="tv-luna" r="{n(r)}"/><g class="tv-mari" transform="rotate({n(nord)})">{mari}</g>{ombra}</g>')


def disegna_cielo(giorno, stretto, lingua):
    """Il cielo di una sera, per il computer o (stretto) per il telefono, dove i punti sono un po' più grandi.
    In due gruppi: il primo si vede con le parole del frontespizio; il secondo, tv-dopo (ciò che cadrebbe sulle parole, le linee
    delle figure, i nomi) compare quando le parole se ne sono andate."""
    c = cielo_di_sera(giorno, stretto, lingua)
    ingrandisci = 1.3 if stretto else 1.0

    def dopo(x, y, margine=0):
        return any(x0 - margine <= x <= x1 + margine and y0 - margine <= y <= y1 + margine for x0, y0, x1, y1 in PAROLE.get((stretto, lingua), ()))

    f = {False: [], True: []}
    x, y, larga, alta, immagine = chiarore_della_via(giorno, stretto, round(c["buio"], 2))
    f[False].append(f'<image x="{x}" y="{y}" width="{larga}" height="{alta}" preserveAspectRatio="none" href="data:image/png;base64,{immagine}"/>')
    for classe, punti in (("tv-polvere", c["polvere"]), ("tv-velo-stelle", c["velo"])):
        for quando in (False, True):
            d = "".join(f"M{round(x)} {round(y)}h0" for x, y in punti if dopo(x, y) == quando)
            if d:
                f[quando].append(f'<path class="{classe}" opacity="{0.3 + 0.7 * c["buio"]:.2f}" d="{d}"/>')
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
        misura = 0 if g < 0.5 else 1 if g < 1.5 else 2 if g < 2.5 else 3 if g < 3.3 else 4 if g < 4.0 else 5 if g < 4.8 else 6 if g < 5.6 else 7
        # il colore, dall'indice B-V del catalogo: si distingue solo nelle stelle abbastanza luminose
        tinta = ("" if misura > 5 else " tv-blu" if colore <= -0.05 else " tv-azzurra" if colore <= 0.25 else "" if colore <= 0.65
                 else " tv-gialla" if colore <= 1.0 else " tv-arancio" if colore <= 1.4 else " tv-rossa")
        quando = dopo(x, y, max(4, 12 + 2 * (5 - misura)))    # al largo dalle parole: di più le stelle più luminose
        if g < 0.95:
            f[quando or dopo(x, y, 14)].append(f'<circle cx="{round(x)}" cy="{round(y)}" r="{n((3.5 - 0.8 * g) * 4.4 * ingrandisci)}" fill="url(#tv-g)" opacity=".3"/>')
        gruppi.setdefault((quando, misura, tinta), []).append(f"M{round(x)} {round(y)}h0")
    for (quando, misura, tinta), punti in sorted(gruppi.items()):
        f[quando].append(f'<path class="tv-s{misura}{tinta}" d="{"".join(punti)}"/>')
    if c["luna"]:
        x, y, r, vista, verso_il_sole, nord = c["luna"]
        f[dopo(x, y, r * (3 + 4 * vista) * 0.5)].append(luna_vera(x, y, r, vista, verso_il_sole, nord))
    for x, y, g, nome in c["pianeti"]:
        r = max(2.3, 3.6 - 0.75 * g) * ingrandisci
        f[dopo(x, y, r * 4)].append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 4)}" fill="url(#tv-g)" opacity=".34"/><circle class="tv-{nome.lower()}" cx="{n(x)}" cy="{n(y)}" r="{n(r)}"/>')
    def classi(x, titolo, peso):
        mezzo = 4.3 * len(titolo) + 8
        return "tv-nome" + (" tv-nome-pianeta" if peso == 50 else "") + (" tv-bordo" if not stretto and (x - mezzo < 280 or x + mezzo > 1180) else "")

    f[True].append("".join(f'<text class="{classi(x, t, peso)}" x="{n(x)}" y="{n(y)}">{t}</text>' for x, y, t, peso in c["nomi"]))
    if {"tv-perseidi", "tv-geminidi"} & set(stagione(giorno)):
        f[True].append('<path class="tv-cadente" d="M612 150l-74 58M846 338l-52 42M360 260l-40 30"/>')
    return f'<g>{"".join(f[False])}</g><g class="tv-dopo">{"".join(f[True])}</g>'


def sole_dell_angolo(giorno, stretto):
    """Dove sta il sole di giorno finché ci sono le parole del frontespizio: nelle finestre in piedi (stretto)
    nell'angolo in alto; nelle altre a destra, da y = 300 al solstizio d'estate a y = 450 a quello d'inverno."""
    if stretto:
        return 905, 64
    declinazione = sole_e_luna(giuliano(mezzogiorno(giorno)))[3]
    return 1245, 300 + 150 * (23.44 - declinazione) / 46.88


def volta(giorno, alone, quale=0, lingua="it"):
    """Il cielo della tavola. La prima scena lo disegna, in due misure; la seconda lo riprende tale e quale."""
    if quale == 0:
        sfumi = "".join(f'<radialGradient id="tv-{nome}"><stop offset="0" stop-color="{colore}" stop-opacity="{forza}"/><stop offset="1" stop-color="{colore}" stop-opacity="0"/></radialGradient>'
                        for nome, colore, forza in (("g", "#DCE6F6", 1), ("r", "#E98FB2", 0.9), ("b", "#8DB7F2", 0.8)))
        # il chiarore della luna: forte vicino al disco, poi un alone largo e leggero
        sfumi += ('<radialGradient id="tv-l">' + "".join(f'<stop offset="{dove}" stop-color="#FFE7B5" stop-opacity="{forza}"/>' for dove, forza in ((0, 0.9), (0.2, 0.42), (0.5, 0.12), (1, 0)))
                  + '</radialGradient>')
        cielo = (f'<defs>{sfumi}</defs><g id="tv-cielo-largo" class="tv-largo">{disegna_cielo(giorno, False, lingua)}</g>'
                 f'<g id="tv-cielo-stretto" class="tv-stretto">{disegna_cielo(giorno, True, lingua)}</g>')
        carta = f'<g id="tv-carta-giorno" class="tv-carta"><g class="tv-dopo">{disegna_giorno(giorno, alone, lingua)}</g></g>'
    else:
        cielo = '<use href="#tv-cielo-largo"/><use href="#tv-cielo-stretto"/>'
        carta = '<use href="#tv-carta-giorno"/>'
    rondini = ""
    if (3, 25) <= (giorno.month, giorno.day) <= (9, 20):
        caso = random.Random(giorno.toordinal())
        voli = []
        for _ in range(caso.randint(3, 6)):
            x, y, s = caso.uniform(96, 372), caso.uniform(236, 392), caso.uniform(0.8, 1.35)   # sotto la riga della data
            voli.append(f"M{n(x)} {n(y)}q{n(3.5 * s)} {n(-4.6 * s)} {n(7 * s)} {n(-0.6 * s)}q{n(3.8 * s)} {n(-4 * s)} {n(7.4 * s)} {n(0.8 * s)}")
        rondini = f'<path class="tv-rondini solo-giorno" d="{"".join(voli)}"/>'
    # Di giorno, con le parole, il sole non può stare al suo posto vero: finirebbe dietro le parole. Sta dove le
    # parole lasciano libero il foglio a ogni misura di finestra (le stesse righe misurate che tengono lontane le
    # stelle): nelle finestre larghe a destra, più alto d'estate e più basso d'inverno, ma mai così in alto da
    # finire sotto la testata sugli schermi bassi; in quelle in piedi nell'angolo in alto, accanto alla data. Quando
    # le parole se ne vanno lascia il posto alla carta del giorno, dove il sole è dov'è davvero. Di notte la luna non
    # sta più qui: è nel cielo, dove sta davvero.
    def emblema(classe, x, y):
        return (f'<g class="{classe}"><circle cx="{n(x)}" cy="{n(y)}" r="80" fill="url(#{alone})"/>'
                f'<circle class="volta-sole" cx="{n(x)}" cy="{n(y)}" r="18"/></g>')

    astro = emblema("tv-emblema-largo", *sole_dell_angolo(giorno, False)) + emblema("tv-emblema-stretto", *sole_dell_angolo(giorno, True))
    return f'<g class="volta"><g class="volta-stelle">{cielo}</g><g class="solo-giorno">{carta}</g>{rondini}<g class="tv-astro solo-giorno"><g class="tv-emblema">{astro}</g></g></g>'


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


# ---------- Il lunario: le stesse cose della tavola, dette a parole ----------

GIORNI = {"it": ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"],
          "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
VERSO = {"it": ["nord", "nord-est", "est", "sud-est", "sud", "sud-ovest", "ovest", "nord-ovest"],
         "en": ["the north", "the north-east", "the east", "the south-east", "the south", "the south-west", "the west", "the north-west"]}
LA_LUNA_E = {"it": {"nuova": "È nuova: non si vede.", "crescente": "È crescente, illuminata per {quanto}%.", "primo": "È al primo quarto, illuminata per {quanto}%.",
                    "piena": "È piena.", "calante": "È calante, illuminata per {quanto}%.", "ultimo": "È all’ultimo quarto, illuminata per {quanto}%."},
             "en": {"nuova": "It is new: it cannot be seen.", "crescente": "It is waxing, {quanto}% lit.", "primo": "It is at first quarter, {quanto}% lit.",
                    "piena": "It is full.", "calante": "It is waning, {quanto}% lit.", "ultimo": "It is at last quarter, {quanto}% lit."}}
FASI = {"it": {"nuova": "nuova", "crescente": "crescente", "primo": "primo quarto", "piena": "piena", "calante": "calante", "ultimo": "ultimo quarto"},
        "en": {"nuova": "new", "crescente": "waxing", "primo": "first quarter", "piena": "full", "calante": "waning", "ultimo": "last quarter"}}


def lunario(giorno, lingua):
    """Il lunario del giorno: il foglio che si apre dalla riga della data, con il sole, la luna, i pianeti e le
    stelle di quella sera detti a parole, e la luna delle sette sere che vengono. Tutto viene dagli stessi conti
    della tavola; gli orari della luna sono arrotondati ai cinque minuti, perché i conti non sono più fini di così."""
    it = lingua == "it"
    largo, stretto = cielo_di_sera(giorno, False, lingua), cielo_di_sera(giorno, True, lingua)
    ora_tavola = a_notte_fatta(giorno)

    def ora(quando, tonda=1):
        minuti = round((quando.hour * 60 + quando.minute + quando.second / 60) / tonda) * tonda % 1440
        h, m = divmod(minuti, 60)
        return f"{h}:{m:02d}" if it else f"{(h - 1) % 12 + 1}:{m:02d} {'am' if h < 12 else 'pm'}"

    def verso_le(quando):
        testo = ora(quando, 5)
        if not it:
            return "around " + testo
        return ("verso l’" if testo.startswith("1:") else "verso le ") + testo

    def quanti(numero, uno, tanti):
        return f"{numero} {uno if numero == 1 else tanti}"

    def migliaia(numero):
        return f"{numero:,}".replace(",", "." if it else ",")

    def dove(alt, az, lei=False):
        punto = VERSO[lingua][round(az / 45) % 8]
        if alt < 10:
            return f"bass{'a' if lei else 'o'} a {punto}" if it else f"low in {punto}"
        return f"a {punto}, alt{'a' if lei else 'o'} {round(alt)} gradi" if it else f"in {punto}, {round(alt)} degrees up"

    # il sole
    sorge, tramonta = sole_del_giorno(giorno)
    ieri = sole_del_giorno(giorno - datetime.timedelta(days=1))
    dura = round((tramonta - sorge).total_seconds() / 60)
    cambia = dura - round((ieri[1] - ieri[0]).total_seconds() / 60)
    ore, minuti = divmod(dura, 60)
    if it:
        lungo = quanti(ore, "ora", "ore") + (f" e {quanti(minuti, 'minuto', 'minuti')}" if minuti else "")
        rispetto = "come ieri" if cambia == 0 else f"{'un minuto' if abs(cambia) == 1 else f'{abs(cambia)} minuti'} {'più' if cambia > 0 else 'meno'} di ieri"
        sole = f"Sorge alle {ora(sorge)} e tramonta alle {ora(tramonta)}. Il giorno dura {lungo}: {rispetto}."
    else:
        lungo = quanti(ore, "hour", "hours") + (f" and {quanti(minuti, 'minute', 'minutes')}" if minuti else "")
        rispetto = "the same as yesterday" if cambia == 0 else f"{quanti(abs(cambia), 'minute', 'minutes')} {'longer' if cambia > 0 else 'shorter'} than yesterday"
        sole = f"It rises at {ora(sorge)} and sets at {ora(tramonta)}. The day lasts {lungo}: {rispetto}."
    # di giorno: l'ora delle ombre, dov'è il sole a quell'ora e quanto sono lunghe
    ora_ombre = di_giorno(giorno)
    alt, az = sole_a(ora_ombre)
    lunga = 1 / math.tan(math.radians(alt))
    passo = 0 if lunga < 0.66 else 1 if lunga < 0.85 else 2 if lunga < 1.25 else 3 if lunga < 1.75 else 4 if lunga < 2.25 else 5
    if it:
        quanto_lunga = ("poco più della metà di", "tre quarti di", "quanto", "una volta e mezza", "due volte", "due volte e mezza")[passo]
        sole += (f" Le ombre della tavola sono quelle delle {ora(ora_ombre)}, due ore dopo il mezzogiorno vero, con il sole {dove(alt, az)}: "
                 f"un’ombra è lunga {quanto_lunga} ciò che la fa. Quando le parole del titolo se ne vanno, sul foglio compare la strada che il sole fa oggi, con le ore.")
    else:
        quanto_lunga = ("just over half the length of", "three quarters the length of", "as long as", "one and a half times as long as", "twice as long as",
                        "two and a half times as long as")[passo]
        sole += (f" The shadows on the plate are those of {ora(ora_ombre)}, two hours after true noon, with the sun {dove(alt, az)}: "
                 f"a shadow is {quanto_lunga} what casts it. When the title’s words leave, the path the sun takes today appears on the sheet, with its hours.")

    # la luna: com'è, dov'è all'ora della tavola, quando tramonta o sorge
    vista, _, nome = fase(giorno)
    quanto = max(1, min(99, round(vista * 100)))
    # in italiano «per l’11%», «per l’80%», ma «per il 9%»
    luna = LA_LUNA_E[lingua][nome].format(quanto=(("l’" if quanto in (1, 8, 11) or 80 <= quanto <= 89 else "il ") if it else "") + str(quanto))
    eventi = luna_del_giorno(giorno)
    alt, az = largo["luna_alta"]
    if alt > 0:
        poi = [quando for che, quando in eventi if che == "tramonta" and quando > ora_tavola]
        luna += (f" All’ora della tavola è {dove(alt, az, True)}" if it else f" At the time of the plate it is {dove(alt, az)}")
        luna += (f"; tramonta {verso_le(poi[0])}." if it else f"; it sets {verso_le(poi[0])}.") if poi else "."
    else:
        prima = [quando for che, quando in eventi if che == "tramonta" and quando <= ora_tavola]
        poi = [quando for che, quando in eventi if che == "sorge" and quando > ora_tavola]
        if prima:
            luna += f" È tramontata {verso_le(prima[-1])}, prima dell’ora della tavola." if it else f" It set {verso_le(prima[-1])}, before the time of the plate."
        elif poi:
            luna += f" Sorge {verso_le(poi[0])}, dopo l’ora della tavola." if it else f" It rises {verso_le(poi[0])}, after the time of the plate."

    if any(nome == "luna" for nome, _, _ in luci(giorno)):
        luna += " Stanotte le ombre sul prato sono le sue." if it else " Tonight the shadows on the grass are cast by the moon."
    di_giorno_c_e = luna_di_giorno(giorno)
    if di_giorno_c_e:
        luna += (f" Di giorno, alle {ora(ora_ombre)}, è {dove(di_giorno_c_e[4], di_giorno_c_e[5], True)}." if it
                 else f" By day, at {ora(ora_ombre)}, it is {dove(di_giorno_c_e[4], di_giorno_c_e[5])}.")

    # la luna delle sette sere che vengono
    sere, dette = [], []
    for k in range(7):
        sera = giorno + datetime.timedelta(days=k)
        quanta, cresce, come = fase(sera)
        x = 24 + 48 * k
        if quanta > 0.988:
            luce = '<circle class="tv-lune-luce" r="13"/>'
        elif quanta < 0.012:
            luce = ""
        else:
            luce = f'<path class="tv-lune-luce" d="M0 -13A13 13 0 0 1 0 13A{n(13 * abs(1 - 2 * quanta))} 13 0 0 {0 if quanta < 0.5 else 1} 0 -13Z"/>'
        giorno_breve = f"{GIORNI[lingua][sera.weekday()][:3]} {sera.day}"
        sere.append(f'<g transform="translate({x} 18){"" if cresce else " scale(-1 1)"}"><circle class="tv-lune-ombra" r="13"/>{luce}</g>'
                    f'<text class="tv-lune-giorno" x="{x}" y="52">{giorno_breve}</text>')
        dette.append(f"{giorno_breve} {FASI[lingua][come]}")
    lune = (f'<svg class="tv-lune" viewBox="0 0 336 60" role="img" aria-label="{"La luna delle prossime sere" if it else "The moon on the coming evenings"}: {", ".join(dette)}">'
            + "".join(sere) + "</svg>")

    # i pianeti
    alti = [(nome, alt, az) for nome, alt, az in largo["pianeti_alti"] if alt > 4]
    if alti:
        pianeti = " ".join(f"{nome} è {dove(alt, az, nome == 'Venere')}." if it else f"{IN_INGLESE[nome]} is {dove(alt, az)}." for nome, alt, az in alti)
    else:
        pianeti = ("A quell’ora nessuno dei quattro (Venere, Marte, Giove, Saturno) è sopra l’orizzonte." if it
                   else "None of the four (Venus, Mars, Jupiter, Saturn) is above the horizon at that time.")

    # le stelle
    nomi = list(dict.fromkeys(t for c in (largo, stretto) for _, _, t, peso in c["nomi"] if peso != 50))
    con_la_luna = largo["chiarore"] > 0.2
    if it:
        stelle = (f"La tavola ne ha {migliaia(len(largo['stelle']))}: quelle che a quell’ora si vedono a occhio nudo verso sud, "
                  f"{'con questa luna' if con_la_luna else 'da un posto buio'}. Al telefono, dove il foglio è più stretto, {migliaia(len(stretto['stelle']))}. "
                  f"Sul foglio hanno il nome: {', '.join(nomi)}.")
    else:
        stelle = (f"The plate has {migliaia(len(largo['stelle']))} of them: the ones you can see with the naked eye at that time, looking south "
                  f"{'under this moon' if con_la_luna else 'from a dark place'}. On a phone, where the sheet is narrower, {migliaia(len(stretto['stelle']))}. "
                  f"Named on the plate: {', '.join(nomi)}.")
    cadenti = set(stagione(giorno)) & {"tv-perseidi", "tv-geminidi"}
    if cadenti:
        perseidi = "tv-perseidi" in cadenti
        stelle += ((" Sono le notti delle Perseidi, le stelle cadenti d’agosto." if perseidi else " Sono le notti delle Geminidi, le stelle cadenti di dicembre.") if it
                   else (" These are the nights of the Perseids, August’s shooting stars." if perseidi else " These are the nights of the Geminids, December’s shooting stars."))

    data = f"{GIORNI[lingua][giorno.weekday()].capitalize()} {'1º' if it and giorno.day == 1 else giorno.day} {MESI[lingua][giorno.month - 1]} {giorno.year}"
    if it:
        apre = f"Il cielo della tavola è quello delle {ora(ora_tavola)}, due ore dopo il tramonto, guardando a sud dalla Calabria."
        voci = (("Il sole", sole), ("La luna", luna + lune), ("I pianeti", pianeti), ("Le stelle", stelle))
        fonti = ("Le stelle vengono dal Bright Star Catalogue (Hoffleit e Warren, 1991), con i loro colori. Il sole, la luna e i pianeti sono "
                 "calcolati, e gli orari valgono per un orizzonte libero. La luna è disegnata più grande del vero; le linee delle figure e il "
                 "chiarore della Via Lattea sono un disegno. Di giorno la strada del sole è disegnata più in piccolo del cielo della notte, perché "
                 "ci stia tutta; le ombre vanno dalla parte giusta e sono lunghe il giusto, viste di scorcio.")
        chiudi = "Chiudi"
    else:
        apre = f"The sky on the plate is the one at {ora(ora_tavola)}, two hours after sunset, looking south from Calabria."
        voci = (("The sun", sole), ("The moon", luna + lune), ("The planets", pianeti), ("The stars", stelle))
        fonti = ("The stars come from the Bright Star Catalogue (Hoffleit and Warren, 1991), with their colours. The sun, the moon and the planets "
                 "are computed, and the times hold for a clear horizon. The moon is drawn larger than life; the lines of the figures and the "
                 "glow of the Milky Way are a drawing. By day the sun’s path is drawn smaller than the night sky, so that all of it fits; "
                 "the shadows fall the right way and are the right length, seen foreshortened.")
        chiudi = "Close"
    return ('<!-- lunario:inizio --><div class="definizione tv-lunario" id="lunario" popover>\n'
            f'  <p class="definizione-termine">{data}</p>\n  <p>{apre}</p>\n  <dl class="tv-voci">\n'
            + "".join(f"    <div><dt>{titolo}</dt><dd>{testo}</dd></div>\n" for titolo, testo in voci)
            + f'  </dl>\n  <p class="tv-fonti">{fonti}</p>\n'
            f'  <button type="button" class="chiudi-definizione" popovertarget="lunario" popovertargetaction="hide">{chiudi}</button>\n</div><!-- lunario:fine -->\n')


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
    # la riga della data è un pulsante: apre il lunario, che sta in fondo a <main>
    cambia(r'<div class="frontespizio-parole">', lambda m: f'<p class="tv-tiratura"><button type="button" class="tv-apri" popovertarget="lunario">{riga_della_data(giorno, lingua)}</button></p>\n      ' + m.group(0))
    cambia(r'</main>', lambda m: lunario(giorno, lingua) + m.group(0))
    cambia(r'<main id="contenuto" class="pagina-casa">', f'<main id="contenuto" class="pagina-casa {" ".join(c for c in stagione(giorno) if c in DI_COLORE)}">')
    dietro, sopra = stagionali(giorno)
    cambia(r'<!-- colle:inizio -->(<path class="fr-collina"[^>]*/>)', lambda m: dietro + "<!-- colle:inizio -->" + m.group(1) + sopra)
    # le ombre della casa e degli alberi: sul prato delle due scene, sotto i tronchi, e sopra il sentiero della soglia
    lontane, vicine, sul_sentiero = ombre(pagina, giorno)
    sul_prato = iter((lontane, vicine))
    cambia(r'<path class="cs-tronco"', lambda m: next(sul_prato) + m.group(0), 2)
    cambia(r'<path class="sg-sentiero" d="[^"]*"/>', lambda m: m.group(0) + sul_sentiero)
    pagina = con_le_ombre_dei_boschi(pagina, giorno)
    mancano = [schema for schema, fatto in conta if not fatto]
    if mancano:
        sys.exit(f"tavola.py: nella pagina ({lingua}) non trovo: {mancano}. La home è cambiata: va aggiornato tavola().")
    return pagina


def studio(pagina, giorno):
    """La pagina dello studio con la stagione e la luna di quel giorno."""
    vista, cresce, _ = fase(giorno)
    pagina, a = re.subn(r'<path class="bs-falce solo-notte"[^>]*/>', lambda m: luna_svg(vista, cresce, "translate(815 79) scale(0.58)"), pagina, count=1)
    pagina, b = re.subn(r'<main id="contenuto" class="pagina-studio">', f'<main id="contenuto" class="pagina-studio {" ".join(c for c in stagione(giorno) if c in DI_COLORE)}">', pagina, count=1)
    if (a, b) != (1, 1):
        sys.exit(f"tavola.py: nella pagina dello studio non trovo la luna o <main> ({a}, {b}). La pagina è cambiata: va aggiornato studio().")
    return pagina


def senza_cielo(pagina):
    """La pagina senza i disegni del cielo e della luna, che dipendono da conti con seni e coseni: due computer diversi
    possono arrotondarli in modo diverso, e una stella sul bordo può esserci in uno e non nell'altro. Il resto (le
    parole, la data, la stagione, tutto ciò che non è tavola) deve invece essere uguale lettera per lettera."""
    pagina = re.sub(r'<g class="volta">.*?(?=<g class="(?:fr-zoom|sg-avvicina)">)', "<!-- cielo -->", pagina, flags=re.S)
    pagina = re.sub(r'<!-- lunario:inizio -->.*?<!-- lunario:fine -->', "<!-- lunario -->", pagina, flags=re.S)   # anche il lunario è fatto di quei conti
    pagina = re.sub(r'<!-- ombre:inizio -->.*?<!-- ombre:fine -->', "<!-- ombre -->", pagina, flags=re.S)         # e le ombre
    return re.sub(r'<g class="solo-notte" transform="[^"]*">.*?</g>', "<!-- luna -->", pagina, flags=re.S)


def scrivi(da, a, giorno):
    """Legge le pagine in «da» e le scrive, con la tavola di quel giorno, in «a» (la stessa cartella, per il sito già
    costruito)."""
    for nome in list(PAGINE) + STUDIO:
        testo = (da / nome).read_text(encoding="utf-8")
        testo = tavola(testo, giorno, PAGINE[nome]) if nome in PAGINE else studio(testo, giorno)
        (a / nome).parent.mkdir(parents=True, exist_ok=True)
        (a / nome).write_text(testo, encoding="utf-8")
        print(f"{a / nome}: {len(testo.encode('utf-8')) / 1024:.0f} KB")


def racconta(giorno):
    c = cielo_di_sera(giorno)
    vista, cresce, _ = fase(giorno)
    luna = CON_LA_LUNA["it"][fase(giorno)[2]]
    return (f"{giorno.isoformat()}, cielo delle {a_notte_fatta(giorno):%H:%M}: {' '.join(stagione(giorno))}; {luna} ({vista:.0%}), cielo buio {c['buio']:.0%}; {len(c['stelle'])} stelle, "
            f"{len(c['polvere']) + len(c['velo'])} di polvere; " + ", ".join(t for _, _, t, _ in c["nomi"]))


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
    prova("stelle nell'estratto del catalogo, in migliaia", len(STELLE) / 1000, 8.33, 0.1)
    # la luna: nell'eclissi sta sul sole (vista dal centro della Terra, a un terzo di grado), e la luna piena sorge quando il sole tramonta
    jd = giuliano(datetime.datetime(2024, 4, 8, 18, 21, tzinfo=utc))
    prova("eclissi dell'8 aprile 2024: gradi fra la luna e il sole, per ascensione retta e declinazione", distanza(*dove_luna(jd), *dove_sole(jd)), 0.33, 0.35)
    prova("  e ascensione retta del sole, in ore", dove_sole(jd)[0] / 15, 1.19, 0.02)
    piena = datetime.date(2024, 9, 17)
    sorge = [quando for che, quando in luna_del_giorno(piena) if che == "sorge"][0]
    prova("luna piena del 17 settembre 2024: minuti fra il tramonto del sole e il sorgere della luna", (sorge - tramonto(piena)).total_seconds() / 60, 0, 25)
    alba = sole_del_giorno(datetime.date(2026, 6, 21))[0]
    prova("alba del 21/6, in ore", alba.hour + alba.minute / 60, 5.5, 0.15)
    # il giorno: a mezzogiorno vero il sole sta a sud, alto quanto vogliono la latitudine e la stagione
    for giorno, declinazione in ((datetime.date(2026, 6, 21), 23.44), (datetime.date(2026, 12, 21), -23.44)):
        alt, az = sole_a(mezzogiorno(giorno))
        prova(f"mezzogiorno vero del {giorno.day}/{giorno.month}: azimut del sole", az, 180, 0.4)
        prova("  e altezza", alt, 90 - LAT + declinazione, 0.05)
    quando = mezzogiorno(datetime.date(2026, 11, 3))
    prova("mezzogiorno vero del 3/11, quando il sole è più in anticipo: in ore", quando.hour + quando.minute / 60, 11 + 38.5 / 60, 0.04)
    # le ombre: con il sole a sud vengono dritte verso chi guarda, con il sole a ovest vanno a sinistra; a 45 gradi sono lunghe quanto le cose
    kx, ky = coricata(45, 180)
    prova("ombra con il sole a sud, alto 45 gradi: di fianco", kx, 0, 0.001)
    prova("  e verso chi guarda", ky, SCORCIO, 0.001)
    prova("ombra con il sole a ovest, alto 45 gradi: di fianco", coricata(45, 270)[0], -1, 0.001)
    prova("ombre dalla scena della soglia: quante cose in piedi", len(cose_in_piedi((SITO / "index.html").read_text(encoding="utf-8"))[0]), 29, 3)
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
    if "--uguali" in sys.argv:
        if len(altri) != 2:
            sys.exit("tavola.py --uguali <pagina> <pagina>")
        una, altra = (senza_cielo(pathlib.Path(f).read_text(encoding="utf-8")) for f in altri)
        return 0 if una == altra else 1
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
