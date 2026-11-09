// Le righe delle parole del frontespizio a tante misure di schermo, per le stelle di disegni/casa.py: apre la home
// servita da 127.0.0.1:8765 (strumenti/servi.py) in Chromium, nel tema scuro, a ogni misura di MISURE, e ci fa girare
// controlli/stelle.js con passi di 4 px. Scrive le righe in disegni/parole-fronte.json e dice, misura per misura, le
// stelle che toccano le parole (devono essere nessuna). Quando cambiano le parole o le loro misure in style.css: si
// lancia, si rilancia casa.py, che sposta le stelle, e si lancia di nuovo per controllare.
//
//     node _lavoro/strumenti/parole-fronte.js
//
// Serve Node con Playwright e il suo Chromium (ci sono nella sessione cloud di Claude Code). Quattro schede alla volta:
// dura una decina di minuti.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const LAVORO = path.resolve(__dirname, '..');
const SITO = 'http://127.0.0.1:8765/';
// La finestra del browser, senza le sue barre: telefoni (anche con le barre di Safari aperte), tablet e computer.
const MISURE = [
  '360x640', '360x780', '375x667', '375x812', '390x664', '390x844', '393x660', '393x852', '402x874', '412x915',
  '430x739', '430x932', '440x956',
  '768x1024', '820x1180', '834x1194', '1024x768', '1024x1366', '1180x820',
  '1024x640', '1152x700', '1280x600', '1280x720', '1280x800', '1366x657', '1440x789', '1440x900', '1470x835',
  '1512x865', '1512x982', '1536x730', '1600x900', '1680x939', '1728x995', '1920x960', '1920x1080', '2560x1300',
];
const STELLE = fs.readFileSync(path.join(LAVORO, 'controlli', 'stelle.js'), 'utf8');

async function misura(browser, m) {
  const [larga, alta] = m.split('x').map(Number);
  const telefono = larga < 800;
  const ctx = await browser.newContext({
    viewport: { width: larga, height: alta }, colorScheme: 'dark', isMobile: telefono, hasTouch: telefono,
  });
  const pagina = await ctx.newPage();
  await pagina.goto(SITO, { waitUntil: 'load' });
  await pagina.evaluate(() => { window.PASSO_STELLE = 4; });
  const esito = await pagina.evaluate(STELLE);
  await ctx.close();
  return esito;
}

(async () => {
  const browser = await chromium.launch();
  const righe = {}, coda = [...MISURE];
  let sopra = 0;
  const scheda = async () => {
    for (let m; (m = coda.shift()); ) {
      const esito = await misura(browser, m);
      righe[m] = esito.misure;
      const s = esito.stelleSulleParole;
      if (s !== 'nessuna') sopra += s.length;
      console.log(`${m.replace('x', '×')}: ${s === 'nessuna' ? 'nessuna stella sulle parole' : s.join('; ')}`);
    }
  };
  await Promise.all([scheda(), scheda(), scheda(), scheda()]);
  const versione = browser.version();
  await browser.close();
  const giorno = new Date().toISOString().slice(0, 10);
  const misurate = JSON.stringify(`${giorno}, Chromium ${versione} su ${process.platform}`);
  const testa = `{\n "misurate": ${misurate},\n "misure": {\n`;
  const corpo = MISURE.map((m) => `  "${m.replace('x', '×')}": [\n`
    + righe[m].map((r) => `   ${JSON.stringify(r)}`).join(',\n') + '\n  ]').join(',\n');
  fs.writeFileSync(path.join(LAVORO, 'disegni', 'parole-fronte.json'), `${testa}${corpo}\n }\n}\n`);
  console.log(sopra ? `${sopra} stelle sulle parole` : 'Nessuna stella sulle parole, a nessuna misura.');
  process.exitCode = sopra ? 1 : 0;
})();
