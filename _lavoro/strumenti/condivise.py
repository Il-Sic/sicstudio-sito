"""Le parti uguali in ogni pagina: la testa (meta, privacy, icone, anteprima), l'intestazione e il colophon.

Le pagine sono HTML normale e si possono cambiare a mano. Questo strumento riscrive solo quello che sta fra i
segni <!-- testa:inizio --> … <!-- testa:fine -->, <!-- testata:inizio --> … <!-- testata:fine --> e
<!-- piede:inizio --> … <!-- piede:fine -->, con i dati di PAGINE qui sotto.

    python3 -I _lavoro/strumenti/condivise.py            aggiorna tutte le pagine
    python3 -I _lavoro/strumenti/condivise.py --nuove    crea anche le pagine che mancano, vuote

Le pagine sono di due case: quelle dello studio (home e studio), con il menu dello studio, e quelle di Argonauta, con
il menu di Argonauta e il ritorno allo studio. La 404 non ha menu.
"""
import html, pathlib, re, sys

SITO = pathlib.Path(__file__).resolve().parents[2]
DOMINIO = "https://sicstudio.app"
# Il numero di Argonauta sull'App Store (solo le cifre). Vuoto finché l'app non è uscita; da quel giorno le pagine di
# Argonauta hanno in testa la riga con cui Safari, su iPhone e iPad, mostra la fascia «Apri nell'App Store» (lo
# Smart App Banner di Apple: funziona senza script).
APP_STORE = ""
CSP = ("default-src 'self'; img-src 'self' data:; script-src 'none'; object-src 'none'; "
       "base-uri 'none'; form-action 'none'")

# file: lingua, percorso, percorso nell'altra lingua, casa («studio», «argonauta» o None), voce del menu, titolo,
# descrizione
PAGINE = {
    "index.html": dict(
        lingua="it", percorso="/", altro="/en/", casa="studio", voce="progetti", titolo="Sic Studio",
        descrizione="Sic Studio è lo studio di Vincenzo Siciliano, in Calabria. Fa app e giochi, con cura e con le "
                    "fonti."),
    "studio/index.html": dict(
        lingua="it", percorso="/studio/", altro="/en/studio/", casa="studio", voce="studio",
        titolo="Lo studio · Sic Studio",
        descrizione="Chi c’è dietro Sic Studio, perché fa Argonauta, da dove viene il nome e come lavora. Con il "
                    "giornale dello studio."),
    "argonauta/index.html": dict(
        lingua="it", percorso="/argonauta/", altro="/en/argonauta/", casa="argonauta", voce="argonauta",
        titolo="Argonauta · Sic Studio",
        descrizione="Argonauta è un’app per esplorare, divertirsi e sognare: una giornata di rotte, schede da "
                    "collezionare e la nave Argo che cresce con te. Qui c’è anche il supporto."),
    "argonauta/il-mito/index.html": dict(
        lingua="it", percorso="/argonauta/il-mito/", altro="/en/argonauta/the-myth/", casa="argonauta", voce="mito",
        titolo="Il mito di Argo · Argonauta",
        descrizione="Perché la guida di Argonauta si chiama Argo: la nave che parlava, gli eroi a bordo e il viaggio "
                    "fino al vello d’oro, con le fonti antiche."),
    "argonauta/aiuto/index.html": dict(
        lingua="it", percorso="/argonauta/aiuto/", altro="/en/argonauta/help/", casa="argonauta", voce="aiuto",
        titolo="Aiuto e domande · Argonauta",
        descrizione="Le risposte alle domande su Argonauta: la rete, la posizione, le rotte, l’Atlante, Argo, le "
                    "emergenze e i dati. E le parole di bordo."),
    "argonauta/privacy/index.html": dict(
        lingua="it", percorso="/argonauta/privacy/", altro="/argonauta/privacy/#en", casa="argonauta",
        voce="privacy", titolo="Argonauta: informativa sulla privacy",
        descrizione="Argonauta non raccoglie dati personali. Non c'è un account. Non ci sono statistiche, pubblicità o "
                    "tracciamento."),
    "404.html": dict(
        lingua="it", percorso=None, altro=None, casa=None, voce=None, titolo="Fuori rotta · Sic Studio",
        descrizione="Questa pagina non c’è. This page doesn’t exist."),
    "en/index.html": dict(
        lingua="en", percorso="/en/", altro="/", casa="studio", voce="progetti", titolo="Sic Studio",
        descrizione="Sic Studio is Vincenzo Siciliano’s studio, in Calabria. It makes apps and games, with care and "
                    "with sources."),
    "en/studio/index.html": dict(
        lingua="en", percorso="/en/studio/", altro="/studio/", casa="studio", voce="studio",
        titolo="The studio · Sic Studio",
        descrizione="Who is behind Sic Studio, why it makes Argonauta, where the name comes from and how it works. "
                    "With the studio’s logbook."),
    "en/argonauta/index.html": dict(
        lingua="en", percorso="/en/argonauta/", altro="/argonauta/", casa="argonauta", voce="argonauta",
        titolo="Argonauta · Sic Studio",
        descrizione="Argonauta is an app to explore, play and dream: a day of routes, cards to collect and the ship "
                    "Argo that grows with you. Support is here too."),
    "en/argonauta/the-myth/index.html": dict(
        lingua="en", percorso="/en/argonauta/the-myth/", altro="/argonauta/il-mito/", casa="argonauta", voce="mito",
        titolo="The myth of Argo · Argonauta",
        descrizione="Why Argonauta’s guide is called Argo: the ship that spoke, the heroes aboard and the voyage to "
                    "the golden fleece, with the ancient sources."),
    "en/argonauta/help/index.html": dict(
        lingua="en", percorso="/en/argonauta/help/", altro="/argonauta/aiuto/", casa="argonauta", voce="aiuto",
        titolo="Help and questions · Argonauta",
        descrizione="Answers to questions about Argonauta: the network, location, routes, the Atlas, Argo, "
                    "emergencies and your data. And the words on board."),
}

