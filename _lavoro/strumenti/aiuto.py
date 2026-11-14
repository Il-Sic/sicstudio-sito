"""Scrive le due pagine «Aiuto e domande», italiana e inglese, dai testi di aiuto.toml: l'apertura con l'indice, i
gruppi di domande con il titolo a lato, le parole di bordo che si aprono nel testo (popover, senza JavaScript) e il
glossario in fondo. Il foglio di ogni parola sta subito dopo il suo pulsante, con il nome della parola: chi usa un
lettore di schermo lo trova lì, e non in fondo alla pagina. Riscrive tutto ciò che sta dentro <main>: una correzione fatta a mano nella pagina si perde, le
parole si cambiano in aiuto.toml.

    python3 -I _lavoro/strumenti/aiuto.py          tutte e due le pagine
    python3 -I _lavoro/strumenti/aiuto.py it|en    una sola

Esce con 1, senza scrivere, se nella pagina non trova <main id="contenuto"> o se nei testi manca una voce.
(Fino all'11/11 i testi venivano dalla copia del sito del 6/11, in online-6-11, e le domande nuove stavano qui dentro.)
"""
import html, pathlib, re, sys, tomllib

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
FILE = {"it": "argonauta/aiuto/index.html", "en": "en/argonauta/help/index.html"}
# Il poema di Apollonio Rodio è un'opera citata: <cite> (8/11).
OPERA = {"it": "Argonautiche", "en": "Argonautica"}
PRIVACY = re.sub(r"\s+", " ", (SITO / "_lavoro" / "riferimenti" / "privacy-argonauta.md").read_text(encoding="utf-8"))


def ident(termine):
    s = html.unescape(re.sub("<[^>]+>", "", termine)).lower()
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u"), ("'", " "), ("’", " ")):
        s = s.replace(a, b)
    return "parola-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def rientra(testo, capoverso, seguito):
    """Le righe di un testo con il rientro della pagina: quelle che aprono un capoverso (<p…) e le altre."""
    righe = [r.strip() for r in testo.strip().split("\n")]
    return "\n".join(" " * (capoverso if r.startswith("<p") else seguito) + r for r in righe if r)


def apostrofi(codice):
    """' diventa ’ nel testo (non nei tag), tranne dentro le citazioni «…» o “…” che vengono dalla privacy."""
    pezzi = re.split(r"(<[^>]+>|«[^»]*»|“[^”]*”)", codice)
    for i, pezzo in enumerate(pezzi):
        if not pezzo or pezzo.startswith("<"):
            continue
        # Solo le frasi intere della privacy: «Durante l'uso», da solo, è il nome di un permesso (come apostrofi.py).
        if pezzo[0] in "«“" and len(pezzo) > 22 and re.sub(r"\s+", " ", pezzo[1:-1]) in PRIVACY:
            continue
        pezzi[i] = pezzo.replace("'", "’")
    return "".join(pezzi)


