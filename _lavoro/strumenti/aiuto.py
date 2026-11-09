"""Rifà la pagina «Aiuto e domande» (italiana o inglese) dal testo di online-6-11, con la nuova forma: l'apertura, i
gruppi di domande con il titolo a lato, le parole di bordo che si aprono nel testo (popover, senza JavaScript) e il
glossario in fondo. I testi delle domande e delle risposte restano quelli di prima, parola per parola.

    python3 -I _lavoro/strumenti/aiuto.py it|en
"""
import html, pathlib, re, sys

SITO = pathlib.Path(__file__).resolve().parents[2]
LINGUA = sys.argv[1]
FILE = {"it": "argonauta/aiuto/index.html", "en": "en/argonauta/help/index.html"}[LINGUA]
# La parola da cercare nelle risposte per ogni voce del glossario (la prima volta che compare).
CERCA = {
    "it": {"Rotta": r"\brott[ae]\b", "Tappa": r"\btapp[ae]\b", "Missione": r"\bmission[ei]\b", "Odissea": r"\bOdissea\b",
           "Atlante": r"\bAtlante\b", "Scheda": r"\bsched[ae]\b", "Diario Esploratore": r"\bDiario\b",
           "Il timbro della collezione": r"\btimbro\b", "Badge": r"\bbadge\b", "Livello": r"\blivell[oi]\b",
           "Argo": r"\bArgo\b", "Equipaggio": r"\b[Ee]quipaggio\b", "Il viaggio di Argo": r"\bviaggio di Argo\b",
           "Miti e leggende": r"\bMiti e leggende\b", "Prima di partire": r"Prima di partire", "Sicurezza": r"«Sicurezza»"},
    "en": {"Route": r"\broutes?\b", "Stage": r"\bstages?\b", "Mission": r"\bmissions?\b", "Odyssey": r"\bOdyssey\b",
           "Atlas": r"\bAtlas\b", "Card": r"\bcards?\b", "Explorer's Journal": r"\bJournal\b",
           "The collection stamp": r"\bstamp\b", "Badge": r"\bbadges?\b", "Level": r"\blevels?\b", "Argo": r"\bArgo\b",
           "Heroes": r"\bHeroes\b", "The Voyage of Argo": r"\b[Vv]oyage\b", "Myths and Legends": r"\b[Mm]yths and [Ll]egends\b",
           "Before You Set Off": r"\b[Bb]efore [Yy]ou [Ss]et [Oo]ff\b", "Safety": r"\bSafety\b"},
}[LINGUA]
PAROLE = {
    "it": {"occhiello": "Argonauta · aiuto", "indice": "In questa pagina", "chiudi": "Chiudi",
           "glossario_nota": "Tocca una parola sottolineata nelle risposte per leggerla qui senza scendere."},
    "en": {"occhiello": "Argonauta · help", "indice": "On this page", "chiudi": "Close",
           "glossario_nota": "Tap an underlined word in the answers to read it here without scrolling."},
}[LINGUA]

vecchio = (SITO / "_lavoro" / "online-6-11" / FILE).read_text(encoding="utf-8")
main = vecchio.split('<main id="contenuto">')[1].split("</main>")[0]
testa = re.search(r'<section class="testa-pagina".*?</section>', main, re.S).group(0)
h1 = re.search(r"<h1[^>]*>(.*?)</h1>", testa, re.S).group(1)
intro = re.search(r'<p class="introduzione">(.*?)</p>', testa, re.S).group(1)
salti = re.findall(r'<li><a href="(#[^"]+)">(.*?)</a></li>', testa)

gruppi = re.findall(r'<section id="([^"]+)"[^>]*>\s*<h2 id="([^"]+)">(.*?)</h2>(.*?)</section>', main, re.S)
voci = []
glossario = None
for sid, hid, titolo, corpo in gruppi:
    if "glossario" in corpo:
        glossario = (sid, hid, titolo, corpo)
    else:
        voci.append((sid, hid, titolo, re.findall(r'<details class="domanda">.*?</details>', corpo, re.S)))
termini = re.findall(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", glossario[3], re.S)
nota_gloss = re.search(r'<p class="secondario">(.*?)</p>', glossario[3], re.S).group(1)


def ident(termine):
    s = html.unescape(re.sub("<[^>]+>", "", termine)).lower()
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u"), ("'", " "), ("’", " ")):
        s = s.replace(a, b)
    return "parola-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")


usati = set()


