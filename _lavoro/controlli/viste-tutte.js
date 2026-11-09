// Il controllo delle viste su tutte le pagine, a 320, 375, 768, 1280 e 1920 px: le apre una alla volta in un iframe
// nascosto della larghezza giusta. Da incollare nel browser dell'app su una pagina del sito servita da
// 127.0.0.1:8765 (non fa parte del sito). Dice: scorrimento laterale, testo sopra i disegni, tocchi sotto 44 px.
// Tutto insieme dura circa 50 s: nel browser dell'app di Claude, che ferma un comando dopo 45 s, si fa una larghezza
// alla volta (circa 10 s ciascuna).
const pagine = ['/', '/studio/', '/argonauta/', '/argonauta/il-mito/', '/argonauta/aiuto/', '/argonauta/privacy/', '/404.html', '/en/', '/en/studio/', '/en/argonauta/', '/en/argonauta/the-myth/', '/en/argonauta/help/'];
const tutti = {};
for (const larghezza of [320, 375, 768, 1280, 1920]) {
  const risultati = {};
  for (const p of pagine) {
    const f = document.createElement('iframe');
    f.style.cssText = 'position:absolute;left:-9999px;top:0;width:' + larghezza + 'px;height:700px;border:0';
    f.src = p + (p.includes('?') ? '&' : '?') + 'v=' + Date.now(); document.body.appendChild(f);
    await new Promise(r => f.onload = r); await new Promise(r => setTimeout(r, 250));
    const d = f.contentDocument, w = f.contentWindow, r = (e) => e.getBoundingClientRect();
    const scorre = d.documentElement.scrollWidth > w.innerWidth + 1;
    const disegni = [...d.querySelectorAll('main img, main svg, main picture')].filter((x) => !x.closest('a, button, summary, .frontespizio-fermo, .meridiana, .crescita-stati, .carta-mappa') && !x.matches('picture img, .marchio, .marchio *') && r(x).width > 0);
    const testi = [...d.querySelectorAll('main h1, main h2, main h3, main p, main li, main dt, main dd, main figcaption, main summary, main .etichetta, main .pulsante')].filter((t) => r(t).width > 0 && t.textContent.trim());
    let sopra = [];
    for (const t of testi) { const a = r(t); for (const x of disegni) { if (t.contains(x) || x.contains(t)) continue; const b = r(x); if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2) sopra.push(t.textContent.trim().slice(0, 20) + '/' + (x.getAttribute('class') || x.tagName)); } }
    const piccoli = [...d.querySelectorAll('a, button, summary')].filter((e) => { const b = r(e); if (b.width === 0) return false; const inLinea = (w.getComputedStyle(e).display === 'inline' || e.matches('.parola')) && e.closest('p, li, dd, figcaption, td'); return !inLinea && (b.height < 43.5 || b.width < 43.5); }).map((e) => e.textContent.trim().slice(0, 20));
    const esito = (scorre ? 'SCORRE ' : '') + (sopra.length ? 'sopra:' + sopra.join('|') + ' ' : '') + (piccoli.length ? 'piccoli:' + piccoli.join('|') : '');
    if (esito) risultati[p] = esito;
    f.remove();
  }
  tutti[larghezza] = Object.keys(risultati).length ? risultati : 'tutto ok';
}
tutti
