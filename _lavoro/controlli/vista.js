// Controllo di una vista, da lanciare nel browser dell'app sulla pagina aperta (non fa parte del sito).
// Dice: scorrimento laterale, testo sopra i disegni, testo tagliato, tocchi più piccoli di 44×44 px.
(() => {
  const r = (e) => e.getBoundingClientRect();
  const scorre = document.documentElement.scrollWidth > innerWidth + 1;
  const disegni = [...document.querySelectorAll('main img, main svg, main picture')]
    .filter((d) => !d.closest('a, button, summary') && !d.matches('picture img') && r(d).width > 0);
  const testi = [...document.querySelectorAll('main h1, main h2, main h3, main p, main li, main dt, main dd, main figcaption, main summary, main .etichetta, main .pulsante')]
    .filter((t) => r(t).width > 0 && t.textContent.trim());
  const sopra = [];
  for (const t of testi) {
    const a = r(t);
    for (const d of disegni) {
      if (t.contains(d) || d.contains(t)) continue;
      const b = r(d);
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w > 2 && h > 2) sopra.push(`${t.tagName.toLowerCase()} «${t.textContent.trim().slice(0, 30)}» su ${d.tagName.toLowerCase()}.${(d.getAttribute('class') || '').split(' ')[0]}`);
    }
  }
  const tagliati = [...document.querySelectorAll('body *')].filter((e) => {
    const s = getComputedStyle(e);
    return (s.overflowX === 'hidden' || s.overflowX === 'clip' || s.textOverflow === 'ellipsis') && e.scrollWidth > e.clientWidth + 1 && e.textContent.trim() && !e.matches('svg, svg *');
  }).map((e) => `${e.tagName.toLowerCase()}.${e.className}`);
  const piccoli = [...document.querySelectorAll('a, button, summary')].filter((e) => {
    const b = r(e);
    if (b.width === 0) return false;
    const inLinea = getComputedStyle(e).display === 'inline' && e.closest('p, li, dd, figcaption, td');
    return !inLinea && (b.height < 43.5 || b.width < 43.5);
  }).map((e) => `«${e.textContent.trim().slice(0, 24)}» ${Math.round(r(e).width)}×${Math.round(r(e).height)}`);
  return { larghezza: innerWidth, altezza: document.documentElement.scrollHeight, scorre, sopra, tagliati, piccoli };
})()
