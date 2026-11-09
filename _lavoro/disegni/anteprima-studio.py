"""L'anteprima dei link dello studio (img/anteprima-studio.jpg, 1200×630), per WhatsApp, iMessage e gli altri: il
paesaggio della prima schermata della home, di giorno, con la terra in alto come all'apertura (la casa, il sentiero, il
laghetto, la stella) e «Sic Studio» scritto nel cielo con il carattere dei titoli. La usano la home e lo studio, in
italiano e in inglese: il nome va bene in tutte e due le lingue.

    python3 -I _lavoro/disegni/anteprima-studio.py

Prende l'SVG dell'apertura da index.html, lo mette in una pagina di prova in _lavoro/prove (che usa style.css, senza
le animazioni), la fotografa con Chrome senza finestra (serve il server locale, servi.py), la fa JPEG con sips e le
toglie i metadati con strumenti/pulisci.py.
"""
import pathlib, re, subprocess, tempfile

QUI = pathlib.Path(__file__).resolve().parent
SITO = QUI.parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

svg = re.search(r'<svg class="frontespizio-paesaggio".*?</svg>', (SITO / "index.html").read_text(encoding="utf-8"), re.S).group(0)
pagina = SITO / "_lavoro" / "prove" / "anteprima-studio.html"
pagina.write_text(f'''<!doctype html>
<meta charset="utf-8">
<title>anteprima</title>
<!-- Scritta da _lavoro/disegni/anteprima-studio.py: non è una pagina del sito. -->
<link rel="stylesheet" href="/style.css">
<style>
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: var(--carta); }}
  .anteprima {{ position: relative; width: 1200px; height: 630px; overflow: hidden; }}
  .anteprima svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
  .anteprima, .anteprima * {{ animation: none !important; }}
  .anteprima .fr-terra {{ transform: none; }}
  .anteprima h1 {{ position: absolute; inset: 58px 0 auto; margin: 0; text-align: center; color: var(--testo);
                  font: 400 136px/1 var(--libro); letter-spacing: -0.035em; }}
</style>
<div class="anteprima">
{svg}
<h1>Sic Studio</h1>
</div>
''', encoding="utf-8")
with tempfile.TemporaryDirectory() as d:
    png = pathlib.Path(d) / "anteprima.png"
    subprocess.run([CHROME, "--headless=new", "--blink-settings=preferredColorScheme=1", f"--user-data-dir={d}/profilo",
                    "--no-first-run", "--hide-scrollbars", "--window-size=1200,630", "--virtual-time-budget=4000",
                    f"--screenshot={png}", "http://127.0.0.1:8765/_lavoro/prove/anteprima-studio.html"],
                   capture_output=True, timeout=90)
    jpg = SITO / "img" / "anteprima-studio.jpg"
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", str(png), "--out", str(jpg)], capture_output=True)
subprocess.run(["python3", "-I", str(SITO / "_lavoro" / "strumenti" / "pulisci.py"), str(jpg)])
print(jpg.relative_to(SITO), jpg.stat().st_size // 1024, "KB")
