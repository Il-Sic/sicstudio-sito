"""L'apostrofo tipografico (’) al posto di quello dritto (') in tutte le pagine del sito: nel testo e negli attributi
che si leggono (alt, title, aria-label e il content delle meta). Restano come sono la pagina della privacy e le sue
frasi citate parola per parola nelle altre pagine, i commenti e la Content-Security-Policy.

    python3 -I _lavoro/strumenti/apostrofi.py
"""
import pathlib, re, sys

SITO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SITO / "_lavoro" / "controlli"))
from comune import pagine, nome  # noqa: E402

PRIVACY = re.sub(r"\s+", " ", (SITO / "_lavoro" / "riferimenti" / "privacy-argonauta.md").read_text(encoding="utf-8"))
LETTI = ("alt", "title", "aria-label", "content")


def della_privacy(testo):
    """Vero se il testo, senza le virgolette intorno, è una frase dell'informativa."""
    t = re.sub(r"\s+", " ", testo).strip().strip("«»“”\"")
    return len(t) > 20 and t in PRIVACY


def nel_testo(pezzo):
    parti = re.split(r"(«[^»]*»|“[^”]*”)", pezzo)
    return "".join(p if (p[:1] in "«“" and della_privacy(p)) else p.replace("'", "’") for p in parti)


def nel_tag(tag):
    if "http-equiv" in tag:
        return tag
    def attributo(m):
        valore = m.group(3)
        return m.group(0) if della_privacy(valore) else f'{m.group(1)}={m.group(2)}{valore.replace(chr(39), "’")}{m.group(2)}'
    return re.sub(r'\b(%s)=(")([^"]*)"' % "|".join(LETTI), attributo, tag)


def sistema(codice):
    pezzi = re.split(r"(<!--.*?-->|<[^>]+>)", codice, flags=re.S)
    for i, pezzo in enumerate(pezzi):
        if not pezzo or pezzo.startswith("<!--"):
            continue
        if pezzo.startswith("<"):
            pezzi[i] = nel_tag(pezzo)
        elif not della_privacy(pezzo):
            pezzi[i] = nel_testo(pezzo)
    return "".join(pezzi)


def main():
    for p in pagine():
        if nome(p).startswith("argonauta/privacy/"):
            continue
        prima = p.read_text(encoding="utf-8")
        dopo = sistema(prima)
        if dopo != prima:
            p.write_text(dopo, encoding="utf-8")
            print(f"{nome(p)}: {prima.count(chr(39)) - dopo.count(chr(39))} apostrofi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
