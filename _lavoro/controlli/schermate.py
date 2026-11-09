"""Le schermate con le copie AVIF e WebP (dal 7/11; le fanno strumenti/schermate.py e strumenti/schermata.py).

In ogni <picture> con una schermata di img/schermate:
- le <source> scure (media prefers-color-scheme: dark) vengono prima delle chiare: il browser prende la prima che va;
- ci sono AVIF e WebP, in scuro e in chiaro, con type, srcset con le larghezze (w) e sizes, uguale in tutte;
- ogni file di un srcset c'è, è del formato del suo type, è largo quanto dice la sua w ed è in proporzione con width e
  height dell'<img> (al pixel); scuro e chiaro, AVIF e WebP hanno le stesse larghezze, e la più grande è quella
  dell'<img>.
Poi i file:
- il JPEG e le copie sono quelli registrati in strumenti/schermate.json quando le copie sono state fatte: se un JPEG
  è cambiato dopo, le copie mostrano ancora la schermata vecchia e vanno rifatte con strumenti/schermate.py;
- nessuna copia in img/schermate senza una pagina che la usi.
"""
import hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, LAVORO, file_del_sito, leggi, misure, nome, pagine

REGISTRO = LAVORO / "strumenti" / "schermate.json"
FORMATI = {"image/avif": "avif", "image/webp": "webp"}
SCURO = "(prefers-color-scheme: dark)"


def figure(p):
    """Le <picture> di una pagina: (riga, attributi delle <source>, attributi dell'<img>)."""
    figure, aperta = [], None
    for n, a, riga in leggi(p).tag:
        if n == "picture":
            aperta = (riga, [])
        elif n == "source" and aperta:
            aperta[1].append(a)
        elif n == "img" and aperta:
            figure.append((aperta[0], aperta[1], a))
            aperta = None
    return figure


def impronta(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def controlla(p, riga, sorgenti, img, usate, registro):
    problemi = []
    dove = f"{nome(p)} riga {riga}"
    lw, lh = int(img.get("width", 0)), int(img.get("height", 0))
    scure = [s.get("media") == SCURO for s in sorgenti]
    if scure != sorted(scure, reverse=True):
        problemi.append(f"{dove}: una <source> chiara prima di una scura")
    jpeg = [img["src"]] + [s["srcset"] for s in sorgenti if "type" not in s]
    larghezze, sizes = {}, set()
    for s in sorgenti:
        if "type" not in s:
            continue
        formato = FORMATI.get(s["type"])
        if not formato:
            problemi.append(f"{dove}: type sconosciuto {s['type']}")
            continue
        tema = "scuro" if s.get("media") == SCURO else "chiaro"
        if not s.get("sizes"):
            problemi.append(f"{dove}: <source {formato} {tema}> senza sizes")
        sizes.add(s.get("sizes"))
        insieme = larghezze.setdefault((tema, formato), [])
        for pezzo in s.get("srcset", "").split(","):
            url, *descrittore = pezzo.split()
            f = SITO / url.lstrip("/")
            usate.add(f)
            if not descrittore or not descrittore[0].endswith("w"):
                problemi.append(f"{dove}: {url} senza la larghezza (w)")
                continue
            w = int(descrittore[0][:-1])
            insieme.append(w)
            letto = misure(f) if f.exists() else None
            if not letto:
                problemi.append(f"{dove}: {url} non c'è o non si legge")
                continue
            if letto[0] != formato:
                problemi.append(f"{dove}: {url} è {letto[0]}, non {formato}")
            if letto[1] != w:
                problemi.append(f"{dove}: {url} è largo {letto[1]} px, non {w}")
            if lw and abs(letto[2] - letto[1] * lh / lw) > 1:
                problemi.append(f"{dove}: {url} è {letto[1]}×{letto[2]}, fuori proporzione con {lw}×{lh}")
    for tema in ("scuro", "chiaro"):
        for formato in ("avif", "webp"):
            if (tema, formato) not in larghezze:
                problemi.append(f"{dove}: manca la <source> {formato.upper()} {tema}")
    serie = {tuple(sorted(v)) for v in larghezze.values()}
    if len(serie) > 1:
        problemi.append(f"{dove}: larghezze diverse fra le copie: {sorted(serie)}")
    tutte = [w for v in larghezze.values() for w in v]
    if tutte and max(tutte) != lw:
        problemi.append(f"{dove}: la copia più grande non è larga come l'<img> ({lw} px)")
    if len(sizes) > 1:
        problemi.append(f"{dove}: sizes diversi nella stessa figura")
    # Le copie sono state fatte da questo JPEG, e sono ancora quelle?
    for url in jpeg:
        f = SITO / url.lstrip("/")
        voce = registro.get(f.stem)
        if not voce:
            problemi.append(f"{dove}: {f.name} non è in {REGISTRO.name}: fare le copie con strumenti/schermate.py")
        elif f.exists() and impronta(f) != voce["jpeg"]:
            problemi.append(f"{dove}: {f.name} è cambiato dopo le sue copie: rifarle con strumenti/schermate.py")
    return problemi


def main():
    registro = json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {}
    impronte = {c: h for voce in registro.values() for c, h in voce["copie"].items()}
    problemi, usate, viste = [], set(), 0
    for p in pagine():
        for riga, sorgenti, img in figure(p):
            if img.get("src", "").startswith("/img/schermate/"):
                viste += 1
                problemi += controlla(p, riga, sorgenti, img, usate, registro)
    for f in file_del_sito(".avif", ".webp"):
        if f.parent.name != "schermate":
            continue
        if f not in usate:
            problemi.append(f"{nome(f)}: copia che nessuna pagina usa")
        if impronte.get(f.name) != impronta(f):
            problemi.append(f"{nome(f)}: non è la copia registrata in {REGISTRO.name}: rifarla con strumenti/schermate.py")
    for x in problemi:
        print(x)
    print(f"Schermate: {viste} figure, {len(usate)} copie usate, {len(problemi)} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
