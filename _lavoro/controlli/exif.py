"""Nessuna immagine del sito porta metadati: niente EXIF (con l'eventuale GPS), XMP o IPTC nei JPEG, niente blocchi
eXIf, iTXt o tEXt nei PNG, niente blocchi EXIF o XMP nei WebP, niente elementi Exif o XMP negli AVIF (dal 7/11, con le
copie delle schermate). Le foto di Sic vanno rifatte da zero (qlmanage, poi sips) prima di entrare nel sito; le copie
delle schermate le fa strumenti/schermate.py, che non scrive metadati.

Dal 14/11 anche le credenziali del contenuto (C2PA: un manifesto firmato con il certificato, il programma che ha fatto
il file, identificativi e orari), che hanno tutti i file del kit del logo: nei JPEG stanno nei segmenti APP11, nei PNG
nel blocco caBX, negli altri formati in scatole loro, e si riconoscono dalle etichette. E gli SVG: niente <metadata>,
RDF o XMP, niente attributi di Inkscape, niente commento di Illustrator, niente percorsi del Mac con il nome
dell'utente. Le copie che sono nel sito ne sono già prive; una copia nuova dal kit va pulita prima di entrare."""
import pathlib, struct, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import file_del_sito, nome, scatola, scatole


def jpeg(dati):
    trovati = []
    i = 2
    while i + 4 <= len(dati) and dati[i] == 0xFF:
        marca = dati[i + 1]
        if marca in (0xD9, 0xDA):  # fine dell'immagine o inizio dei dati
            break
        lung = struct.unpack(">H", dati[i + 2:i + 4])[0]
        corpo = dati[i + 4:i + 2 + lung]
        if marca == 0xE1 and corpo.startswith(b"Exif"):
            trovati.append("EXIF" + (" con GPS" if b"GPS" in corpo else ""))
        elif marca == 0xE1 and b"ns.adobe.com/xap" in corpo:
            trovati.append("XMP")
        elif marca == 0xED:
            trovati.append("IPTC")
        elif marca == 0xEB:  # APP11: le scatole JUMBF, dove stanno le credenziali C2PA
            trovati.append("APP11 (C2PA)")
        i += 2 + lung
    return trovati


def png(dati):
    trovati = []
    i = 8
    while i + 8 <= len(dati):
        lung, tipo = struct.unpack(">I4s", dati[i:i + 8])
        if tipo in (b"eXIf", b"iTXt", b"tEXt", b"zTXt"):
            trovati.append(tipo.decode())
        elif tipo == b"caBX":  # le credenziali C2PA
            trovati.append("caBX (C2PA)")
        i += 12 + lung
    return trovati


def webp(dati):
    """I blocchi del contenitore RIFF dopo «WEBP»: EXIF e XMP sono metadati (ICCP, il profilo dei colori, va bene)."""
    trovati = []
    i = 12
    while i + 8 <= len(dati):
        tipo, lung = dati[i:i + 4], struct.unpack("<I", dati[i + 4:i + 8])[0]
        if tipo == b"EXIF":
            trovati.append("EXIF" + (" con GPS" if b"GPS" in dati[i + 8:i + 8 + lung] else ""))
        elif tipo == b"XMP ":
            trovati.append("XMP")
        i += 8 + lung + (lung & 1)
    return trovati


def avif(dati):
    """Gli elementi dell'AVIF sono elencati in meta › iinf: uno di tipo Exif, o mime con application/rdf+xml (XMP), è
    un metadato. Il profilo dei colori sta altrove (colr) e va bene."""
    trovati = []
    dove = scatola(dati, b"meta", b"iinf")
    if not dove:
        return trovati
    a, b = dove
    for tipo, x, y in scatole(dati, a + 4 + (2 if dati[a] == 0 else 4), b):     # versione e flag, poi quanti sono
        if tipo != b"infe" or dati[x] < 2:
            continue
        p = x + 4 + (2 if dati[x] == 2 else 4) + 2                             # item_ID e protezione
        if dati[p:p + 4] == b"Exif":
            trovati.append("EXIF")
        elif dati[p:p + 4] == b"mime" and b"rdf+xml" in dati[p:y]:
            trovati.append("XMP")
    return trovati


# Le etichette di un manifesto C2PA, in qualunque formato.
C2PA = (b"urn:c2pa:", b"c2pa.claim", b"c2pa.signature")
# Nel testo di un SVG: il segno e che cosa è.
SVG = (("<metadata", "<metadata>"), ("c2pa", "C2PA"), ("<rdf:", "RDF"), ("adobe:ns:meta", "XMP"),
       ("sodipodi:", "Inkscape"), ("inkscape:", "Inkscape"), ("Adobe Illustrator", "Illustrator"),
       ("/Users/", "un percorso del Mac"))


def svg(dati):
    testo = dati.decode("utf-8", "replace")
    trovati = []
    for segno, cosa in SVG:
        if segno in testo and cosa not in trovati:
            trovati.append(cosa)
    return trovati


def main():
    problemi, visti = 0, {}
    for p in file_del_sito(".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"):
        dati = p.read_bytes()
        if p.suffix.lower() == ".svg":
            formato, trovati = "SVG", svg(dati)
        elif dati[:2] == b"\xff\xd8":
            formato, trovati = "JPEG", jpeg(dati)
        elif dati[:8] == b"\x89PNG\r\n\x1a\n":
            formato, trovati = "PNG", png(dati)
        elif dati[:4] == b"RIFF" and dati[8:12] == b"WEBP":
            formato, trovati = "WebP", webp(dati)
        elif dati[4:8] == b"ftyp" and dati[8:12] in (b"avif", b"avis"):
            formato, trovati = "AVIF", avif(dati)
        else:
            formato, trovati = "?", ["formato che non riconosco"]
        if formato != "SVG" and not any("C2PA" in t for t in trovati) and any(e in dati for e in C2PA):
            trovati.append("C2PA")
        visti[formato] = visti.get(formato, 0) + 1
        if trovati:
            print(f"METADATI {nome(p)}: {', '.join(trovati)}")
            problemi += 1
    print(f"Metadati: {sum(visti.values())} immagini ({', '.join(f'{n} {f}' for f, n in sorted(visti.items()))}), "
          f"{problemi} con metadati")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
