"""Cose comuni ai controlli del sito: dove sono i file, come si leggono le pagine e le misure delle immagini."""
import pathlib, struct
from html.parser import HTMLParser

SITO = pathlib.Path(__file__).resolve().parents[2]
LAVORO = SITO / "_lavoro"
ESCLUSE = {".git", "_lavoro"}


def file_del_sito(*estensioni):
    """I file pubblici del sito con queste estensioni, senza _lavoro e .git."""
    for p in sorted(SITO.rglob("*")):
        if not p.is_file():
            continue
        if any(parte in ESCLUSE for parte in p.relative_to(SITO).parts):
            continue
        if not estensioni or p.suffix.lower() in estensioni:
            yield p


def pagine():
    return list(file_del_sito(".html"))


def nome(p):
    return str(p.relative_to(SITO))


VUOTI = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Albero(HTMLParser):
    """Legge una pagina e tiene i tag con gli attributi, il testo e gli errori di forma."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag = []          # (nome, attributi come dict, riga)
        self.aperti = []       # pila dei tag aperti
        self.errori = []
        self.testo = []        # (testo, pila dei tag aperti in quel momento)
        self.in_svg = 0

    def handle_starttag(self, nome, attributi):
        att = dict(attributi)
        self.tag.append((nome, att, self.getpos()[0]))
        if nome in VUOTI:
            return
        self.aperti.append((nome, att))
        if nome == "svg":
            self.in_svg += 1

    def handle_startendtag(self, nome, attributi):
        self.tag.append((nome, dict(attributi), self.getpos()[0]))

    def handle_endtag(self, nome):
        if nome in VUOTI:
            return
        if not self.aperti:
            self.errori.append(f"riga {self.getpos()[0]}: </{nome}> senza apertura")
            return
        if self.aperti[-1][0] == nome:
            self.aperti.pop()
            if nome == "svg":
                self.in_svg -= 1
            return
        # Un tag chiuso fuori ordine.
        nomi = [n for n, _ in self.aperti]
        if nome in nomi:
            while self.aperti and self.aperti[-1][0] != nome:
                rimasto = self.aperti.pop()[0]
                if rimasto not in ("p", "li", "dt", "dd", "option"):
                    self.errori.append(f"riga {self.getpos()[0]}: <{rimasto}> non chiuso prima di </{nome}>")
            self.aperti.pop()
        else:
            self.errori.append(f"riga {self.getpos()[0]}: </{nome}> senza apertura")

    def handle_data(self, dati):
        # Anche gli spazi fra un tag e l'altro: separano le parole.
        self.testo.append((dati, [(n, a) for n, a in self.aperti]))


def leggi(p):
    a = Albero()
    a.feed(p.read_text(encoding="utf-8"))
    a.close()
    return a


# ---------- Le immagini, senza librerie: formato e misure, e le scatole dell'AVIF ----------

def scatole(dati, inizio=0, fine=None):
    """Le scatole (box) di un file ISOBMFF, come l'AVIF, fra inizio e fine: (tipo, inizio del contenuto, fine)."""
    fine = len(dati) if fine is None else fine
    i = inizio
    while i + 8 <= fine:
        lung, tipo = struct.unpack(">I4s", dati[i:i + 8])
        testa = 8
        if lung == 1:
            lung, testa = struct.unpack(">Q", dati[i + 8:i + 16])[0], 16
        elif lung == 0:
            lung = fine - i
        if lung < testa or i + lung > fine:
            return
        yield tipo, i + testa, i + lung
        i += lung


def scatola(dati, *percorso):
    """Il contenuto (inizio, fine) della prima scatola a quel percorso, per esempio b"meta", b"iinf"; di meta si salta
    la testa con versione e flag. None se non c'è."""
    a, b = 0, len(dati)
    for tipo in percorso:
        for t, x, y in scatole(dati, a, b):
            if t == tipo:
                a, b = (x + 4 if t == b"meta" else x), y
                break
        else:
            return None
    return a, b


def misure(p):
    """(formato, larghezza, altezza) di un'immagine JPEG, PNG, WebP o AVIF, lette dal file; None se non si capisce."""
    dati = p.read_bytes()
    if dati[:2] == b"\xff\xd8":
        i = 2
        while i + 9 <= len(dati) and dati[i] == 0xFF:
            marca = dati[i + 1]
            if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):      # SOF: altezza e larghezza
                h, w = struct.unpack(">HH", dati[i + 5:i + 9])
                return "jpeg", w, h
            i += 2 + struct.unpack(">H", dati[i + 2:i + 4])[0]
    elif dati[:8] == b"\x89PNG\r\n\x1a\n":
        return ("png", *struct.unpack(">II", dati[16:24]))
    elif dati[:4] == b"RIFF" and dati[8:12] == b"WEBP":
        tipo = dati[12:16]
        if tipo == b"VP8 ":
            w, h = struct.unpack("<HH", dati[26:30])
            return "webp", w & 0x3FFF, h & 0x3FFF
        if tipo == b"VP8L":
            x = int.from_bytes(dati[21:25], "little")
            return "webp", (x & 0x3FFF) + 1, ((x >> 14) & 0x3FFF) + 1
        if tipo == b"VP8X":
            return "webp", int.from_bytes(dati[24:27], "little") + 1, int.from_bytes(dati[27:30], "little") + 1
    elif dati[4:8] == b"ftyp" and dati[8:12] in (b"avif", b"avis"):
        dove = scatola(dati, b"meta", b"iprp", b"ipco", b"ispe")
        if dove:
            return ("avif", *struct.unpack(">II", dati[dove[0] + 4:dove[0] + 12]))
    return None
