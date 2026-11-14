"""Il contrasto di ogni coppia di testo e fondo, in chiaro e in scuro, con le variabili di style.css.

Testo normale almeno 4,5:1; testi grandi, simboli e disegni almeno 3:1. Le coppie sono quelle che il sito usa:
se ne aggiungi una nel CSS, aggiungila qui.
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO

CSS = SITO / "style.css"

# (testo, fondo, minimo, dove, temi): temi è "chiaro", "scuro" o "entrambi". I colori scritti con # sono quelli
# fissi del CSS (la copertina, la fascetta, il cielo dell'apertura).
COPPIE = [
    ("--testo", "--carta", 4.5, "testo sulla carta", "entrambi"),
    ("--testo-2", "--carta", 4.5, "note, date e didascalie sulla carta", "entrambi"),
    ("--testo", "--carta-2", 4.5, "testo sul tavolo e nel colophon", "entrambi"),
    ("--testo-2", "--carta-2", 4.5, "note sul tavolo e nel colophon", "entrambi"),
    ("--testo", "--scheda", 4.5, "testo sui fogli (quaderno, definizioni)", "entrambi"),
    ("--testo-2", "--scheda", 4.5, "note sui fogli", "entrambi"),
    ("--mare", "--carta", 4.5, "link sulla carta", "entrambi"),
    ("--mare", "--carta-2", 4.5, "link sul tavolo", "entrambi"),
    ("--mare", "--scheda", 4.5, "link e «Chiudi» sui fogli", "entrambi"),
    ("--oro", "--carta", 3.0, "numeri e capilettera d'oro, grandi", "entrambi"),
    ("--oro", "--carta-2", 3.0, "numeri d'oro sul tavolo", "entrambi"),
    ("#F6E7C2", "#0A1828", 4.5, "titolo della copertina sul velo scuro in alto", "entrambi"),
    ("#EFE4D0", "#0A1828", 4.5, "motto e marca della copertina sul velo", "entrambi"),
    ("#1E1B17", "#E7C46E", 4.5, "fascetta «In prova»", "entrambi"),
    ("#E7C46E", "--rilegatura", 4.5, "il nome sul dorso", "entrambi"),
    ("#FFFFFF", "--rilegatura", 4.5, "testo bianco sulla rilegatura", "entrambi"),
    ("--testo-2", "#F2D2AE", 4.5, "frase dell'apertura sull'alba, nel punto più caldo", "chiaro"),
    ("--testo", "#172741", 4.5, "testo dell'apertura sul cielo di notte, all'orizzonte", "scuro"),
    ("--testo-2", "#172741", 4.5, "frase dell'apertura sul cielo di notte, all'orizzonte", "scuro"),
    ("--testo", "#FBF0E2", 4.5, "la giornata all'alba", "chiaro"),
    ("--testo-2", "#E9E6EF", 4.5, "la giornata a sera", "chiaro"),
    ("--testo-2", "#17171D", 4.5, "la giornata all'alba, di notte", "scuro"),
    ("--testo-2", "#070A12", 4.5, "la giornata a sera, di notte", "scuro"),
    ("--testo", "#EEDDBF", 4.5, "testo sul muro della bottega (--muro)", "chiaro"),
    ("--testo-2", "#EEDDBF", 4.5, "occhielli sul muro della bottega", "chiaro"),
    ("#065F80", "#EEDDBF", 4.5, "link sul muro della bottega (.dentro ha il suo --mare)", "chiaro"),
    ("--testo", "#2A2018", 4.5, "testo sul muro della bottega, di notte", "scuro"),
    ("--testo-2", "#2A2018", 4.5, "occhielli sul muro della bottega, di notte", "scuro"),
    ("--mare", "#2A2018", 4.5, "link sul muro della bottega, di notte", "scuro"),
    ("--testo", "#DCE7EA", 4.5, "nomi degli approdi sul mare della carta", "chiaro"),
    ("--testo", "#0F1E2C", 4.5, "nomi degli approdi sul mare della carta, di notte", "scuro"),
    ("#46697A", "#DCE7EA", 4.5, "nomi dei mari sulla carta", "chiaro"),
    ("#7FA7B8", "#0F1E2C", 4.5, "nomi dei mari sulla carta, di notte", "scuro"),
]


def variabili(css):
    """Le variabili del primo :root (chiaro) e di :root dentro prefers-color-scheme: dark (scuro); i blocchi P3 no."""
    chiaro = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", re.search(r":root\s*\{([^}]*)\}", css).group(1)))
    m = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}", css)
    scuro = dict(chiaro)
    scuro.update(dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1))))
    return chiaro, scuro


def rgba(valore):
    v = valore.strip()
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        parti = [x.strip() for x in m.group(1).split(",")]
        r, g, b = (float(x) for x in parti[:3])
        a = float(parti[3]) if len(parti) > 3 else 1.0
        return (r, g, b, a)
    raise ValueError(valore)


def sopra(colore, fondo):
    r, g, b, a = colore
    R, G, B, _ = fondo
    return (r * a + R * (1 - a), g * a + G * (1 - a), b * a + B * (1 - a), 1.0)


def luminanza(c):
    def canale(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (canale(x) for x in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rapporto(a, b):
    la, lb = luminanza(a), luminanza(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main():
    css = CSS.read_text(encoding="utf-8")
    problemi = 0
    for tema, var in zip(("chiaro", "scuro"), variabili(css)):
        for testo, fondo, minimo, dove, temi in COPPIE:
            if temi not in ("entrambi", tema):
                continue
            try:
                f = rgba(var.get(fondo, fondo))
                t = sopra(rgba(var.get(testo, testo)), f)
            except (KeyError, ValueError) as e:
                print(f"{tema}: non trovo {e} per «{dove}»")
                problemi += 1
                continue
            r = rapporto(t, f)
            stato = "ok" if r >= minimo else "BASSO"
            if r < minimo:
                problemi += 1
            print(f"{tema:6} {r:5.2f}:1 (min {minimo}) {stato:5} {dove}")
    print(f"Contrasto: {problemi} coppie sotto il minimo")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
