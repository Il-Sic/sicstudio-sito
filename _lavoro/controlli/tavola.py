"""La tavola del giorno (disegni/tavola.py). Le pagine in git non la contengono: la scrive nel sito già costruito il
lavoro giornaliero, quando è acceso. Qui la si rifà per un giro di date, nelle due home e nelle due pagine dello
studio, in una cartella di passaggio, e si guarda che ogni pagina resti in regola come le altre:
- i conti del cielo tornano sulle date note (tavola.py --verifica);
- HTML ben formato e id unici (come forma.py), niente script né stili in linea e le meta al loro posto (risorse.py);
- sotto i 150 KB (pesi.py);
- ogni classe tv- usata nelle pagine è in style.css, e ogni classe tv- di style.css serve ad almeno una data;
- apostrofi tipografici nelle parole che la tavola aggiunge.
"""
import collections, datetime, importlib.util, pathlib, re, sys, tempfile
QUI = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(QUI))
from comune import SITO, leggi
import risorse

# Lo script dei disegni ha lo stesso nome di questo controllo: lo si carica dal suo file.
_dove = importlib.util.spec_from_file_location("tavola_dei_disegni", QUI.parent / "disegni" / "tavola.py")
tavola = importlib.util.module_from_spec(_dove)
_dove.loader.exec_module(tavola)

KB = 1024


def date():
    """Oggi, e un giro di date fisse (così il controllo dà lo stesso esito ogni giorno): il primo e il 15 di ogni mese
    del 2027, più i giorni in cui la tavola ha qualcosa di suo, cioè le stelle cadenti d'agosto e di dicembre, il 29
    febbraio e una sera con Venere (gli altri pianeti passano già nelle prime)."""
    giorni = {datetime.date(2027, mese, g) for mese in range(1, 13) for g in (1, 15)}
    giorni |= {datetime.datetime.now(tavola.ROMA).date(), datetime.date(2027, 8, 12), datetime.date(2027, 12, 13), datetime.date(2028, 2, 29),
               datetime.date(2027, 12, 23)}
    return sorted(giorni)


def main():
    problemi = []
    if tavola.verifica():
        problemi.append("i conti del cielo non tornano (vedi sopra)")
    css = (SITO / "style.css").read_text(encoding="utf-8")
    nel_css = set(re.findall(r"\.(tv-[a-z0-9-]+)", css))
    usate, pagine, pesante = set(), 0, 0
    with tempfile.TemporaryDirectory() as cartella:
        p = pathlib.Path(cartella) / "pagina.html"
        for giorno in date():
            for nome in list(tavola.PAGINE) + tavola.STUDIO:
                testo = (SITO / nome).read_text(encoding="utf-8")
                testo = tavola.tavola(testo, giorno, tavola.PAGINE[nome]) if nome in tavola.PAGINE else tavola.studio(testo, giorno)
                p.write_text(testo, encoding="utf-8")
                pagine += 1
                pesante = max(pesante, len(testo.encode("utf-8")))
                dove = f"{nome} del {giorno.isoformat()}"
                albero = leggi(p)
                errori = list(albero.errori)
                aperti = [n for n, _ in albero.aperti if n not in ("html", "body", "head")]
                if aperti:
                    errori.append(f"tag non chiusi alla fine: {aperti}")
                ids = collections.Counter(a["id"] for _, a, _ in albero.tag if "id" in a)
                errori += [f"id ripetuto: {i} ({c} volte)" for i, c in ids.items() if c > 1]
                errori += risorse.controlla_pagina(p)
                if len(testo.encode("utf-8")) > 150 * KB:
                    errori.append(f"{len(testo.encode('utf-8')) / KB:.0f} KB (massimo 150)")
                classi = {c for _, a, _ in albero.tag for c in (a.get("class") or "").split() if c.startswith("tv-")}
                usate |= classi
                errori += [f"la classe {c} non è in style.css" for c in sorted(classi - nel_css)]
                # le parole che la tavola aggiunge: la riga della data e i nomi nel cielo
                aggiunte = re.findall(r'<(?:p class="tv-tiratura"|text class="tv-nome[^"]*"[^>]*)>([^<]*)<', testo)
                errori += [f"apostrofo dritto in «{a}»" for a in aggiunte if "'" in a]
                if nome in tavola.PAGINE and not any("tv-tiratura" in (a.get("class") or "") for _, a, _ in albero.tag):
                    errori.append("manca la riga della data")
                problemi += [f"{dove}: {e}" for e in errori]
    problemi += [f"style.css: la classe {c} non serve a nessuna data" for c in sorted(nel_css - usate)]
    for riga in problemi:
        print(riga)
    print(f"Tavola del giorno: {pagine} pagine rifatte per {len(date())} date, la più pesante {pesante / KB:.0f} KB, {len(problemi)} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
