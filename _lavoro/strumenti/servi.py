"""Il server locale per guardare il sito, senza cache: ogni pagina e ogni foglio si rileggono dal disco.

    python3 -I _lavoro/strumenti/servi.py           (dalla cartella del sito; http://127.0.0.1:8765/)
    /usr/bin/python3 -I _lavoro/strumenti/servi.py --rete
                    (anche dagli apparecchi della Wi-Fi di casa, per guardarlo in Safari sull'iPhone:
                    http://<indirizzo del Mac>:8765/, con l'indirizzo che dà «ipconfig getifaddr en0». Con il Python di
                    Apple, che il firewall del Mac lascia passare; quello di Homebrew resta fermo ad aspettare il permesso)

Dagli altri apparecchi si vedono solo i file che vanno online: niente _lavoro, niente .git e niente file nascosti (dal
Mac stesso anche le pagine di prova in _lavoro).
"""
import functools, http.server, pathlib, sys, urllib.parse

SITO = pathlib.Path(__file__).resolve().parents[2]
RETE = "--rete" in sys.argv


class SenzaCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        if RETE and self.client_address[0] not in ("127.0.0.1", "::1"):
            percorso = urllib.parse.unquote(self.path.split("?", 1)[0].split("#", 1)[0])
            if any(pezzo.startswith((".", "_")) for pezzo in percorso.split("/")):
                self.send_error(404)
                return None
        return super().send_head()

    def send_error(self, code, message=None, explain=None):
        """Come GitHub Pages: per un indirizzo che non c'è, «Fuori rotta» (404.html) con il codice 404."""
        pagina = SITO / "404.html"
        if code == 404 and pagina.exists():
            corpo = pagina.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(corpo)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    gestore = functools.partial(SenzaCache, directory=str(SITO))
    http.server.ThreadingHTTPServer(("0.0.0.0" if RETE else "127.0.0.1", 8765), gestore).serve_forever()
