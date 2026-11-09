"""Le parole da rileggere: ogni volta che compaiono, si controlla che vadano bene.

Si cercano nel testo visibile, negli alt, nei title, nelle aria-label e nelle meta description e og:.
Per le pagine inglesi si cercano anche le parole inglesi corrispondenti.
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import pagine, leggi, nome

# Le parole stanno in parole.json, accanto a questo file, che resta solo sul Mac (fuori da git: il repository è pubblico
# e fra quelle parole ci sono nomi che il sito non deve dire). «intere» si cercano solo come parole intere, in maiuscolo.
LISTA = pathlib.Path(__file__).with_name("parole.json")


def testi(p):
    albero = leggi(p)
    for dati, pila in albero.testo:
        if any(n in ("title",) for n, _ in pila) or not dati.strip():
            pass
        if dati.strip():
            yield dati
    for n, a, _ in albero.tag:
        for chiave in ("alt", "title", "aria-label"):
            if a.get(chiave):
                yield a[chiave]
        if n == "meta" and (a.get("name") == "description" or (a.get("property") or "").startswith("og:")):
            yield a.get("content") or ""


def main():
    if not LISTA.exists():
        print("Parole da rileggere: manca _lavoro/controlli/parole.json, che sta solo sul Mac (fuori da git)")
        return 0
    parole = json.loads(LISTA.read_text(encoding="utf-8"))
    intere = r"\b(?:" + "|".join(re.escape(w) for w in parole["intere"]) + r")\b"
    trovate = 0
    for p in pagine():
        testo = " ".join(" ".join(t.split()) for t in testi(p))
        cerca = parole["italiane"] + (parole["inglesi"] if "/en/" in f"/{nome(p)}" or p.name == "404.html" else [])
        trovati = [(m.start(), m.end(), m.group(0)) for m in re.finditer("|".join(re.escape(w) for w in cerca), testo, re.I)]
        # Le parole intere solo così come sono: «ai soccorsi» non conta.
        trovati += [(m.start(), m.end(), m.group(0)) for m in re.finditer(intere, testo)]
        for inizio_m, fine_m, parola in sorted(trovati):
            inizio = max(0, inizio_m - 70)
            print(f"{nome(p)}: [{parola}] …{testo[inizio:fine_m + 70]}…")
            trovate += 1
    print(f"Parole da rileggere: {trovate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
