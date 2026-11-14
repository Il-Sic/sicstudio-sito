"""Scrive il codice di una schermata dell'app in una cornice di telefono, in chiaro e in scuro, con le misure vere.

    python3 -I _lavoro/strumenti/schermata.py <nome> "<testo alternativo>" ["<didascalia>"]
    python3 -I _lavoro/strumenti/schermata.py --pagine [<pagina> …]

Dal 7/11 ogni schermata ha anche le copie AVIF e WebP in tre larghezze (le fa strumenti/schermate.py): il <picture>
le offre per prime, con srcset e sizes, e il JPEG resta la riserva. Con --pagine riscrive le righe <source> delle
schermate già nelle pagine (tutte, o quelle date), dai file che ci sono in img/schermate: va lanciato quando le copie
cambiano larghezza o una schermata le ha per la prima volta. L'<img> resta com'è, con il suo testo alternativo.
"""
import functools, pathlib, re, sys

SITO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SITO / "_lavoro" / "controlli"))
import comune  # noqa: E402
CARTELLA = SITO / "img" / "schermate"
SCURO = "(prefers-color-scheme: dark)"

# Quanto è larga una schermata nella pagina, per sizes (misurato il 7/11 con _lavoro/prove/larghezze-schermate.html,
# da 320 a 1920 px). In style.css il telefono è largo min(19rem, 72vw), con 0,5rem di cornice per lato, e la radice è
# di 17 px: l'immagine è larga 72vw − 17px fino a 448 px di finestra, poi 306 px. Nei «momenti» della giornata, dai
# 56rem in su, e con almeno 30rem di altezza (14/11), il telefono segue l'altezza della finestra fino a 21rem: l'immagine
# è al massimo 340 px. Più in basso, i telefoni in orizzontale, resta in colonna come al telefono.
SIZES = "(min-width: 449px) 306px, calc(72vw - 17px)"
SIZES_MOMENTO = "(min-width: 56rem) and (min-height: 30rem) 340px, " + SIZES

# Una figura già nella pagina: <picture>, le righe <source>, l'<img> della schermata chiara, </picture>.
FIGURA = re.compile(r'(?P<a>[ \t]*)<picture>\n(?:[ \t]*<source [^>]*>\n)*(?P<b>[ \t]*)'
                    r'(?P<img><img src="/img/schermate/(?P<nome>[a-z0-9-]+)-chiaro\.jpg"[^>]*>)\n(?P<c>[ \t]*)</picture>')


@functools.cache
def misure(p):
    """Larghezza e altezza di un'immagine, lette dal file come fanno i controlli (prima le chiedeva a sips, che c'è
    solo sul Mac: così lo script gira anche su GitHub, dentro costruisci.py --verifica)."""
    m = comune.misure(p)
    if m is None:
        sys.exit(f"schermata.py: non capisco le misure di {p}")
    return m[1], m[2]


def candidati(nome, tema, formato):
    """Le copie <nome>-<tema>[-<larghezza>].<formato> che ci sono, dalla più stretta, per srcset."""
    forma = re.compile(rf"{re.escape(nome)}-{tema}(-\d+)?\.{formato}")
    coppie = sorted((misure(p)[0], p.name) for p in CARTELLA.glob(f"{nome}-{tema}*.{formato}") if forma.fullmatch(p.name))
    return ", ".join(f"/img/schermate/{n} {w}w" for w, n in coppie)


def sorgenti(nome, sizes):
    """Le righe <source>: il browser prende la prima che va bene, quindi prima le scure (con media), poi le chiare,
    e in ognuna prima AVIF, poi WebP. Il JPEG scuro resta com'era; il chiaro è l'<img>."""
    righe = []
    for tema, media in (("scuro", f' media="{SCURO}"'), ("chiaro", "")):
        for tipo, formato in (("image/avif", "avif"), ("image/webp", "webp")):
            srcset = candidati(nome, tema, formato)
            if srcset:
                righe.append(f'<source type="{tipo}"{media} srcset="{srcset}" sizes="{sizes}">')
        if tema == "scuro":
            righe.append(f'<source srcset="/img/schermate/{nome}-scuro.jpg"{media}>')
    return righe


def sizes_per(testo, posizione):
    """Il sizes di una schermata a quel punto della pagina: dentro un «momento» della giornata o fuori."""
    prima = testo[:posizione]
    return SIZES_MOMENTO if prima.rfind('<article class="momento') > prima.rfind("</article>") else SIZES


def codice(nome, alt, didascalia=None, rientro="      ", sizes=SIZES):
    w, h = misure(CARTELLA / f"{nome}-chiaro.jpg")
    righe = [
        f'<figure class="schermata">',
        f'  <div class="telefono">',
        f'    <picture>',
        *(f'      {s}' for s in sorgenti(nome, sizes)),
        f'      <img src="/img/schermate/{nome}-chiaro.jpg" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">',
        f'    </picture>',
        f'  </div>',
    ]
    if didascalia:
        righe.append(f'  <figcaption>{didascalia}</figcaption>')
    righe.append('</figure>')
    return "\n".join(rientro + r for r in righe)


def aggiorna(pagina):
    """Riscrive le righe <source> delle schermate di una pagina; dice quante figure ha visto."""
    testo = pagina.read_text(encoding="utf-8")

    def nuova(m):
        righe = [m["a"] + "<picture>", *(m["b"] + s for s in sorgenti(m["nome"], sizes_per(testo, m.start()))),
                 m["b"] + m["img"], m["c"] + "</picture>"]
        return "\n".join(righe)

    nuovo, n = FIGURA.subn(nuova, testo)
    if nuovo != testo:
        pagina.write_text(nuovo, encoding="utf-8")
    return n, nuovo != testo


def pagine():
    for p in sorted(SITO.rglob("*.html")):
        if not {"_lavoro", ".git"} & set(p.relative_to(SITO).parts):
            yield p


if __name__ == "__main__":
    if sys.argv[1:2] == ["--pagine"]:
        for p in [pathlib.Path(x).resolve() for x in sys.argv[2:]] or pagine():
            n, cambiata = aggiorna(p)
            if n:
                print(f"{p.relative_to(SITO)}: {n} schermate, {'riscritte' if cambiata else 'già a posto'}")
    else:
        print(codice(*sys.argv[1:]))