PAROLE = {
    "it": {
        "salta": "Vai al contenuto", "menu": "Menu", "chiudi": "Chiudi", "menu_studio": "Lo studio",
        "menu_argonauta": "Argonauta", "pagine": "Tutte le pagine", "casa": "Sic Studio, la pagina iniziale",
        "altra": "English", "altra_lingua": "en", "luogo": "In Calabria",
        "voci_studio": [("progetti", "Progetti"), ("studio", "Lo studio"), ("argonauta", "Argonauta"),
                        ("contatti", "Contatti")],
        "voci_argonauta": [("mito", "Il mito"), ("aiuto", "Aiuto e domande"), ("privacy", "Privacy"),
                           ("supporto", "Supporto")],
        "colophon": "Composto con i caratteri del tuo dispositivo.",
        "crediti": ("I disegni del sito, con la nave, gli eroi e i paesaggi di Argo, sono provvisori. Le schermate "
                    "vengono dall’app: sulle mappe ci sono i loro crediti."),
        "og_locale": "it_IT",
        "og": {"studio": ("anteprima-logo.jpg", "Il logo di Sic Studio: un sentiero a S pieno di stelle sale tra le colline sotto il cielo che gira, con il nome sotto."),
               "argonauta": ("anteprima.jpg", "La nave Argo sul mare, di giorno.")},
    },
    "en": {
        "salta": "Skip to content", "menu": "Menu", "chiudi": "Close", "menu_studio": "The studio",
        "menu_argonauta": "Argonauta", "pagine": "All pages", "casa": "Sic Studio, home page",
        "altra": "Italiano", "altra_lingua": "it", "luogo": "In Calabria",
        "voci_studio": [("progetti", "Projects"), ("studio", "The studio"), ("argonauta", "Argonauta"),
                        ("contatti", "Contact")],
        "voci_argonauta": [("mito", "The myth"), ("aiuto", "Help and questions"), ("privacy", "Privacy"),
                           ("supporto", "Support")],
        "colophon": "Set in your device’s own typefaces.",
        "crediti": ("The site’s drawings, with the ship, the heroes and Argo’s landscapes, are provisional. The "
                    "screenshots come from the app: the maps show their credits."),
        "og_locale": "en_GB",
        "og": {"studio": ("anteprima-logo.jpg", "The Sic Studio logo: an S-shaped path full of stars climbs between the hills under the turning sky, with the name below."),
               "argonauta": ("anteprima.jpg", "The ship Argo at sea, by day.")},
    },
}

