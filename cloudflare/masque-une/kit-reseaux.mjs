const media = 'https://velocemercato.fr';
const univers = 'https://vmunivers.fr';
const studio = media + '/web-studio#tarifs';
const formats = media + '/pub/#packs';
const calendar = new Intl.DateTimeFormat('fr-CA', { timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit' });
const displayDate = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', dateStyle: 'long' });
const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

function titleOf(row) {
  const names = { amp: '&', quot: '"', apos: "'", lt: '<', gt: '>', nbsp: ' ' };
  return row.titre.replace(/&(#x[0-9a-f]+|#\d+|amp|quot|apos|lt|gt|nbsp);/gi, (entity, value) => {
    const key = value.toLowerCase();
    if (key[0] !== '#') return names[key] ?? entity;
    const code = key[1] === 'x' ? Number.parseInt(key.slice(2), 16) : Number(key.slice(1));
    return code > 0 && code <= 0x10ffff && !(code >= 0xd800 && code <= 0xdfff) ? String.fromCodePoint(code) : entity;
  }).trim();
}

async function latest(path, today, now) {
  try {
    const response = await fetch(media + path, { signal: AbortSignal.timeout(5000), cf: { cacheTtl: 180 } });
    if (!response.ok) return null;
    const rows = await response.json();
    if (!Array.isArray(rows)) return null;
    return rows.filter(row => {
      const time = Date.parse(row?.publishedAt);
      return Number.isFinite(time) && time <= now.getTime() && calendar.format(time) === today &&
        typeof row.titre === 'string' && row.titre.trim() && row.sources?.some(source => typeof source?.url === 'string' && source.url.startsWith('https://'));
    }).sort((a, b) => Date.parse(b.publishedAt) - Date.parse(a.publishedAt))[0] ?? null;
  } catch {
    return null;
  }
}

export async function renderKit(now = new Date(), analysis = null) {
  const today = calendar.format(now);
  const [foot, news] = await Promise.all([latest('/articles.json', today, now), latest('/vm-gaming/news.json', today, now)]);
  const cards = [
    { brand: 'Véloce Mercato', headline: 'Le foot et le sport au quotidien', link: media + '/#feed-title', visual: foot ? titleOf(foot) : null,
      text: foot ? '⚽ À lire sur Véloce Mercato aujourd’hui. ' + titleOf(foot).slice(0, 220) + ' · Retrouvez aussi les résultats et le multisport.': '⚽ Foot, résultats, mercato et multisport. Retrouve les derniers titres et les Pastilles de Véloce Mercato.' },
    { brand: 'VM Univers', headline: 'Les médias et services VM', link: univers + '/', visual: news ? titleOf(news) : null,
      text: (news ? '🎮 Côté gaming aujourd’hui : ' + titleOf(news).slice(0, 220) + ' · ' : '') + 'Découvre VM Univers, le portail des médias, applications et services VM.' },
    { brand: 'VM Studio', headline: 'Un site pour ton activité', link: studio,
      text: '🛠️ Artisan, club ou commerce ? VM Studio crée des sites à partir de 290 €. Découvrez les modèles et les formules, puis demandez un devis.' },
    { brand: 'Véloce Mercato × VM Univers', headline: 'Fais connaître ton activité', link: formats,
      text: '📣 Un événement, une ouverture ou une offre locale ? Découvrez les encarts VM Belfort à 29 €/mois, les encarts sur un média VM à 39 €/mois et les formats réseaux sur devis selon le canal.' }
  ];
  if (analysis) {
    const kickoff = new Intl.DateTimeFormat('fr-FR', {
      dateStyle: 'full', timeStyle: 'short', timeZone: 'Europe/Paris'
    }).format(analysis.kickoff);
    cards.push({
      brand: 'VM Multisport',
      headline: 'Analyse sportive',
      visual: analysis.match,
      link: media + '/pronos/#pronos-du-jour',
      text: '🏟️ Avant-match VM · ' + analysis.match + ' · ' + kickoff + ' (Paris). ' +
        analysis.analysis + ' Sources : ' + analysis.sources.map(source => source.name).join(', ') + '.'
    });
  }
  const markup = cards.map(card => '<article data-visual="' + escape(card.visual ? card.visual.length > 68 ? card.visual.slice(0, 65).replace(/\s+\S*$/, '') + '…' : card.visual : card.headline) + '"><small>' + escape(card.brand) + '</small><h2>' + escape(card.headline) + '</h2><p class="copy">' + escape(card.text) + '</p><a class="destination" href="' + escape(card.link) + '">' + escape(card.link) + '</a><div class="actions"><button type="button" data-action="copy">Copier le texte</button><button type="button" data-action="image">Télécharger le visuel</button></div><p class="status" role="status"></p></article>').join('');
  const script = `
  document.querySelectorAll('article').forEach(card => {
    const status = card.querySelector('.status');
    card.addEventListener('click', async event => {
      const action = event.target.dataset.action;
      if (!action) return;
      const url = card.querySelector('.destination').href;
      if (action === 'copy') {
        try {
          await navigator.clipboard.writeText(card.querySelector('.copy').textContent + '\\n' + url);
          status.textContent = 'Texte et lien copiés.';
          event.target.textContent = 'Copié ✓';
          setTimeout(() => { event.target.textContent = 'Copier le texte'; }, 2000);
        } catch {
          status.textContent = 'Tu peux sélectionner le texte et le lien pour les copier.';
        }
        return;
      }
      const canvas = document.createElement('canvas');
      canvas.width = 1080;
      canvas.height = 1350;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#101930'; ctx.fillRect(0, 0, 1080, 1350);
      ctx.strokeStyle = '#263966'; ctx.lineWidth = 8;
      for (let x = -550; x < 1500; x += 95) {
        ctx.beginPath(); ctx.moveTo(x, 760); ctx.lineTo(x + 750, 0); ctx.stroke();
      }
      ctx.fillStyle = '#ffc957'; ctx.fillRect(72, 88, 930, 96);
      ctx.fillStyle = '#101930'; ctx.font = 'bold 42px sans-serif';
      ctx.fillText(card.querySelector('small').textContent, 104, 150, 864);
      ctx.fillStyle = '#d74352';
      ctx.beginPath(); ctx.moveTo(108, 690); ctx.lineTo(365, 351); ctx.lineTo(584, 548); ctx.lineTo(872, 297); ctx.lineTo(984, 690); ctx.fill();
      try {
        const mark = new Image();
        mark.src = '/assets/vm-logo-optimized.webp';
        await mark.decode();
        ctx.drawImage(mark, 337, 250, 406, 406);
      } catch {}
      ctx.fillStyle = '#fff5db'; ctx.fillRect(72, 745, 930, 365);
      ctx.fillStyle = '#101930'; ctx.font = 'bold ' + (card.dataset.visual.length > 34 ? 57 : 76) + 'px sans-serif';
      const words = card.dataset.visual.split(' ');
      let line = '', y = 854;
      for (const word of words) {
        const next = line ? line + ' ' + word : word;
        if (ctx.measureText(next).width > 842 && line) { ctx.fillText(line, 108, y); y += 93; line = word; }
        else line = next;
      }
      ctx.fillText(line, 108, y, 842);
      ctx.fillStyle = '#ffc957'; ctx.font = 'bold 40px sans-serif';
      ctx.fillText(new URL(url).hostname, 84, 1232, 900);
      ctx.font = 'bold 27px sans-serif';
      ctx.fillText(document.documentElement.dataset.date.split('-').reverse().join('/'), 84, 1286, 900);
      const download = document.createElement('a');
      download.download = 'vm-' + document.documentElement.dataset.date + '-' + Array.from(document.querySelectorAll('article')).indexOf(card) + '.png';
      download.href = canvas.toDataURL('image/png');
      download.click();
      status.textContent = 'Visuel prêt à partager.';
    });
  });
  `;
  return new Response('<!doctype html><html lang="fr" data-date="' + escape(today) + '"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Kit réseaux du jour · VM Studio</title><style>*{box-sizing:border-box}body{margin:0;background:#101930;color:#fff5db;font:16px/1.55 system-ui}main{width:min(100% - 32px,1040px);margin:28px auto}h1,h2{line-height:1.16}h1{font-size:clamp(2rem,5vw,3.5rem)}a,small{color:#ffc957;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:14px}article{background:#192645;border:1px solid #465a83;border-radius:16px;padding:17px;min-width:0}.actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}button{min-height:46px;padding:8px 12px;background:#ffc957;color:#101930;border:0;border-radius:8px;font:700 1rem system-ui;cursor:pointer}.status{margin:.5rem 0 0}small{font-weight:750}a:focus-visible,button:focus-visible{outline:3px solid white;outline-offset:3px}</style><main><small>VÉLOCE MERCATO · VM UNIVERS · VM STUDIO</small><h1>Kit réseaux du jour</h1><p>' + escape(displayDate.format(now)) + ' · Copie le texte, télécharge le visuel, puis publie sur ton compte.</p><div class="grid">' + markup + '</div><p><a href="' + studio + '">Création de sites</a> · <a href="' + formats + '">Publicité et partenariats</a></p></main><script>' + script + '</script></html>', {
    headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' }
  });
}
