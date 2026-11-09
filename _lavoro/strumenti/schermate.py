"""Le copie leggere delle schermate di Argonauta: AVIF e WebP in tre larghezze, per <picture> con srcset e sizes.

Per ogni schermata usata nelle pagine (img/schermate/<nome>-chiaro.jpg e -scuro.jpg) scrive in img/schermate/
<nome>-<tema>-400 e -680, larghe 400 e 680 px, e <nome>-<tema>, larga come il JPEG (870 px, la mappa 780), ognuna in
.avif e in .webp. Il JPEG non si tocca: resta la riserva per chi non legge né AVIF né WebP.

Le larghezze vengono dalle misure del 7/11 (_lavoro/prove/larghezze-schermate.html): nella pagina una schermata è
larga al massimo 340 px; 400 basta agli schermi normali, 680 (2 × 340) a quelli doppi del computer e dell'iPad, quella
del JPEG ai telefoni (3×, circa 800 px).

Le copie si fanno dal PNG originale del giro di screenshot dell'app (_lavoro/riferimenti/schermate/<tema>-<origine>.png,
vedi ORIGINI), che è senza perdite: rifatte dal JPEG ne copierebbero i difetti intorno alle lettere. Se il PNG non c'è,
si fanno dal JPEG e lo script lo dice.

Niente metadati: né EXIF né XMP né profilo ICC. Il JPEG non ha profilo, quindi è sRGB, come le copie: nel WebP lo dice
l'assenza del profilo, nell'AVIF il colore nclx 1/13/6 (sRGB) che scrive libavif. Alla fine le impronte (sha-256) del
JPEG e delle copie vanno in schermate.json, qui accanto: controlli/schermate.py le confronta e avvisa se un JPEG è
cambiato e le sue copie no.

Serve Pillow con AVIF, nell'ambiente di _lavoro (una volta sola, dalla cartella del sito):
    python3 -m venv _lavoro/ambiente
    _lavoro/ambiente/bin/pip install pillow

Poi, dalla cartella del sito:
    _lavoro/ambiente/bin/python -I _lavoro/strumenti/schermate.py            tutte quelle usate nelle pagine
    _lavoro/ambiente/bin/python -I _lavoro/strumenti/schermate.py scheda     solo quelle date, in chiaro e in scuro
e infine, se le larghezze sono cambiate o la schermata è nuova, le righe <source> nelle pagine:
    python3 -I _lavoro/strumenti/schermata.py --pagine
"""
import hashlib, io, json, pathlib, re, sys

from PIL import Image, features

SITO = pathlib.Path(__file__).resolve().parents[2]
CARTELLA = SITO / "img" / "schermate"
ORIGINALI = SITO / "_lavoro" / "riferimenti" / "schermate"
REGISTRO = pathlib.Path(__file__).with_name("schermate.json")

# Da quale PNG del giro c3-dopo (4/11) viene ogni schermata: <tema>-<origine>.png. Una schermata nuova si aggiunge qui,
# con lo stesso PNG da cui si fa il JPEG (COME-SI-AGGIORNA, §7).
ORIGINI = {
    "argo": "40-argo-cinque-rotte",
    "diario": "16-diario-completo",
    "equipaggio": "15-equipaggio",
    "leggenda": "08-leggenda",
    "orfeo": "15-equipaggio-orfeo",
    "prima-di-partire": "12-rotta-prima-di-partire-consigli",
    "rotta": "05-anteprima",
    "scheda": "21-atlante-aquila-dati",
    "sicurezza": "12-sicurezza",
}

# Le larghezze piccole; la grande è quella del JPEG.
LARGHEZZE = (400, 680)

# La qualità (AVIF, WebP), scelta a occhio il 7/11 su ritagli ingranditi delle scritte più piccole e chiare (i crediti
# della foto nella scheda, il timbro, i crediti della mappa, il testo bianco sul nero): con queste le lettere restano
# nette come nel PNG, più del JPEG di oggi. Nella copia da 400 le lettere sono di pochi pixel: lì un po' di più.
QUALITA = {400: (60, 85), 680: (50, 80), "grande": (50, 80)}
AVIF = {"subsampling": "4:4:4", "speed": 2}    # 4:4:4: il colore resta pieno intorno alle scritte colorate
WEBP = {"method": 6}


def usate():
    """I nomi delle schermate che le pagine del sito mostrano (dal JPEG chiaro dell'<img>)."""
    nomi = set()
    for p in SITO.rglob("*.html"):
        if {"_lavoro", ".git"} & set(p.relative_to(SITO).parts):
            continue
        nomi |= set(re.findall(r'src="/img/schermate/([a-z0-9-]+)-chiaro\.jpg"', p.read_text(encoding="utf-8")))
    return sorted(nomi)


def impronta(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sorgente(nome, tema, jpeg):
    """L'immagine da cui fare le copie: il PNG originale se c'è, se no il JPEG."""
    png = ORIGINALI / f"{tema}-{ORIGINI[nome]}.png" if nome in ORIGINI else None
    if png and png.exists():
        im, origine = Image.open(png), png
    else:
        print(f"  {nome}-{tema}: il PNG originale non c'è, le copie vengono dal JPEG")
        im, origine = Image.open(jpeg), jpeg
    im = im.convert("RGB")
    im.info = {}                                   # niente EXIF, XMP o profilo da portarsi dietro
    return im, origine


def copie(nome, tema):
    jpeg = CARTELLA / f"{nome}-{tema}.jpg"
    with Image.open(jpeg) as j:
        W, H = j.size
    im, origine = sorgente(nome, tema, jpeg)
    voce = {"jpeg": impronta(jpeg), "origine": str(origine.relative_to(SITO)), "copie": {}}
    pesi = []
    for w in [x for x in LARGHEZZE if x < W] + [W]:
        h = round(H * w / W)
        ridotta = im if im.size == (w, h) else im.resize((w, h), Image.Resampling.LANCZOS)
        ridotta.info = {}
        q_avif, q_webp = QUALITA[w if w != W else "grande"]
        coda = "" if w == W else f"-{w}"
        for formato, opzioni in (("avif", dict(AVIF, quality=q_avif)), ("webp", dict(WEBP, quality=q_webp))):
            dati = io.BytesIO()
            ridotta.save(dati, formato.upper(), icc_profile=None, **opzioni)
            p = CARTELLA / f"{nome}-{tema}{coda}.{formato}"
            p.write_bytes(dati.getvalue())
            voce["copie"][p.name] = impronta(p)
            pesi.append(f"{p.name} {p.stat().st_size / 1024:.0f}")
    print(f"  {nome}-{tema} (da {origine.name}, JPEG {jpeg.stat().st_size / 1024:.0f} KB): " + ", ".join(pesi) + " KB")
    return voce


def main():
    if not features.check("avif"):
        sys.exit("Questo Pillow non scrive AVIF: usa _lavoro/ambiente/bin/python (vedi in cima al file).")
    nomi = sys.argv[1:] or usate()
    registro = json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {}
    for nome in nomi:
        for tema in ("chiaro", "scuro"):
            if not (CARTELLA / f"{nome}-{tema}.jpg").exists():
                sys.exit(f"Manca img/schermate/{nome}-{tema}.jpg")
            registro[f"{nome}-{tema}"] = copie(nome, tema)
    REGISTRO.write_text(json.dumps(registro, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Copie fatte per {len(nomi)} schermate; impronte in {REGISTRO.relative_to(SITO)}")


if __name__ == "__main__":
    main()
