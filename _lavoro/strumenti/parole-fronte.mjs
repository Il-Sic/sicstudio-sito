// Le righe delle parole del frontespizio (la frase, il titolo, la riga sotto) a tante misure di finestra, in italiano e
// in inglese, per le stelle della tavola del giorno: disegni/tavola.py accende solo dopo che le parole se ne sono
// andate le stelle che cadrebbero su una riga, a una qualunque di queste misure (una stella accanto a una parola
// sembra un punto o un accento).
//
//     node _lavoro/strumenti/parole-fronte.mjs               misura, e scrive disegni/parole-fronte.json
//     node _lavoro/strumenti/parole-fronte.mjs --controlla   guarda la prova (tavola.py --prova) a queste misure e ad
//                                                            altre mai misurate: nessuna stella deve toccare una parola
//
// Si rilancia quando cambiano le parole o le loro misure in style.css; poi «tavola.py --prova» e «--controlla».
// Servono Node 22 o più, Google Chrome (lo guida senza finestra, dal suo protocollo di debug) e il server del sito
// acceso (strumenti/servi.py). Va fatto su un Mac: le parole sono in Iowan Old Style, che c'è solo sui dispositivi
// Apple, e con un altro carattere le righe cadono altrove. Dura qualche minuto.
//
// Le righe sono nelle coordinate del disegno (il viewBox 1440×900 del paesaggio), per tutto lo scorrimento in cui le
// parole si vedono, con 6 px di margine.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const LAVORO = join(dirname(fileURLToPath(import.meta.url)), '..');
const SITO = 'http://127.0.0.1:8765';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PAGINE = { it: '/', en: '/en/' };
// La finestra del browser senza le sue barre: telefoni (anche con le barre di Safari aperte), tablet e computer.
const MISURE = [
  '360x640', '360x780', '375x548', '375x580', '375x667', '375x812', '390x659', '390x664', '390x844', '393x660',
  '393x852', '402x681', '402x874', '412x915', '430x739', '430x932', '440x956',
  '768x1024', '820x1180', '834x1194', '1024x768', '1024x1366', '1180x820',
  '1024x640', '1152x700', '1280x600', '1280x720', '1280x800', '1366x657', '1440x789', '1440x900', '1470x835',
  '1512x865', '1512x982', '1536x730', '1600x900', '1680x939', '1728x995', '1920x960', '1920x1080', '2560x1300',
];
// Misure mai misurate, per il controllo: se il margine non basta, qui si vede.
const ALTRE = ['384x700', '400x760', '414x896', '428x780', '800x1100', '1100x720', '1300x760', '1400x850', '1800x1000', '2048x1100'];
const MARGINE = 6, PASSO = 6;
const aspetta = (ms) => new Promise((ok) => setTimeout(ok, ms));

