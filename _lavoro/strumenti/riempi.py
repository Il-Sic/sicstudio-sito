"""Riempie i segnaposto delle schermate in una pagina: {{schermata:nome|testo alternativo|didascalia}}.

    python3 -I _lavoro/strumenti/riempi.py <pagina.html>

Ogni segnaposto diventa una figura con la cornice del telefono, in chiaro e in scuro, con le misure vere e le copie
AVIF e WebP (vedi schermata.py; le copie si fanno prima, con schermate.py). La didascalia si può lasciare vuota. Il
sizes dipende dal posto: dentro un «momento» della giornata la schermata è più larga sul computer.
"""
import pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from schermata import codice, sizes_per

p = pathlib.Path(sys.argv[1])
testo = p.read_text(encoding="utf-8")


def figura(m):
    parti = m.group(1).split("|")
    didascalia = parti[2] if len(parti) > 2 and parti[2] else None
    return codice(parti[0], parti[1], didascalia, rientro="", sizes=sizes_per(testo, m.start()))


testo, n = re.subn(r"\{\{schermata:([^}]+)\}\}", figura, testo)
p.write_text(testo, encoding="utf-8")
print(f"{p}: {n} schermate")
