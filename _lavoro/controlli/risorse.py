"""Niente risorse da altri siti, niente script, attributi on…, style= o <style>; in ogni pagina le meta richieste.
Fanno eccezione solo i dati strutturati (<script type="application/ld+json"> senza src), che il browser non esegue.

Le meta: charset per prima, subito dopo la Content-Security-Policy esatta e il referrer; poi viewport, lang,
title, description, canonical, theme-color per chiaro e scuro e color-scheme.
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comune import SITO, pagine, file_del_sito, leggi, nome

CSP = ("default-src 'self'; img-src 'self' data:; script-src 'none'; object-src 'none'; "
       "base-uri 'none'; form-action 'none'")
ESTERNO = re.compile(r"^(https?:)?//", re.I)


def controlla_pagina(p):
    problemi = []
    testo = p.read_text(encoding="utf-8")
    albero = leggi(p)
    tag = albero.tag
    # L'ordine delle prime meta.
    meta = [(n, a) for n, a, _ in tag if n == "meta"]
    if not meta or "charset" not in meta[0][1]:
        problemi.append("la prima meta non è il charset")
    if len(meta) < 3 or meta[1][1].get("http-equiv", "").lower() != "content-security-policy" or meta[1][1].get("content") != CSP:
        problemi.append("subito dopo il charset manca la Content-Security-Policy esatta")
    if len(meta) < 3 or meta[2][1].get("name") != "referrer" or meta[2][1].get("content") != "no-referrer":
        problemi.append("dopo la CSP manca <meta name=\"referrer\" content=\"no-referrer\">")
    nomi_meta = {a.get("name") for _, a in meta}
    for richiesto in ("viewport", "description", "color-scheme"):
        if richiesto not in nomi_meta:
            problemi.append(f"manca la meta {richiesto}")
    temi = [a for _, a in meta if a.get("name") == "theme-color"]
    if len(temi) < 2 or not any("dark" in (a.get("media") or "") for a in temi) or not any("light" in (a.get("media") or "") for a in temi):
        problemi.append("mancano i theme-color per chiaro e scuro")
    html = [a for n, a, _ in tag if n == "html"]
    if not html or not html[0].get("lang"):
        problemi.append("manca lang su <html>")
    if not any(n == "title" for n, _, _ in tag):
        problemi.append("manca <title>")
    if not any(n == "link" and "canonical" in (a.get("rel") or "") for n, a, _ in tag) and p.name != "404.html":
        problemi.append("manca il link canonical")
    # Niente script, stili in linea o gestori di eventi.
    for n, a, riga in tag:
        if n in ("script", "style", "iframe", "form", "object", "embed"):
            if n == "script" and a.get("type") == "application/ld+json" and set(a) == {"type"}:
                continue                      # dati strutturati: il browser non li esegue
            problemi.append(f"riga {riga}: <{n}>")
        for chiave in a:
            if chiave.lower().startswith("on"):
                problemi.append(f"riga {riga}: attributo {chiave} su <{n}>")
            if chiave.lower() == "style":
                problemi.append(f"riga {riga}: attributo style su <{n}>")
        for chiave in ("src", "href", "srcset", "xlink:href", "poster", "data"):
            valore = a.get(chiave)
            if not valore:
                continue
            esterno = any(ESTERNO.match(v.strip().split(" ")[0]) for v in valore.split(","))
            if n == "a" and chiave == "href":
                continue                      # i link verso altri siti vanno bene
            if n == "link" and "canonical" in (a.get("rel") or "") or n == "link" and "alternate" in (a.get("rel") or ""):
                continue                      # indirizzi, non risorse
            if n == "meta":
                continue
            if esterno:
                problemi.append(f"riga {riga}: risorsa da un altro sito su <{n} {chiave}=\"{valore}\">")
    if re.search(r"javascript:", testo, re.I):
        problemi.append("un indirizzo javascript:")
    return problemi


def controlla_css(p):
    problemi = []
    for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)", p.read_text(encoding="utf-8")):
        if ESTERNO.match(m.group(1)):
            problemi.append(f"url() da un altro sito: {m.group(1)}")
    if re.search(r"@import", p.read_text(encoding="utf-8")):
        problemi.append("@import")
    return problemi


def controlla_svg(p):
    problemi = []
    t = p.read_text(encoding="utf-8")
    if re.search(r"<script|\son\w+=", t, re.I):
        problemi.append("script o gestori di eventi")
    for m in re.finditer(r"(?:href|src)=\"([^\"]+)\"", t):
        if ESTERNO.match(m.group(1)) and "www.w3.org" not in m.group(1):
            problemi.append(f"risorsa da un altro sito: {m.group(1)}")
    return problemi


def main():
    totale = 0
    for p in pagine():
        problemi = controlla_pagina(p)
        totale += len(problemi)
        for x in problemi:
            print(f"{nome(p)}: {x}")
    for p in file_del_sito(".css"):
        for x in controlla_css(p):
            totale += 1
            print(f"{nome(p)}: {x}")
    for p in file_del_sito(".svg"):
        for x in controlla_svg(p):
            totale += 1
            print(f"{nome(p)}: {x}")
    print(f"Risorse e meta: {len(pagine())} pagine, {totale} problemi")
    return 1 if totale else 0


if __name__ == "__main__":
    sys.exit(main())
