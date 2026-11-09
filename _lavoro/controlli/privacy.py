"""La pagina della privacy dice parola per parola il testo di privacy-argonauta.md, in italiano e in inglese.

Si confrontano le parole dentro <article id="it"> e <article id="en">, senza la navigazione aggiunta
(gli elementi con la classe «lingua» o «indice»). Il testo della bozza parte da «## Italiano».
"""
import difflib, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, LAVORO, leggi

BOZZA = LAVORO / "riferimenti" / "privacy-argonauta.md"
PAGINA = SITO / "argonauta" / "privacy" / "index.html"
ESCLUDI = {"lingua", "language", "indice"}


def parole(s):
    return re.findall(r"[\w'’«»().,:;\[\]-]+", s)


def testo_bozza():
    corpo = BOZZA.read_text(encoding="utf-8").split("## Italiano", 1)[1]
    corpo = corpo.replace("## English", "")
    corpo = re.sub(r"^#+ ", "", corpo, flags=re.M)
    corpo = corpo.replace("**", "").replace("`", "")
    corpo = re.sub(r"^\s*- ", "", corpo, flags=re.M)
    corpo = re.sub(r"^---\s*$", "", corpo, flags=re.M)
    return parole(corpo)


def testo_pagina():
    albero = leggi(PAGINA)
    pezzi = []
    for dati, pila in albero.testo:
        dentro = any(n == "article" and a.get("id") in ("it", "en") for n, a in pila)
        escluso = any(set((a.get("class") or "").split()) & ESCLUDI for _, a in pila)
        if dentro and not escluso:
            pezzi.append(dati)
    return parole("".join(pezzi))


def main():
    a, b = testo_bozza(), testo_pagina()
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    diff = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"Privacy: {len(a)} parole nella bozza, {len(b)} nella pagina, {len(diff)} differenze")
    for op, i1, i2, j1, j2 in diff:
        print(f"  {op}: bozza «{' '.join(a[i1:i2])}» · pagina «{' '.join(b[j1:j2])}»")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main())
