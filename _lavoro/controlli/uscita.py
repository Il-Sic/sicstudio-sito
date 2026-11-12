"""La lista delle frasi da cambiare il giorno in cui un'app esce (strumenti/uscita.py) è ancora buona: ogni frase «di
oggi» della lista c'è ancora, una volta sola, nel suo file. Se una pagina è cambiata, la lista va aggiornata, se no
quel giorno la frase vecchia resterebbe online.

La lista sta solo sul Mac di Sic (fuori da git: parla di cose non ancora annunciate). Dove non c'è, come su GitHub, il
controllo esce con 3 e nel riassunto di tutti.py compare come «saltato». Una lista non ancora completa non è un
problema: lo diventa una frase che non si trova più."""
import pathlib, subprocess, sys

QUI = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    sys.exit(subprocess.run([sys.executable, "-I", str(QUI.parent / "strumenti" / "uscita.py")]).returncode)
