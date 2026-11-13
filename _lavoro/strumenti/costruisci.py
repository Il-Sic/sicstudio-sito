"""Rifà tutto ciò che nel sito è scritto da uno script, nell'ordine giusto, con un comando solo.

    python3 -I _lavoro/strumenti/costruisci.py              rifà le pagine e i disegni
    python3 -I _lavoro/strumenti/costruisci.py --verifica   non tocca niente: rifà tutto in una copia e dice che cosa cambierebbe

Con --verifica esce con 1 se rifacendo cambia anche un solo file. Vuol dire una di due cose: un pezzo scritto da uno
script è stato ritoccato a mano nella pagina (e al prossimo giro andrebbe perso), oppure uno script o i suoi dati
sono cambiati e non è stato rilanciato. È uno dei controlli di tutti.py (controlli/generati.py), quindi lo guarda
anche GitHub a ogni pull request.

Qui ci sono solo gli script che dai file in git rifanno sempre gli stessi file, su qualunque computer. Restano a mano,
quando serve, quelli che hanno bisogno d'altro (li elenca A_MANO, e la guida dice quando).
"""
import filecmp, pathlib, shutil, subprocess, sys, tempfile

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]

# Lo script (dentro _lavoro), i suoi argomenti, e che cosa rifà. L'ordine conta: gli apostrofi per ultimi, perché
# ripassano il testo che gli altri hanno scritto.
PASSI = [
    ("disegni/marchio-3.py", [], "il marchio (img/icona.svg; favicon.ico e apple-touch-icon.png vengono dal kit del logo)"),
    ("disegni/argo-navis.py", [], "la nave Argo nel cielo, in italiano e in inglese"),
    ("disegni/argonauta.py", [], "il guscio dell'argonauta"),
    ("strumenti/condivise.py", [], "la testa, l'intestazione e il colophon di ogni pagina"),
    ("strumenti/aiuto.py", [], "le due pagine di aiuto, dai testi di aiuto.toml"),
    ("strumenti/schermata.py", ["--pagine"], "le righe <source> delle schermate"),
    ("disegni/casa.py", [], "la casa, il cielo e le cose della bottega, nella home e nello studio"),
    ("disegni/carta.py", [], "la carta del viaggio nelle pagine del mito, e i suoi fotogrammi in style.css"),
    ("strumenti/apostrofi.py", [], "gli apostrofi tipografici"),
]
A_MANO = [
    ("disegni/png.py", "l'anteprima dei link di Argonauta: servono i disegni originali, che stanno solo sul Mac"),
    ("disegni/anteprima-studio.py", "l'anteprima dei link dello studio: servono Chrome e il server acceso"),
    ("strumenti/schermate.py", "le copie AVIF e WebP delle schermate: servono Pillow e le schermate originali"),
    ("strumenti/parole-fronte.mjs", "le righe delle parole del frontespizio: servono Node, Chrome e il server acceso"),
    ("disegni/coste.py", "le coste della carta: serve il file di Natural Earth, scaricato a parte"),
]


def lancia(cartella, zitto):
    """Lancia i passi nella cartella data (il sito, o una sua copia). Ritorna i passi che non sono andati."""
    falliti = []
    for script, argomenti, che_cosa in PASSI:
        r = subprocess.run([sys.executable, "-I", str(cartella / "_lavoro" / script), *argomenti], cwd=cartella, capture_output=True, text=True)
        if r.returncode:
            falliti.append(script)
            print(f"NO  {script}: esce con {r.returncode}\n" + "".join("      " + riga + "\n" for riga in (r.stdout + r.stderr).strip().splitlines()[-6:]), end="")
        elif not zitto:
            print(f"ok  {script}: {che_cosa}")
    return falliti


def in_git():
    """I file del sito che non sono ignorati da git: quelli seguiti e quelli nuovi."""
    r = subprocess.run(["git", "-C", str(SITO), "ls-files", "-z", "--cached", "--others", "--exclude-standard"], capture_output=True)
    if r.returncode:
        sys.exit("costruisci.py --verifica: serve git, per sapere quali file fanno parte del sito")
    return [f for f in r.stdout.decode("utf-8").split("\0") if f and (SITO / f).is_file()]


def verifica():
    file = in_git()
    with tempfile.TemporaryDirectory() as copia:
        copia = pathlib.Path(copia)
        for f in file:
            (copia / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SITO / f, copia / f)
        falliti = lancia(copia, zitto=True)
        cambiati = [f for f in file if not filecmp.cmp(SITO / f, copia / f, shallow=False)]
        nuovi = sorted(str(p.relative_to(copia)) for p in copia.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                       and str(p.relative_to(copia)) not in set(file))
    for f in cambiati:
        print(f"CAMBIA {f}: rifatto dagli script non è più uguale (ritoccato a mano, o script non rilanciato)")
    for f in nuovi:
        print(f"NUOVO  {f}: uno script lo scrive, ma fra i file del sito non c'è")
    problemi = len(falliti) + len(cambiati) + len(nuovi)
    print(f"Generati: {len(PASSI)} script rilanciati in una copia di {len(file)} file, {problemi} problemi")
    return 1 if problemi else 0


def main():
    if "--verifica" in sys.argv:
        return verifica()
    falliti = lancia(SITO, zitto=False)
    if falliti:
        print(f"\nNon sono andati: {', '.join(falliti)}. Le pagine possono essere rimaste a metà: si guarda con «git status».")
        return 1
    print("\nRestano a mano, quando serve:")
    for script, quando in A_MANO:
        print(f"    {script}: {quando}")
    print("Poi i controlli: python3 -I _lavoro/controlli/tutti.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
