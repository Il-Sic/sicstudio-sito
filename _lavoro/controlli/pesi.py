"""I pesi (seconda passata): ogni pagina HTML sotto i 150 KB, i fogli di stile insieme sotto i 90 KB (erano 80 dal
7/11, con la casa che si apre e la carta vera; 90 dal 9/11, con il sole, la luna e le stelle che si accendono), ogni
immagine sotto i 250 KB, il sito intero sotto i 6 MB (senza _lavoro e .git). Dal 7/11 le copie AVIF e WebP delle
schermate (strumenti/schermate.py) contano a parte, sotto i 6 MB anche loro: sono alternative al JPEG, e chi apre una
pagina ne scarica una sola per schermata."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import file_del_sito, nome

KB = 1024
COPIE = (".avif", ".webp")


def main():
    problemi = 0
    tutti = list(file_del_sito())
    totale = sum(p.stat().st_size for p in tutti)
    css = sum(p.stat().st_size for p in tutti if p.suffix == ".css")
    copie = sum(p.stat().st_size for p in tutti if p.suffix.lower() in COPIE)
    for p in tutti:
        dim = p.stat().st_size
        if p.suffix == ".html" and dim > 150 * KB:
            print(f"TROPPO {nome(p)}: {dim / KB:.0f} KB (massimo 150)"); problemi += 1
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".svg", ".webp", ".avif", ".gif", ".ico") and dim > 250 * KB:
            print(f"TROPPO {nome(p)}: {dim / KB:.0f} KB (massimo 250)"); problemi += 1
    if css > 90 * KB:
        print(f"TROPPO i fogli di stile: {css / KB:.1f} KB (massimo 90)"); problemi += 1
    if totale - copie > 6 * KB * KB:
        print(f"TROPPO il sito: {(totale - copie) / KB / KB:.2f} MB senza le copie AVIF e WebP (massimo 6)"); problemi += 1
    if copie > 6 * KB * KB:
        print(f"TROPPO le copie AVIF e WebP: {copie / KB / KB:.2f} MB (massimo 6)"); problemi += 1
    piu = sorted(tutti, key=lambda p: -p.stat().st_size)[:8]
    print(f"Pesi: {len(tutti)} file, {totale / KB:.0f} KB in tutto, di cui {copie / KB:.0f} KB di copie AVIF e WebP; "
          f"CSS {css / KB:.1f} KB; i più grandi: "
          + ", ".join(f"{nome(p)} {p.stat().st_size / KB:.0f} KB" for p in piu))
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
