"""Ciò che nel sito è scritto da uno script è ancora uguale a ciò che lo script scrive: rifà tutto in una copia
(strumenti/costruisci.py --verifica) e si ferma se cambia anche un solo file. Trova un pezzo generato ritoccato a mano
nella pagina, uno script cambiato e non rilanciato, e i segni di un blocco scritti male o tolti."""
import pathlib, subprocess, sys

QUI = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    sys.exit(subprocess.run([sys.executable, "-I", str(QUI.parent / "strumenti" / "costruisci.py"), "--verifica"]).returncode)