async function chrome() {
  const profilo = mkdtempSync(join(tmpdir(), 'parole-'));
  const processo = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profilo}`, '--no-first-run',
    '--disable-extensions', '--hide-scrollbars', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const indirizzo = await new Promise((ok, no) => {
    let testo = '';
    processo.stderr.on('data', (d) => { testo += d; const m = testo.match(/DevTools listening on (ws:\/\/\S+)/); if (m) ok(m[1]); });
    setTimeout(() => no(new Error('Chrome non risponde')), 20000);
  });
  const schede = await (await fetch(`http://127.0.0.1:${new URL(indirizzo).port}/json/list`)).json();
  const ws = new WebSocket(schede.find((s) => s.type === 'page').webSocketDebuggerUrl);
  await new Promise((ok) => ws.addEventListener('open', ok, { once: true }));
  let n = 0, caricata = null;
  const attese = new Map();
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && attese.has(m.id)) { const a = attese.get(m.id); attese.delete(m.id); m.error ? a.no(new Error(m.error.message)) : a.ok(m.result); }
    else if (m.method === 'Page.loadEventFired' && caricata) caricata();
  });
  const cdp = (method, params = {}) => new Promise((ok, no) => { const i = ++n; attese.set(i, { ok, no }); ws.send(JSON.stringify({ id: i, method, params })); });
  await cdp('Page.enable');
  await cdp('Runtime.enable');
  return {
    // apre una pagina a una misura, nel tema scuro (dove ci sono le stelle), e ci fa girare una funzione
    async guarda(url, misura, funzione, ...argomenti) {
      const [w, h] = misura.split('x').map(Number);
      await cdp('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 800 });
      await cdp('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'dark' }, { name: 'prefers-reduced-motion', value: 'no-preference' }] });
      const fatta = new Promise((ok) => { caricata = ok; });
      await cdp('Page.navigate', { url });
      await Promise.race([fatta, aspetta(15000)]);
      const r = await cdp('Runtime.evaluate', { expression: `(${funzione})(${argomenti.map((a) => JSON.stringify(a)).join(', ')})`, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(`${url} a ${misura}: ${JSON.stringify(r.exceptionDetails).slice(0, 600)}`);
      return r.result.value;
    },
    async chiudi() { ws.close(); processo.kill(); await aspetta(300); rmSync(profilo, { recursive: true, force: true }); },
  };
}

// Gira nella pagina. Scorre il frontespizio finché le parole si vedono; a ogni passo prende i rettangoli delle righe.
// Se «controlla», conta anche le stelle della tavola che in quel momento si vedono e toccano una riga.
async function nellaPagina(passo, margine, controlla) {
  await document.fonts.ready;
  const fotogramma = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const palco = document.querySelector('.frontespizio-palco');
  const disegno = document.querySelector('.frontespizio-paesaggio');
  const parole = document.querySelector('.frontespizio-parole');
  const corsa = palco.offsetHeight - innerHeight + palco.getBoundingClientRect().top + scrollY;
  const opacita = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentNode) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const testi = [];
  const giro = document.createTreeWalker(parole, NodeFilter.SHOW_TEXT);
  while (giro.nextNode()) if (giro.currentNode.textContent.trim()) testi.push(giro.currentNode);
  const righe = {}, toccano = new Set();
  // le stelle e i pianeti del cielo che si vede a questa misura (largo o stretto)
  const cielo = controlla && [...disegno.querySelectorAll('.tv-largo, .tv-stretto')].find((g) => getComputedStyle(g).display !== 'none');
  const stelle = [];
  if (cielo) {
    for (const p of cielo.querySelectorAll('path[class^="tv-s"]')) {
      for (const m of p.getAttribute('d').matchAll(/M(-?[\d.]+) (-?[\d.]+)h0/g)) stelle.push({ el: p, x: +m[1], y: +m[2], r: parseFloat(getComputedStyle(p).strokeWidth) / 2 });
    }
    for (const c of cielo.querySelectorAll('circle[class^="tv-"]')) stelle.push({ el: c, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r') });
  }
  for (let y = 0; y <= corsa; y += passo) {
    scrollTo(0, y);
    await fotogramma();
    if (opacita(parole) <= 0.01) { if (y > corsa * 0.3) break; continue; }
    const m = disegno.getScreenCTM();
    const linee = [];
    testi.forEach((t, i) => {
      if (opacita(t.parentElement) <= 0.01) return;
      const r = document.createRange();
      r.selectNodeContents(t);
      [...r.getClientRects()].forEach((q, j) => {
        if (q.width < 1) return;
        linee.push(q);
        const g = (righe[`${i}.${j}`] ||= [Infinity, Infinity, -Infinity, -Infinity]);
        g[0] = Math.min(g[0], (q.left - margine - m.e) / m.a); g[1] = Math.min(g[1], (q.top - margine - m.f) / m.d);
        g[2] = Math.max(g[2], (q.right + margine - m.e) / m.a); g[3] = Math.max(g[3], (q.bottom + margine - m.f) / m.d);
      });
    });
    for (const s of stelle) {
      if (opacita(s.el) <= 0.05) continue;
      const k = s.el.getScreenCTM();
      const sx = k.a * s.x + k.c * s.y + k.e, sy = k.b * s.x + k.d * s.y + k.f, sr = s.r * Math.hypot(k.a, k.b);
      // una stella conta se tocca il rettangolo delle lettere, stretto di un quinto sopra e sotto (lì c'è l'interlinea)
      if (linee.some((q) => sx + sr > q.left - 2 && sx - sr < q.right + 2 && sy + sr > q.top + q.height * 0.2 && sy - sr < q.bottom - q.height * 0.2)) {
        toccano.add(`${Math.round(s.x)},${Math.round(s.y)}`);
      }
    }
  }
  scrollTo(0, 0);
  return {
    righe: Object.values(righe).map((g) => [Math.floor(g[0]), Math.floor(g[1]), Math.ceil(g[2]), Math.ceil(g[3])]),
    stelle: stelle.length, toccano: [...toccano],
  };
}

const controlla = process.argv.includes('--controlla');
const b = await chrome();
let problemi = 0;
try {
  if (controlla) {
    for (const [lingua, pagina] of Object.entries(PAGINE)) {
      for (const m of [...MISURE, ...ALTRE]) {
        const e = await b.guarda(`${SITO}/_lavoro/prove/tavola${pagina}`, m, nellaPagina, PASSO, MARGINE, true);
        if (!e.stelle) { console.log(`${lingua} ${m}: non trovo il cielo della tavola (prima «tavola.py --prova»)`); problemi++; continue; }
        if (e.toccano.length) { console.log(`${lingua} ${m.replace('x', '×')}: ${e.toccano.length} stelle sulle parole, a ${e.toccano.join(' ')}`); problemi += e.toccano.length; }
      }
    }
    console.log(problemi ? `${problemi} problemi` : `Nessuna stella sulle parole: ${MISURE.length + ALTRE.length} misure, due lingue.`);
  } else {
    const righe = {};
    for (const [lingua, pagina] of Object.entries(PAGINE)) {
      righe[lingua] = {};
      for (const m of MISURE) {
        righe[lingua][m.replace('x', '×')] = (await b.guarda(SITO + pagina, m, nellaPagina, PASSO, MARGINE, false)).righe;
        process.stdout.write('.');
      }
    }
    const versione = (await (await fetch(`${SITO}/`)).text()).length;   // solo per accorgersi se il server è spento
    if (!versione) throw new Error('il server del sito non risponde');
    const giorno = new Date().toISOString().slice(0, 10);
    const corpo = Object.entries(righe).map(([lingua, misure]) => `  "${lingua}": {\n`
      + Object.entries(misure).map(([m, r]) => `   "${m}": ${JSON.stringify(r)}`).join(',\n') + '\n  }').join(',\n');
    writeFileSync(join(LAVORO, 'disegni', 'parole-fronte.json'),
      `{\n "misurate": "${giorno}, Google Chrome su ${process.platform}, con Iowan Old Style",\n "righe": {\n${corpo}\n }\n}\n`);
    const quante = Object.values(righe).flatMap((l) => Object.values(l)).reduce((a, r) => a + r.length, 0);
    console.log(`\nparole-fronte.json: ${quante} righe, ${MISURE.length} misure, due lingue`);
    if (Object.values(righe).some((l) => Object.values(l).some((r) => r.length < 5))) { console.log('A qualche misura ci sono meno di cinque righe: la pagina è cambiata?'); problemi++; }
  }
} finally {
  await b.chiudi();
}
process.exitCode = problemi ? 1 : 0;