# Il marchio: la S del logo del 13/11/2026, il sentiero a tre tornanti pieno di cielo dal tramonto alla notte, con la
# Via Lattea del Cigno e le sue stelle vere. È un'immagine per tutte le pagine, una per la carta e una per la notte
# (img/marchio-giorno.svg e img/marchio-notte.svg, dalla cartella web/ del kit del logo): <picture> sceglie con il tema
# del sistema, come .solo-giorno e .solo-notte. Le misure sono in style.css (.marchio), quelle del logo del kit.
MARCHIO = ('<picture><source srcset="/img/marchio-notte.svg" media="(prefers-color-scheme: dark)">'
           '<img class="marchio" src="/img/marchio-giorno.svg" alt="" width="54" height="45"></picture>')


ICONA_MENU = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
              '<path d="M4 8.5h16M4 15.5h16"/></svg>')


def percorsi(lingua):
    if lingua == "it":
        return {"home": "/", "progetti": "/#progetti", "studio": "/studio/", "contatti": "#contatti",
                "argonauta": "/argonauta/", "mito": "/argonauta/il-mito/", "aiuto": "/argonauta/aiuto/",
                "privacy": "/argonauta/privacy/", "supporto": "/argonauta/#supporto", "giornale": "/studio/#giornale"}
    return {"home": "/en/", "progetti": "/en/#progetti", "studio": "/en/studio/", "contatti": "#contatti",
            "argonauta": "/en/argonauta/", "mito": "/en/argonauta/the-myth/", "aiuto": "/en/argonauta/help/",
            "privacy": "/argonauta/privacy/#en", "supporto": "/en/argonauta/#support",
            "giornale": "/en/studio/#giornale"}


def e(testo):
    return html.escape(testo).replace("&#x27;", "'")


def testa(file, d):
    lingua, percorso, altro, casa = d["lingua"], d["percorso"], d["altro"], d["casa"]
    righe = [
        '<meta charset="utf-8">',
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">',
        '<meta name="referrer" content="no-referrer">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="theme-color" content="#FAF7F0" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#0C1015" media="(prefers-color-scheme: dark)">',
        f"<title>{e(d['titolo'])}</title>",
        f'<meta name="description" content="{e(d["descrizione"])}">',
    ]
    if APP_STORE and casa == "argonauta":
        righe += [f'<meta name="apple-itunes-app" content="app-id={APP_STORE}">']
    if percorso:
        it, en = (percorso, altro) if lingua == "it" else (altro, percorso)
        righe += [f'<link rel="canonical" href="{DOMINIO}{percorso}">']
        if "#" not in (altro or ""):
            righe += [f'<link rel="alternate" hreflang="it" href="{DOMINIO}{it}">',
                      f'<link rel="alternate" hreflang="en" href="{DOMINIO}{en}">',
                      f'<link rel="alternate" hreflang="x-default" href="{DOMINIO}{it}">']
        p = PAROLE[lingua]
        immagine, alt = p["og"][casa]
        righe += [
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Sic Studio">',
            f'<meta property="og:locale" content="{p["og_locale"]}">',
            f'<meta property="og:title" content="{e(d["titolo"])}">',
            f'<meta property="og:description" content="{e(d["descrizione"])}">',
            f'<meta property="og:url" content="{DOMINIO}{percorso}">',
            f'<meta property="og:image" content="{DOMINIO}/img/{immagine}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{e(alt)}">',
            # Su X l'anteprima grande, come su WhatsApp e iMessage, invece della scheda piccola.
            '<meta name="twitter:card" content="summary_large_image">',
        ]
        if file == "index.html":
            # Il nome del sito nei risultati di Google: i dati strutturati WebSite, solo nella home del dominio
            # (developers.google.com/search/docs/appearance/site-names, letto il 9/11/2026). Sono dati, non uno
            # script: il browser non li esegue e la CSP non li blocca.
            righe += ['<script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebSite", '
                      f'"name": "Sic Studio", "url": "{DOMINIO}/"}}</script>']
    else:
        righe += ['<meta name="robots" content="noindex">']
    righe += [
        '<link rel="icon" href="/favicon.ico" sizes="32x32">',
        '<link rel="icon" href="/img/icona.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="stylesheet" href="/style.css">',
    ]
    return "\n".join(righe)


