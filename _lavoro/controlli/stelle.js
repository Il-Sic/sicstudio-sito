// Le stelle del cielo della home e le parole del frontespizio (la frase e il titolo), per tutto lo scorrimento. Da
// incollare nel browser sulla home servita da 127.0.0.1:8765 (non fa parte del sito), nel tema scuro, a una misura alla
// volta: 390×844, 375×667 e 1440×900. Scorre il palco a passi di 2 px e, finché si vedono insieme stelle e parole, dice:
// - le stelle che toccano una riga, con 6 px di margine, nel cielo del frontespizio e in quello della soglia (devono
//   essere nessuna);
// - le righe nelle coordinate del cielo, con il margine: quando cambiano le parole o le loro misure in style.css, si
//   rimisura alle tre misure e si scrivono in PAROLE_FRONTE in _lavoro/disegni/casa.py.
// Dura meno di un minuto per misura, con la scheda in vista: in una scheda nascosta il browser ferma i fotogrammi, e
// con loro lo scorrimento.
(async () => {
  const MARGINE = 6, PASSO = 2;
  const fotogramma = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const palco = document.querySelector('.frontespizio-palco');
  const corsa = palco.offsetHeight - innerHeight + palco.getBoundingClientRect().top + scrollY;
  const parole = document.querySelector('.frontespizio-parole');
  const cieli = { frontespizio: '.frontespizio-paesaggio .volta-stelle', soglia: '.soglia-disegno .volta-stelle' };
  const opacita = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentNode) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const testi = [];
  const giro = document.createTreeWalker(parole, NodeFilter.SHOW_TEXT);
  while (giro.nextNode()) if (giro.currentNode.textContent.trim()) testi.push(giro.currentNode);
  const sopra = {}, righe = {};
  for (let y = 0; y <= corsa; y += PASSO) {
    scrollTo(0, y);
    await fotogramma();
    if (opacita(parole) <= 0) continue;
    const linee = [];
    testi.forEach((t, i) => {
      const o = opacita(t.parentElement);
      if (o <= 0) return;
      const r = document.createRange();
      r.selectNodeContents(t);
      [...r.getClientRects()].forEach((q, j) => { if (q.width >= 1) linee.push({ chiave: `${i}.${j}`, testo: t.textContent.trim(), q, o }); });
    });
    for (const [nome, sel] of Object.entries(cieli)) {
      const gruppo = document.querySelector(sel);
      const oS = opacita(gruppo);
      if (oS <= 0) continue;
      const m = gruppo.getScreenCTM();
      [...gruppo.children].forEach((c, k) => {
        const b = c.getBoundingClientRect();
        for (const { testo, q } of linee) {
          if (b.right > q.left - MARGINE && b.left < q.right + MARGINE && b.bottom > q.top - MARGINE && b.top < q.bottom + MARGINE) {
            (sopra[`${nome} ${k}`] ||= new Set()).add(testo);
          }
        }
      });
      if (nome !== 'frontespizio') continue;
      for (const { chiave, q } of linee) {
        const g = (righe[chiave] ||= [Infinity, Infinity, -Infinity, -Infinity]);
        const x0 = (q.left - MARGINE - m.e) / m.a, y0 = (q.top - MARGINE - m.f) / m.d;
        const x1 = (q.right + MARGINE - m.e) / m.a, y1 = (q.bottom + MARGINE - m.f) / m.d;
        g[0] = Math.min(g[0], x0); g[1] = Math.min(g[1], y0); g[2] = Math.max(g[2], x1); g[3] = Math.max(g[3], y1);
      }
    }
  }
  scrollTo(0, 0);
  const stelleSulleParole = Object.entries(sopra).map(([k, s]) => `${k}: ${[...s].join(' / ')}`);
  return {
    misura: `${innerWidth}×${innerHeight}`,
    stelleSulleParole: stelleSulleParole.length ? stelleSulleParole : 'nessuna',
    righe: Object.values(righe).map((g) => `(${Math.floor(g[0])}, ${Math.floor(g[1])}, ${Math.ceil(g[2])}, ${Math.ceil(g[3])})`).join(', '),
  };
})();