def avvolgi(risposta):
    """Mette il pulsante della parola alla sua prima comparsa, fuori dai link e dai tag."""
    pezzi = re.split(r"(<a\b.*?</a>|<[^>]+>)", risposta, flags=re.S)
    for i, pezzo in enumerate(pezzi):
        if not pezzo or pezzo.startswith("<"):
            continue
        for termine, modello in sorted(CERCA.items(), key=lambda kv: -len(kv[1])):
            if termine in usati:
                continue
            m = re.search(modello, pezzo)
            if m:
                usati.add(termine)
                bottone = (f'<button type="button" class="parola" popovertarget="{ident(termine)}">'
                           f'{m.group(0)}</button>')
                dopo = re.match(r"[,.;:!?»”)]+", pezzo[m.end():])
                if dopo:  # la virgola o il punto restano sulla stessa riga della parola
                    bottone = f'<span class="parola-legata">{bottone}{dopo.group(0)}</span>'
                    pezzo = pezzo[:m.start()] + bottone + pezzo[m.end() + len(dopo.group(0)):]
                else:
                    pezzo = pezzo[:m.start()] + bottone + pezzo[m.end():]
        pezzi[i] = pezzo
    return "".join(pezzi)


righe = [f'<header class="apertura-aiuto fascia">',
         f'  <p class="occhiello">{PAROLE["occhiello"]}</p>',
         f'  <h1>{h1}</h1>',
         f'  <p class="sottotitolo misura">{intro}</p>',
         f'  <nav class="indice-mito" aria-label="{PAROLE["indice"]}">',
         '    <ol>' + "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in salti) + '</ol>',
         '  </nav>', '</header>', '']
for n, (sid, hid, titolo, domande) in enumerate(voci):
    classe = "domande-gruppo fascia-stretta" + (" tavolo" if n % 2 else "")
    righe.append(f'<section class="{classe}" id="{sid}" aria-labelledby="{hid}">')
    righe.append('  <div class="domande-riga">')
    righe.append(f'    <h2 class="titolo-sezione" id="{hid}">{titolo}</h2>')
    righe.append('    <div class="domande">')
    for d in domande:
        d = re.sub(r'(<div class="risposta">)(.*?)(</div>)', lambda m: m.group(1) + avvolgi(m.group(2)) + m.group(3), d, flags=re.S)
        righe.append("      " + d.strip())
    righe.append('    </div>')
    righe.append('  </div>')
    righe.append('</section>')
    righe.append('')
sid, hid, titolo, _ = glossario
righe.append(f'<section class="parole-bordo fascia-stretta" id="{sid}" aria-labelledby="{hid}">')
righe.append('  <div class="capo">')
righe.append(f'    <h2 class="titolo-sezione" id="{hid}">{titolo}</h2>')
righe.append(f'    <p class="sottotitolo misura">{nota_gloss}</p>')
righe.append('  </div>')
righe.append('  <dl class="glossario">')
for dt, dd in termini:
    righe.append(f'    <div><dt>{dt}</dt><dd>{dd.strip()}</dd></div>')
righe.append('  </dl>')
righe.append('</section>')
righe.append('')
righe.append('<div class="definizioni">')
for dt, dd in termini:
    if html.unescape(re.sub("<[^>]+>", "", dt)) not in usati and dt not in usati:
        continue
    righe.append(f'  <div class="definizione" id="{ident(dt)}" popover>')
    righe.append(f'    <p class="definizione-termine">{dt}</p>')
    righe.append(f'    <p>{dd.strip()}</p>')
    righe.append(f'    <button type="button" class="chiudi-definizione" popovertarget="{ident(dt)}" popovertargetaction="hide">{PAROLE["chiudi"]}</button>')
    righe.append('  </div>')
righe.append('</div>')

PRIVACY = (SITO / "_lavoro" / "riferimenti" / "privacy-argonauta.md").read_text(encoding="utf-8")
PRIVACY = re.sub(r"\s+", " ", PRIVACY)


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


# Lo studio è Vincenzo e parla in prima persona (Sic, 7/11): «scrivimi», non «scrivici».
if LINGUA == "it":
    righe = [r.replace("scrivici a", "scrivimi a") for r in righe]
righe = [apostrofi(r) for r in righe]
pagina = (SITO / FILE).read_text(encoding="utf-8")
a = pagina.index('<main id="contenuto"'); b = pagina.index("</main>")
pagina = pagina[:a] + '<main id="contenuto" class="pagina-aiuto">\n\n' + "\n".join(righe) + "\n\n" + pagina[b:]
(SITO / FILE).write_text(pagina, encoding="utf-8")
print(FILE, "domande:", sum(len(v[3]) for v in voci), "parole nel testo:", len(usati), "di", len(termini))
print("non trovate:", [t for t in CERCA if t not in usati])