def voci(d):
    """Le voci del menu della pagina: (chiave, testo, indirizzo)."""
    p, u = PAROLE[d["lingua"]], percorsi(d["lingua"])
    elenco = p["voci_studio"] if d["casa"] == "studio" else p["voci_argonauta"]
    return [(k, t, u[k]) for k, t in elenco]


def al_telefono(h, d):
    """Nel menu del telefono un link a una sezione della stessa pagina ha un «?» vuoto prima del «#» (/?#contatti):
    così la pagina si ricarica e il menu, che è un popover, si chiude. Il menu del computer resta com'è."""
    pagina, segno, sezione = h.partition("#")
    if segno and pagina in ("", d["percorso"]):
        return f'{d["percorso"]}?#{sezione}'
    return h


def testata(file, d):
    lingua, casa = d["lingua"], d["casa"]
    p, u = PAROLE[lingua], percorsi(lingua)
    altra = d["altro"] or ("/en/" if lingua == "it" else "/")

    def lingua_link(h):
        return f'<a href="{h}" hreflang="{p["altra_lingua"]}" lang="{p["altra_lingua"]}">{p["altra"]}</a>'
    righe = [f'<a class="salta" href="#contenuto">{p["salta"]}</a>', f'<header class="testata testata-{casa or "fuori"}">',
             '  <div class="testata-riga">']
    righe.append(f'    <a class="casa" href="{u["home"]}" aria-label="{p["casa"]}">{MARCHIO}<span>Sic Studio</span></a>')
    if casa == "argonauta":
        attuale = ' aria-current="page"' if d["voce"] == "argonauta" else ""
        righe.append(f'    <span class="testata-sep" aria-hidden="true">/</span>'
                     f'<a class="progetto" href="{u["argonauta"]}"{attuale}>Argonauta</a>')
    if casa:
        def lista(classe, telefono=False):
            link = (lambda h: al_telefono(h, d)) if telefono else (lambda h: h)
            r = [f'      <ul class="{classe}">']
            for k, t, h in voci(d):
                attuale = ' aria-current="page"' if k == d["voce"] else ""
                r.append(f'        <li><a href="{link(h)}"{attuale}>{t}</a></li>')
            r.append(f'        <li class="lingua">{lingua_link(link(altra))}</li>')
            r.append('      </ul>')
            return r
        nome_menu = p["menu_studio"] if casa == "studio" else p["menu_argonauta"]
        righe += [f'    <nav class="menu-largo" aria-label="{nome_menu}">'] + lista("menu") + ['    </nav>']
        righe += [
            f'    <button class="apri-menu" type="button" popovertarget="menu-telefono" aria-label="{p["menu"]}">'
            f'{ICONA_MENU}</button>',
            '    <div class="menu-telefono" id="menu-telefono" popover>',
            f'      <nav aria-label="{nome_menu}">',
        ]
        if casa == "argonauta":
            righe.append(f'      <p class="menu-casa"><a href="{u["home"]}">← Sic Studio</a></p>')
            righe.append(f'      <ul class="menu"><li><a href="{u["argonauta"]}"'
                         f'{" aria-current=" + chr(34) + "page" + chr(34) if d["voce"] == "argonauta" else ""}>Argonauta</a></li></ul>')
        righe += ["  " + r for r in lista("menu", telefono=True)]
        righe += [
            '      </nav>',
            f'      <button class="chiudi-menu" type="button" popovertarget="menu-telefono" popovertargetaction="hide">'
            f'{p["chiudi"]}</button>',
            '    </div>',
        ]
    righe += ['  </div>', '</header>']
    return "\n".join(righe)


