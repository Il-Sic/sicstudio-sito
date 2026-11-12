"""La tavola del giorno (disegni/tavola.py). Le pagine in git non la contengono: la scrive nel sito già costruito il
lavoro giornaliero, quando è acceso. Qui la si rifà per un giro di date, nelle due home e nelle due pagine dello
studio, in una cartella di passaggio, e si guarda che ogni pagina resti in regola come le altre:
- i conti del cielo tornano sulle date note (tavola.py --verifica);
- HTML ben formato e id unici (come forma.py), niente script né stili in linea e le meta al loro posto (risorse.py);
- sotto i 400 KB: dal 12/11 il cielo ha tutte le stelle a occhio nudo e la Via Lattea dipinta, e il peso non è più
  un vincolo (lo ha detto Sic); il limite resta contro gli errori grossolani;
- ogni classe tv- usata nelle pagine è in style.css, e ogni classe tv- di style.css serve ad almeno una data;
- apostrofi tipografici nelle parole che la tavola aggiunge: la data della testata, i nomi nel cielo, il lunario;
- la luna del giorno e la data stanno nella testata, una volta, e sono il pulsante che apre il lunario; la data ha
  la forma lunga e quella breve, e il nome per chi non vede le contiene; il lunario c'è, una volta;
- di giorno: la carta con la strada del sole c'è una volta e la soglia la riprende; il suo sole sta nella fascia che
  si vede anche al telefono, sotto la testata; le ombre del sole ci sono nelle due scene e sopra il sentiero;
- le righe delle parole del frontespizio (parole-fronte.json) ci sono, per le due lingue e le due forme di finestra.
Che nessuna stella tocchi davvero una parola, e che le parole stiano sopra gli alberi della casa a ogni misura di
finestra, lo guarda nel browser strumenti/parole-fronte.mjs --controlla, a mano.
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
                if len(testo.encode("utf-8")) > 400 * KB:
                    errori.append(f"{len(testo.encode('utf-8')) / KB:.0f} KB (massimo 400)")
                classi = {c for _, a, _ in albero.tag for c in (a.get("class") or "").split() if c.startswith("tv-")}
                usate |= classi
                errori += [f"la classe {c} non è in style.css" for c in sorted(classi - nel_css)]
                # le parole che la tavola aggiunge: la data della testata, i nomi nel cielo e il lunario
                aggiunte = re.findall(r'<(?:span class="tv-oggi-[a-z]+"|text class="tv-nome[^"]*"[^>]*)>([^<]*)<', testo)
                aggiunte += re.findall(r'class="tv-oggi"[^>]*aria-label="([^"]*)"', testo)
                lunario = re.findall(r'<!-- lunario:inizio -->(.*?)<!-- lunario:fine -->', testo, flags=re.S)
                aggiunte += [pezzo for l in lunario for pezzo in re.findall(r'>([^<]+)<', l)] + [v for l in lunario for v in re.findall(r'aria-label="([^"]*)"', l)]
                errori += [f"apostrofo dritto in «{a}»" for a in aggiunte if "'" in a]
                if nome in tavola.PAGINE:
                    oggi = re.findall(r'<button type="button" class="tv-oggi" popovertarget="lunario" aria-label="([^"]*)"><svg class="tv-sigillo"[^>]*><g[^>]*>'
                                      r'<circle class="tv-lune-ombra" r="13"/>.*?</g></svg><span class="tv-oggi-lunga">([^<]+)</span><span class="tv-oggi-corta">([^<]+)</span></button>',
                                      testo.split("<!-- testata:fine -->")[0])
                    if len(oggi) != 1 or testo.count('class="tv-oggi"') != 1:
                        errori.append("nella testata non c'è, una volta, il pulsante con la luna e la data che apre il lunario")
                    elif oggi[0][1] not in oggi[0][0] or not oggi[0][2][:1].isdigit() or str(giorno.year) not in oggi[0][0]:
                        errori.append(f"la data della testata non torna con il suo nome: {oggi[0]}")
                    if len(lunario) != 1 or testo.count('id="lunario" popover') != 1:
                        errori.append("il lunario non c'è una volta sola")
                    elif len(re.findall(r'class="tv-lune-giorno"', lunario[0])) != 7 or lunario[0].count("<dt>") != 4:
                        errori.append("al lunario manca una voce o una delle sette lune")
                    # la carta del giorno e le ombre
                    if testo.count('id="tv-carta-giorno"') != 1 or testo.count('<use href="#tv-carta-giorno"/>') != 1:
                        errori.append("la carta del giorno non c'è una volta, o la soglia non la riprende")
                    x, y = tavola.sul_foglio_di_giorno(*tavola.sole_a(tavola.di_giorno(giorno)))
                    if not (530 < x < 925 and 185 < y < 560):
                        errori.append(f"il sole della carta del giorno è fuori dalla fascia che si vede ({x:.0f}, {y:.0f})")
                    if testo.count('id="tv-ombra-sole"') != 1 or testo.count('<use href="#tv-ombra-sole"/>') != 2 or testo.count('class="tv-ombra tv-ombra-lontana"') < 3:
                        errori.append("le ombre del sole non ci sono nelle due scene, sopra il sentiero e sotto i boschi")
                    if re.search(r'[ "MLHVZ(]-?(?:nan|inf)\b', testo):
                        errori.append("un numero della tavola non è un numero (nan o inf)")
                # il confronto di online.sh: tolti i disegni del cielo e della luna non deve restarne traccia
                spoglia = tavola.senza_cielo(testo)
                if any(pezzo in spoglia for pezzo in ('class="volta"', "tv-luna", "tv-cielo", "tv-lune", "data:image", "tv-ombra", "tv-carta", "tv-strada", "tv-sigillo")):
                    errori.append("senza_cielo() lascia nella pagina pezzi del cielo, della luna, del lunario, delle ombre o la luna della testata")
                problemi += [f"{dove}: {e}" for e in errori]
    problemi += [f"style.css: la classe {c} non serve a nessuna data" for c in sorted(nel_css - usate)]
    # le righe delle parole da cui le stelle stanno lontane: tutte e due le lingue, finestre in piedi e sdraiate
    for lingua in tavola.PAGINE.values():
        for stretto, forma in ((True, "più alte che larghe"), (False, "più larghe che alte")):
            if len(tavola.PAROLE.get((stretto, lingua), ())) < 40:
                problemi.append(f"parole-fronte.json: poche righe misurate in «{lingua}» per le finestre {forma} (si rifanno con strumenti/parole-fronte.mjs)")
    for riga in problemi:
        print(riga)
    print(f"Tavola del giorno: {pagine} pagine rifatte per {len(date())} date, la più pesante {pesante / KB:.0f} KB, {len(problemi)} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
