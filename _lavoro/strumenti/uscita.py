"""Il giorno in cui un'app esce: cambia in un colpo solo le frasi del sito che quel giorno diventano false.

La lista delle frasi sta in _lavoro/riferimenti/uscita.toml, che resta solo sul Mac: parla di cose non ancora
annunciate, e il repository è pubblico. Ogni voce dice il file, la frase di oggi («prima») e quella del giorno
dell'uscita («dopo»); oppure, per una frase da riguardare quel giorno ma che non cambia, «resta = true».

    python3 -I _lavoro/strumenti/uscita.py             dice che cosa cambierebbe e che cosa manca; non tocca niente
    python3 -I _lavoro/strumenti/uscita.py --applica   cambia i file e rilancia costruisci.py

O cambia tutto, o non cambia niente. Non applica se:
- una frase «prima» non c'è una volta sola nel suo file (la pagina è cambiata: la lista va aggiornata);
- a una voce mancano sia «dopo» sia «resta» (va ancora decisa);
- in un «dopo» c'è {numero} o {store} e in [valori] il numero dell'app sull'App Store è vuoto.
Senza --applica esce con 1 solo nel primo caso, perché una lista non ancora completa è normale fino al giorno
dell'uscita: così la può lanciare ogni volta tutti.py (controlli/uscita.py) e accorgersi se una frase è cambiata.

Nel «dopo», {numero} è il numero dell'app sull'App Store e {store} il suo indirizzo. Dopo --applica: i controlli
(tutti.py), una riga nel giornale dello studio, e la privacy, che ha la sua strada (prima la bozza).
"""
import pathlib, subprocess, sys, tomllib

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
LISTA = SITO / "_lavoro" / "riferimenti" / "uscita.toml"


def leggi():
    """La lista: i valori e le voci, ognuna con il suo stato. Ritorna (voci, scadute, da decidere, senza valore)."""
    dati = tomllib.loads(LISTA.read_text(encoding="utf-8"))
    numero = str(dati.get("valori", {}).get("numero", "")).strip()
    valori = {"{numero}": numero, "{store}": f"https://apps.apple.com/app/id{numero}"}
    voci, scadute, da_decidere, senza_valore = [], [], [], []
    for n, voce in enumerate(dati.get("voce", []), 1):
        dove, prima, che = voce["dove"], voce["prima"], voce.get("che", "")
        nome = f"{n}. {dove}: {che}"
        file = (SITO / dove).resolve()
        if SITO.resolve() not in file.parents or not file.is_file():
            scadute.append(f"{nome} (il file non c'è)")
            continue
        quante = file.read_text(encoding="utf-8").count(prima)
        if quante != 1:
            scadute.append(f"{nome} (la frase di oggi c'è {quante} volte invece di una)")
            continue
        if voce.get("resta"):
            continue
        if "dopo" not in voce:
            da_decidere.append(nome)
            continue
        dopo = voce["dopo"]
        if not numero and any(segno in dopo for segno in valori):
            senza_valore.append(nome)
        for segno, valore in valori.items():
            dopo = dopo.replace(segno, valore)
        voci.append((nome, file, prima, dopo))
    return voci, scadute, da_decidere, senza_valore


def main():
    if not LISTA.exists():
        print(f"Uscita: la lista ({LISTA.relative_to(SITO)}) sta solo sul Mac di Sic, e qui non c'è")
        return 3
    voci, scadute, da_decidere, senza_valore = leggi()
    for nome in scadute:
        print(f"SCADUTA      {nome}")
    for nome in da_decidere:
        print(f"DA DECIDERE  {nome}")
    for nome in senza_valore:
        print(f"SENZA NUMERO {nome}")
    pronta = not (scadute or da_decidere or senza_valore)
    if "--applica" not in sys.argv:
        for nome, _, prima, dopo in voci:
            print(f"cambia       {nome}")
        print(f"Uscita: {len(voci)} frasi da cambiare, {len(da_decidere)} da decidere, {len(senza_valore)} aspettano il numero dell'app, "
              f"{len(scadute)} scadute; " + ("pronta" if pronta else "non ancora pronta"))
        return 1 if scadute else 0
    if not pronta:
        print("Uscita: non applico niente finché la lista non è completa")
        return 1
    # Più voci possono toccare lo stesso file: si cambia il testo in memoria e si scrive una volta sola.
    testi = {}
    for nome, file, prima, dopo in voci:
        testo = testi.get(file) or file.read_text(encoding="utf-8")
        if testo.count(prima) != 1:
            print(f"Uscita: due voci si pestano i piedi in {file.relative_to(SITO)} ({nome}); non ho cambiato niente")
            return 1
        testi[file] = testo.replace(prima, dopo)
    for file, testo in testi.items():
        file.write_text(testo, encoding="utf-8")
        print(f"cambiato {file.relative_to(SITO)}")
    r = subprocess.run([sys.executable, "-I", str(QUI / "costruisci.py")])
    print("\nOra: i controlli (python3 -I _lavoro/controlli/tutti.py), una riga nel giornale, e la privacy.")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
