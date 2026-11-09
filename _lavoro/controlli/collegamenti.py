"""Ogni link interno, ancore comprese, porta a qualcosa che esiste; i link esterni si elencano."""
import pathlib, re, sys
from urllib.parse import urlsplit, unquote
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, pagine, leggi, nome


def bersaglio(da, percorso):
    """Il file a cui porta un indirizzo interno, come lo serve GitHub Pages."""
    if percorso.startswith("/"):
        p = SITO / percorso.lstrip("/")
    else:
        p = (da.parent / percorso)
    p = pathlib.Path(unquote(str(p)))
    if percorso.endswith("/") or p.is_dir():
        p = p / "index.html"
    return p


def id_di(p, cache={}):
    if p not in cache:
        cache[p] = {a["id"] for _, a, _ in leggi(p).tag if "id" in a}
    return cache[p]


def main():
    rotti, esterni = [], {}
    for p in pagine():
        for n, a, riga in leggi(p).tag:
            for chiave in ("href", "src", "srcset", "content"):
                valore = a.get(chiave)
                if not valore or (n == "meta" and chiave == "content" and not valore.startswith("https://sicstudio.app")):
                    continue
                for pezzo in ([v.strip().split(" ")[0] for v in valore.split(",")] if chiave == "srcset" else [valore]):
                    parti = urlsplit(pezzo)
                    if parti.scheme in ("mailto", "tel", "data"):
                        continue
                    if parti.scheme in ("http", "https"):
                        if parti.netloc == "sicstudio.app":
                            interno = parti.path or "/"
                        else:
                            esterni.setdefault(pezzo, set()).add(nome(p))
                            continue
                    else:
                        interno = parti.path
                    destinazione = bersaglio(p, interno) if interno else p
                    if not destinazione.exists():
                        rotti.append(f"{nome(p)} riga {riga}: {pezzo} → manca {destinazione.relative_to(SITO) if SITO in destinazione.parents else destinazione}")
                        continue
                    if parti.fragment and destinazione.suffix == ".html" and parti.fragment not in id_di(destinazione):
                        rotti.append(f"{nome(p)} riga {riga}: {pezzo} → manca l'ancora #{parti.fragment}")
    for x in rotti:
        print("ROTTO", x)
    print(f"Link: {len(rotti)} rotti; {len(esterni)} esterni:")
    for url, dove in sorted(esterni.items()):
        print(f"  {url}  ({', '.join(sorted(dove))})")
    return 1 if rotti else 0


if __name__ == "__main__":
    sys.exit(main())