def pagina(testi, lingua):
    """Il contenuto di <main> in una lingua, e le parole di bordo che nelle risposte non compaiono mai."""
    def t(tabella, chiave):
        return tabella[chiave][lingua]

    voci = testi["parole"]["voce"]
    # Ogni parola di bordo diventa un pulsante la prima volta che compare in una risposta; i modelli più lunghi si
    # provano per primi («viaggio di Argo» prima di «Argo»).
    da_cercare = sorted(((t(v, "parola"), t(v, "cerca")) for v in voci), key=lambda coppia: -len(coppia[1]))
    usate = set()
    capo, parole = testi["pagina"], testi["parole"]
    spiegate = [(t(v, "parola"), rientra(t(v, "vuol-dire"), 10, 10).lstrip()) for v in voci]

    def foglio(parola):
        """Il foglio che si apre sulla parola: elementi di frase, perché sta nel capoverso della risposta. role="group"
        perché uno span possa avere il nome della parola (aria-labelledby)."""
        i, spiega = ident(parola), " ".join(dict(spiegate)[parola].split())
        return (f'<span class="definizione" id="{i}" popover role="group" aria-labelledby="{i}-termine">'
                f'<span class="definizione-termine" id="{i}-termine">{parola}</span>'
                f'<span class="definizione-testo">{spiega}</span>'
                f'<button type="button" class="chiudi-definizione" popovertarget="{i}" popovertargetaction="hide">'
                f'{t(capo, "chiudi")}</button></span>')

    def con_i_fogli(testo):
        """Al posto dei segni lasciati da avvolgi(), i fogli delle parole."""
        return re.sub("\ue000(\\d+)\ue001", lambda m: foglio(da_cercare[int(m.group(1))][0]), testo)

    def avvolgi(risposta):
        """Mette il pulsante della parola alla sua prima comparsa, fuori dai link e dai tag, e dopo il pulsante un segno
        con il numero della parola: il suo foglio lo mette con_i_fogli(), così il testo del foglio non entra nella
        ricerca delle parole che vengono dopo."""
        pezzi = re.split(r"(<a\b.*?</a>|<[^>]+>)", risposta, flags=re.S)
        for i, pezzo in enumerate(pezzi):
            if not pezzo or pezzo.startswith("<"):
                continue
            for n, (parola, modello) in enumerate(da_cercare):
                if parola in usate:
                    continue
                m = re.search(modello, pezzo)
                if m:
                    usate.add(parola)
                    bottone = f'<button type="button" class="parola" popovertarget="{ident(parola)}">{m.group(0)}</button>'
                    segno = f"\ue000{n}\ue001"
                    dopo = re.match(r"[,.;:!?»”)]+", pezzo[m.end():])
                    if dopo:  # la virgola o il punto restano sulla stessa riga della parola; il foglio fuori, a capo libero
                        bottone = f'<span class="parola-legata">{bottone}{dopo.group(0)}</span>'
                        pezzo = pezzo[:m.start()] + bottone + segno + pezzo[m.end() + len(dopo.group(0)):]
                    else:
                        pezzo = pezzo[:m.start()] + bottone + segno + pezzo[m.end():]
            pezzi[i] = pezzo
        return "".join(pezzi)

    indice = [(t(g, "id"), t(g, "titolo")) for g in testi["gruppo"]] + [(t(parole, "id"), t(parole, "titolo"))]
    righe = ['<header class="apertura-aiuto fascia">',
             f'  <p class="occhiello">{t(capo, "occhiello")}</p>',
             f'  <h1>{t(capo, "titolo")}</h1>',
             f'  <p class="sottotitolo misura">{rientra(t(capo, "introduzione"), 10, 10).lstrip()}</p>',
             f'  <nav class="indice-mito" aria-label="{t(capo, "indice")}">',
             '    <ol>' + "".join(f'<li><a href="#{i}">{titolo}</a></li>' for i, titolo in indice) + '</ol>',
             '  </nav>', '</header>', '']
    for n, gruppo in enumerate(testi["gruppo"]):
        classe = "domande-gruppo fascia-stretta" + (" tavolo" if n % 2 else "")
        righe += [f'<section class="{classe}" id="{t(gruppo, "id")}" aria-labelledby="{t(gruppo, "id-del-titolo")}">',
                  '  <div class="domande-riga">',
                  f'    <h2 class="titolo-sezione" id="{t(gruppo, "id-del-titolo")}">{t(gruppo, "titolo")}</h2>',
                  '    <div class="domande">']
        for domanda in gruppo["domanda"]:
            righe += ['      <details class="domanda">',
                      f'          <summary>{t(domanda, "chiede")}</summary>',
                      '          <div class="risposta">',
                      con_i_fogli(avvolgi(rientra(t(domanda, "risponde"), 12, 14))),
                      '          </div>',
                      '        </details>']
        righe += ['    </div>', '  </div>', '</section>', '']
    righe += [f'<section class="parole-bordo fascia-stretta" id="{t(parole, "id")}" aria-labelledby="{t(parole, "id-del-titolo")}">',
              '  <div class="capo">',
              f'    <h2 class="titolo-sezione" id="{t(parole, "id-del-titolo")}">{t(parole, "titolo")}</h2>',
              f'    <p class="sottotitolo misura">{t(parole, "nota")}</p>',
              '  </div>',
              '  <dl class="glossario">']
    righe += [f'    <div><dt>{parola}</dt><dd>{spiega}</dd></div>' for parola, spiega in spiegate]
    righe += ['  </dl>', '</section>']
    righe = [re.sub(rf"\b{OPERA[lingua]}\b", f"<cite>{OPERA[lingua]}</cite>", apostrofi(r)) for r in righe]
    return "\n".join(righe), [parola for parola, _ in spiegate if parola not in usate]


def main():
    lingue = [a for a in sys.argv[1:] if a in FILE] or list(FILE)
    try:
        testi = tomllib.loads((QUI / "aiuto.toml").read_text(encoding="utf-8"))
        contenuti = {lingua: pagina(testi, lingua) for lingua in lingue}
    except (KeyError, tomllib.TOMLDecodeError) as errore:
        print(f"aiuto.toml: manca una voce, o c'è un errore di scrittura: {errore}")
        return 1
    problemi = 0
    for lingua, (contenuto, mai) in contenuti.items():
        p = SITO / FILE[lingua]
        testo = p.read_text(encoding="utf-8")
        nuovo, quante = re.subn(r'<main id="contenuto"[^>]*>.*?</main>', lambda m: '<main id="contenuto" class="pagina-aiuto">\n\n' + contenuto + "\n\n</main>",
                                testo, flags=re.S)
        if quante != 1:
            print(f'{FILE[lingua]}: <main id="contenuto"> c\'è {quante} volte invece di una')
            problemi += 1
            continue
        if nuovo != testo:
            p.write_text(nuovo, encoding="utf-8")
        domande = sum(len(g["domanda"]) for g in testi["gruppo"])
        print(f"{FILE[lingua]}: {domande} domande, {len(testi['parole']['voce']) - len(mai)} parole di bordo nel testo; mai usate: {', '.join(mai) or 'nessuna'}")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
