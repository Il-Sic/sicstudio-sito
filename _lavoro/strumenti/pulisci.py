"""Toglie i metadati dalle immagini, senza ricodificarle: nei JPEG i blocchi EXIF e XMP (APP1) e IPTC (APP13), nei PNG
i blocchi eXIf, iTXt, tEXt e zTXt, nei WebP (dal 7/11) i blocchi EXIF e XMP. Il profilo dei colori (ICC) resta. Poi si
controlla con controlli/exif.py. Un AVIF non lo tocca: le copie delle schermate le rifà strumenti/schermate.py, che
non scrive metadati.

    python3 -I _lavoro/strumenti/pulisci.py <immagine> [<immagine> …]
"""
import pathlib, struct, sys


def jpeg(dati):
    fuori = bytearray(dati[:2])
    i = 2
    while i + 4 <= len(dati) and dati[i] == 0xFF:
        marca = dati[i + 1]
        if marca == 0xDA:  # da qui in poi i dati dell'immagine: si copiano così come sono
            break
        lung = struct.unpack(">H", dati[i + 2:i + 4])[0]
        blocco = dati[i:i + 2 + lung]
        corpo = blocco[4:]
        togli = (marca == 0xE1 and (corpo.startswith(b"Exif") or b"ns.adobe.com/xap" in corpo)) or marca == 0xED
        if not togli:
            fuori += blocco
        i += 2 + lung
    fuori += dati[i:]
    return bytes(fuori)


def png(dati):
    fuori = bytearray(dati[:8])
    i = 8
    while i + 8 <= len(dati):
        lung, tipo = struct.unpack(">I4s", dati[i:i + 8])
        blocco = dati[i:i + 12 + lung]
        if tipo not in (b"eXIf", b"iTXt", b"tEXt", b"zTXt"):
            fuori += blocco
        i += 12 + lung
    return bytes(fuori)


def webp(dati):
    """Toglie i blocchi EXIF e XMP del RIFF, spegne i loro segni nel blocco VP8X e rifà la lunghezza del RIFF."""
    blocchi = []
    i = 12
    while i + 8 <= len(dati):
        lung = struct.unpack("<I", dati[i + 4:i + 8])[0]
        blocco = bytearray(dati[i:i + 8 + lung + (lung & 1)])
        if blocco[:4] == b"VP8X":
            blocco[8] &= ~(0x08 | 0x04) & 0xFF     # i segni «c'è EXIF» e «c'è XMP»
        if blocco[:4] not in (b"EXIF", b"XMP "):
            blocchi.append(bytes(blocco))
        i += 8 + lung + (lung & 1)
    corpo = b"WEBP" + b"".join(blocchi)
    return b"RIFF" + struct.pack("<I", len(corpo)) + corpo


for nome in sys.argv[1:]:
    p = pathlib.Path(nome)
    dati = p.read_bytes()
    if dati[:2] == b"\xff\xd8":
        nuovi = jpeg(dati)
    elif dati[:8] == b"\x89PNG\r\n\x1a\n":
        nuovi = png(dati)
    elif dati[:4] == b"RIFF" and dati[8:12] == b"WEBP":
        nuovi = webp(dati)
    else:
        print(f"{p}: non è JPEG, PNG o WebP, lasciata com'è (un AVIF si rifà con strumenti/schermate.py)")
        continue
    p.write_bytes(nuovi)
    print(f"{p}: {len(dati) // 1024} → {len(nuovi) // 1024} KB")
