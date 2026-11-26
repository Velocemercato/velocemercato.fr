// "Vérifié" est la date du contrôle par le robot, distincte de l'heure d'affichage.
export const snapshotTime = data => data?.verifie || data?.maj;
export function freshSnapshot(data, now = Date.now()) {
  const age = now - Date.parse(snapshotTime(data));
  return Number.isFinite(age) && age >= -60000 && age <= 40 * 60000;
}

const sources = [
  'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/scores-live/scores.json',
  '/scores.json',
];

async function readSnapshot(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5500);
  try {
    const response = await fetch(url + '?t=' + Math.floor(Date.now() / 60000), {
      cache: 'no-store',
      signal: controller.signal,
    });
    const data = response.ok ? await response.json() : null;
    return Array.isArray(data?.matchs) ? data : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export async function loadScoreSnapshot() {
  const direct = await readSnapshot(sources[0]);
  if (freshSnapshot(direct)) return direct;
  const fallback = await readSnapshot(sources[1]);
  if (freshSnapshot(fallback) || !direct) return fallback;
  if (!fallback) return direct;
  return Date.parse(snapshotTime(fallback)) > (Date.parse(snapshotTime(direct)) || 0)
    ? fallback : direct;
}
