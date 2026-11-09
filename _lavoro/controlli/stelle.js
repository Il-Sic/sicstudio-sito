// Le stelle del cielo della home e le parole del frontespizio (la frase e il titolo), per tutto lo scorrimento. Da
// incollare nel browser sulla home servita da 127.0.0.1:8765 (non fa parte del sito), nel tema scuro, alla misura che si
// vuole provare. Scorre il palco a passi di 2 px e, finché si vedono insieme stelle e parole, dice:
// - le stelle che toccano una riga, con 6 px di margine, nel cielo del frontespizio (anche quelle che tornano al loro
//   posto quando le parole se ne vanno, «sotto») e in quello della soglia (devono essere nessuna);
// - le righe nelle coordinate del cielo, con il margine. Quelle di tutte le misure le scrive in disegni/parole-fronte.json
//   strumenti/parole-fronte.js, che fa girare questo controllo da solo a 37 misure, con passi di 4 px; quelle misurate
//   qui a mano, sul Mac, vanno in PAROLE_MAC in disegni/casa.py.
// Dura meno di un minuto per misura, con la scheda in vista: in una scheda nascosta il browser ferma i fotogrammi, e
// con loro lo scorrimento.
(async () => {
  const MARGINE = 6, PASSO = window.PASSO_STELLE || 2;
  const fotogramma = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const palco = document.querySelector('.frontespizio-palco');
  const corsa = palco.offsetHeight - innerHeight + palco.getBoundingClientRect().top + scrollY;
  const parole = document.querySelector('.frontespizio-parole');
  const cieli = {
    frontespizio: '.frontespizio-paesaggio .volta-stelle', sotto: '.frontespizio-paesaggio .volta-sotto',
    soglia: '.soglia-disegno .volta-stelle',
  };
  const opacita = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentNode) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const testi = [];
  const giro = document.createTreeWalker(parole, NodeFilter.SHOW_TEXT);
  while (giro.nextNode()) if (giro.currentNode.textContent.trim()) testi.push(giro.currentNode);
  // Di chi è la riga: le due frasi, il titolo o la riga sotto il titolo.
  const elemento = (t) => {
    const e = t.parentElement.closest('h1, p');
    return e.tagName === 'H1' ? 'titolo' : e.className || 'sottotitolo';
  };
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
      if (!gruppo || opacita(gruppo) <= 0) continue;
      const m = gruppo.getScreenCTM();
      const disegno = gruppo.ownerSVGElement.getBoundingClientRect();
      [...gruppo.querySelectorAll('circle')].forEach((c, k) => {
        if (opacita(c) <= 0) return;
        const b = c.getBoundingClientRect();
        // Fuori dal suo disegno una stella non si vede: la taglia il bordo dell'SVG (con «Riduci movimento», il cielo
        // della soglia continua sopra il suo riquadro, dove c'è il titolo).
        if (b.bottom <= disegno.top || b.top >= disegno.bottom || b.right <= disegno.left || b.left >= disegno.right) return;
        for (const { testo, q } of linee) {
          if (b.right > q.left - MARGINE && b.left < q.right + MARGINE && b.bottom > q.top - MARGINE && b.top < q.bottom + MARGINE) {
            (sopra[`${nome} ${k}`] ||= new Set()).add(testo);
          }
        }
      });
      if (nome !== 'frontespizio') continue;
      for (const { chiave, q } of linee) {
        const nodo = testi[+chiave.split('.')[0]];
        const g = (righe[chiave] ||= Object.assign([Infinity, Infinity, -Infinity, -Infinity], {
          el: elemento(nodo), fs: parseFloat(getComputedStyle(nodo.parentElement).fontSize) / m.a,
        }));
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
    // Le stesse righe con l'elemento e la misura del carattere nel cielo, per parole-fronte.json.
    misure: Object.values(righe).map((g) => ({
      el: g.el, fs: Math.round(g.fs * 100) / 100,
      r: [Math.floor(g[0]), Math.floor(g[1]), Math.ceil(g[2]), Math.ceil(g[3])],
    })),
  };
})();