def piede(file, d):
    lingua = d["lingua"]
    p, u = PAROLE[lingua], percorsi(lingua)
    altra = d["altro"] or ("/en/" if lingua == "it" else "/")
    contatti = "/#contatti" if lingua == "it" else "/en/#contatti"
    studio = [(k, t) for k, t in p["voci_studio"] if k != "argonauta"]
    argonauta = [("argonauta", "Argonauta")] + p["voci_argonauta"]

    def link(k):
        return contatti if k == "contatti" else u[k]

    def gruppo(titolo, voci):
        return (f'      <div><p class="colophon-titolo">{titolo}</p><ul>'
                + "".join(f'<li><a href="{link(k)}">{t}</a></li>' for k, t in voci) + '</ul></div>')

    return "\n".join([
        '<footer class="colophon">',
        '  <div class="colophon-riga">',
        f'    <div class="colophon-firma">{MARCHIO}',
        '      <p><strong>Sic Studio</strong> di Vincenzo Siciliano</p>',
        f'      <p>{p["luogo"]}</p>',
        '    </div>',
        f'    <nav class="colophon-pagine" aria-label="{p["pagine"]}">',
        gruppo("Sic Studio", studio),
        gruppo("Argonauta", argonauta),
        '    </nav>',
        '    <div class="colophon-nota">',
        '      <p>© 2026 Vincenzo Siciliano · <a href="mailto:vincenzo@sicstudio.app">vincenzo@sicstudio.app</a> · '
        f'<a href="{altra}" hreflang="{p["altra_lingua"]}" lang="{p["altra_lingua"]}">{p["altra"]}</a></p>',
        f'      <p>{p["colophon"]}</p>',
        f'      <p class="crediti" id="crediti">{p["crediti"]}</p>',
        '    </div>',
        '  </div>',
        # La partita IVA, quando c'è, va qui dentro, in una riga <p> del colophon (va indicata nella home del sito).
        '</footer>',
    ])


PARTI = {"testa": testa, "testata": testata, "piede": piede}


def scheletro(d):
    return (f'<!doctype html>\n<html lang="{d["lingua"]}">\n<head>\n<!-- testa:inizio -->\n<!-- testa:fine -->\n</head>\n'
            '<body>\n<!-- testata:inizio -->\n<!-- testata:fine -->\n<main id="contenuto">\n</main>\n'
            '<!-- piede:inizio -->\n<!-- piede:fine -->\n</body>\n</html>\n')


def aggiorna(file, d, nuove):
    """Riscrive le tre parti di una pagina. Ritorna quanti problemi ha trovato: la pagina che manca, o una parte i cui
    segni non ci sono una volta sola (scritti male, tolti o doppi)."""
    p = SITO / file
    if not p.exists():
        if not nuove:
            print(f"manca {file}")
            return 1
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(scheletro(d), encoding="utf-8")
        print(f"creata {file}")
    testo = p.read_text(encoding="utf-8")
    prima = testo
    problemi = 0
    for parte, funzione in PARTI.items():
        modello = re.compile(rf"(<!-- {parte}:inizio -->\n).*?(<!-- {parte}:fine -->)", re.S)
        testo, quante = modello.subn(lambda m: m.group(1) + funzione(file, d) + "\n" + m.group(2), testo)
        if quante != 1:
            print(f"{file}: i segni di «{parte}» ci sono {quante} volte invece di una")
            problemi += 1
    testo = re.sub(r'<html lang="[a-z]+"', f'<html lang="{d["lingua"]}"', testo, count=1)
    if testo != prima and not problemi:
        p.write_text(testo, encoding="utf-8")
        print(f"aggiornata {file}")
    return problemi


def main():
    nuove = "--nuove" in sys.argv
    problemi = sum(aggiorna(file, d, nuove) for file, d in PAGINE.items())
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
