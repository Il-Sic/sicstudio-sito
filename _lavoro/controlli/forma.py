"""HTML ben formato: tag chiusi, id unici, un solo h1, alt su ogni immagine, lang sull'html."""
import collections, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import pagine, leggi, nome


def main():
    problemi = 0
    for p in pagine():
        albero = leggi(p)
        errori = list(albero.errori)
        aperti = [n for n, _ in albero.aperti if n not in ("html", "body", "head")]
        if aperti:
            errori.append(f"tag non chiusi alla fine: {aperti}")
        ids = collections.Counter(a["id"] for _, a, _ in albero.tag if "id" in a)
        errori += [f"id ripetuto: {i} ({c} volte)" for i, c in ids.items() if c > 1]
        h1 = sum(1 for n, _, _ in albero.tag if n == "h1")
        if h1 != 1:
            errori.append(f"{h1} h1 invece di uno")
        for n, a, riga in albero.tag:
            if n == "img" and "alt" not in a:
                errori.append(f"riga {riga}: <img> senza alt")
            if n == "svg" and a.get("aria-hidden") != "true" and a.get("role") != "img" and not a.get("aria-label"):
                errori.append(f"riga {riga}: <svg> né decorativo (aria-hidden) né con un nome (role=img e aria-label)")
        for e in errori:
            print(f"{nome(p)}: {e}")
        problemi += len(errori)
    print(f"Forma dell'HTML: {len(pagine())} pagine, {problemi} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
