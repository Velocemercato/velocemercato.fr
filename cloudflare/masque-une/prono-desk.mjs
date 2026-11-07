const minutes = 60_000;
const freshness = 30 * minutes;
const analysisLink = 'https://velocemercato.fr/pronos/#pronos-du-jour';
const when = new Intl.DateTimeFormat('fr-FR', {
  dateStyle: 'medium', timeStyle: 'short', timeZone: 'Europe/Paris'
});
const decimal = new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const percent = new Intl.NumberFormat('fr-FR', { style: 'percent', maximumFractionDigits: 1 });
const labels = ['id', 'eventId', 'sport', 'event', 'market', 'pick', 'provider', 'model'];
const risk = '18+ · Le jeu comporte des risques · Cote variable · Aucun gain garanti.';

function secureUrl(value) {
  const url = typeof value === 'string' ? URL.parse(value) : null;
  return url?.protocol === 'https:' && !url.username && !url.password ? url : null;
}

function validText(value) {
  return typeof value === 'string' && value.trim().length > 0 && value.length <= 160;
}

function windowOf(row, now) {
  const observed = Date.parse(row.checkedAt);
  const start = Date.parse(row.startsAt);
  if (!(observed <= now && now < start && now < observed + freshness)) return null;
  return { expires: Math.min(start, observed + freshness), observed, start };
}

function candidate(row, now) {
  if (row?.visibility !== 'public' || row.status !== 'verified' ||
      !labels.every(key => validText(row[key])) || !secureUrl(row.source) ||
      !secureUrl(row.officialSource) || !Number.isFinite(row.odds) || row.odds <= 1.30 ||
      !Number.isFinite(row.probability) || row.probability >= 1 || row.probability * row.odds <= 1) return null;
  const window = windowOf(row, now);
  return window ? { ...row, ...window } : null;
}

function combined(row, picks, now) {
  if (row?.visibility !== 'public' || row.status !== 'verified' ||
      !['id', 'provider', 'model'].every(key => validText(row[key])) || !secureUrl(row.source) ||
      !Array.isArray(row.legs) || row.legs.length < 2 || row.legs.length > 3 ||
      !Number.isFinite(row.odds) || row.odds < 2 ||
      !Number.isFinite(row.probability) || row.probability >= 1 || row.probability * row.odds <= 1) return null;
  const legs = row.legs.map(id => picks.get(id));
  if (legs.some(leg => !leg || leg.provider !== row.provider) ||
      new Set(legs.map(leg => leg.eventId)).size !== legs.length ||
      row.probability > Math.min(...legs.map(leg => leg.probability))) return null;
  const firstStart = Math.min(...legs.map(leg => leg.start));
  const window = windowOf({ ...row, startsAt: new Date(firstStart).toISOString() }, now);
  return window ? { ...row, ...window, expires: Math.min(window.expires, ...legs.map(leg => leg.expires)), legs } : null;
}

export function selectPronos(data, now) {
  const rank = (a, b) => b.probability - a.probability || a.start - b.start;
  const picks = (Array.isArray(data?.singles) ? data.singles : []).slice(0, 500)
    .map(row => candidate(row, now)).filter(Boolean);
  const byId = new Map(picks.map(pick => [pick.id, pick]));
  const combos = (Array.isArray(data?.combos) ? data.combos : []).slice(0, 500)
    .map(row => combined(row, byId, now)).filter(Boolean).sort(rank);
  return { single: picks.sort(rank)[0] ?? null, combo: combos[0] ?? null };
}

export async function readPronoDesk(env, now) {
  const url = secureUrl(env?.VM_PRONOS_FEED_URL);
  if (!url) return { single: null, combo: null, connected: false };
  try {
    const headers = { Accept: 'application/json' };
    if (env.VM_PRONOS_FEED_TOKEN) headers.Authorization = 'Bearer ' + env.VM_PRONOS_FEED_TOKEN;
    const r = await fetch(url, { headers, redirect: 'error', signal: AbortSignal.timeout(3500) });
    if (!r.ok) return { single: null, combo: null, connected: true };
    return { ...selectPronos(await r.json(), now), connected: true };
  } catch {
    return { single: null, combo: null, connected: true };
  }
}

export function pronoKitContent(desk, analysis, now) {
  const cards = [];
  if (desk.single) {
    const row = desk.single;
    cards.push({
      brand: 'VM Multisport · 18+', headline: 'Sélection publique', link: analysisLink,
      visual: 'Cote ' + decimal.format(row.odds) + ' · ' + row.pick,
      expires: row.expires,
      text: row.sport + ' · ' + row.event + ' · ' + when.format(row.start) + ' (Paris). ' +
        'Marché : ' + row.market + ' · Choix : ' + row.pick + '. Cote ' + decimal.format(row.odds) +
        ' relevée chez ' + row.provider + ' le ' + when.format(row.observed) + '. Probabilité prudente estimée : ' +
        percent.format(row.probability) + '. ' + risk,
      source: row.source, officialSource: row.officialSource
    });
  }
  if (desk.combo) {
    const row = desk.combo;
    cards.push({
      brand: 'VM Multisport · 18+', headline: 'Combiné public', link: analysisLink,
      visual: 'Combiné · cote ' + decimal.format(row.odds),
      expires: row.expires,
      text: row.legs.map(leg => leg.event + ' : ' + leg.market + ' · ' + leg.pick).join(' / ') +
        '. Cote combinée ' + decimal.format(row.odds) + ' relevée chez ' + row.provider + ' le ' +
        when.format(row.observed) + '. Probabilité prudente estimée : ' + percent.format(row.probability) + '. ' + risk,
      source: row.source
    });
  }
  if (!desk.single && analysis && now < analysis.kickoff) {
    cards.push({
      brand: 'VM Multisport', headline: 'Avant-match sourcé', visual: analysis.match, link: analysisLink,
      expires: analysis.kickoff,
      text: analysis.match + ' · ' + when.format(analysis.kickoff) + ' (Paris). ' + analysis.analysis +
        ' Sources : ' + analysis.sources.map(source => source.name).join(', ') + '.'
    });
  }
  const state = !desk.connected
    ? 'Flux de cotes à connecter. L’avant-match sourcé reste disponible quand il y en a un.'
    : 'Les cotes expirent après 30 minutes ou au coup d’envoi. Les fiches apparaissent après vérification.';
  const status = state + (!desk.single ? ' Aucune sélection chiffrée active.' : '') +
    (!desk.combo ? ' Aucun combiné vérifié à cote totale d’au moins 2,00.' : '');
  const next = Math.min(now + freshness, ...cards.map(card => card.expires));
  return { cards, status, refreshIn: Math.max(1, Math.ceil((next - now) / 1000)) };
}
