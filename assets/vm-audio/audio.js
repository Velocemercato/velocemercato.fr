const tracks = [
  { title: 'Néons sur Belfort', bpm: 104, chords: [[48, 55, 63, 67], [44, 51, 60, 65], [46, 53, 62, 65], [43, 50, 58, 62]], lead: [72, 75, 79, 75, 72, 70, 67, 70] },
  { title: 'Dernier train du soir', bpm: 74, chords: [[50, 57, 64, 65], [46, 53, 60, 65], [48, 55, 62, 64], [45, 52, 55, 62]], lead: [69, 72, 74, 77, 76, 74, 72, 69] },
  { title: 'Énergie d’arène', bpm: 140, chords: [[45, 52, 60, 64], [41, 48, 57, 64], [43, 50, 59, 62], [40, 47, 56, 62]], lead: [76, 81, 79, 76, 74, 72, 71, 68] }
];
const sampleRate = 22050;
const tau = 2 * Math.PI;
const frequency = note => 440 * 2 ** ((note - 69) / 12);

function instrumental(track) {
  const beat = 60 / track.bpm;
  const total = Math.ceil(32 * beat * sampleRate);
  const samples = new Float32Array(total);
  const mellow = track.bpm < 85;
  let seed = 1361;
  const note = (at, length, midi, amplitude, pad = false) => {
    const first = Math.round(at * sampleRate);
    const count = Math.round(length * sampleRate);
    const step = tau * frequency(midi) / sampleRate;
    for (let i = 0; i < count && first + i < total; i++) {
      const t = i / sampleRate;
      const attack = Math.min(1, t / (pad ? .22 : .025));
      const release = Math.min(1, (length - t) / (pad ? .45 : .13));
      const angle = i * step;
      const wave = Math.sin(angle) + (pad ? .15 : .24) * Math.sin(angle * 2);
      samples[first + i] += wave * attack * release * amplitude * (pad ? .8 : Math.exp(-t * 2.8));
    }
  };
  const drum = (at, high) => {
    const first = Math.round(at * sampleRate);
    const count = Math.floor(sampleRate * (high ? .08 : .22));
    for (let i = 0; i < count && first + i < total; i++) {
      const t = i / sampleRate;
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      const part = high ? (seed / 4294967296 - .5) * Math.exp(-t * 54) * .18
        : Math.sin(tau * (47 * t + 4 * (1 - Math.exp(-t * 17)))) * Math.exp(-t * 21) * .28;
      samples[first + i] += part * Math.min(1, t * 500);
    }
  };
  for (let bar = 0; bar < 8; bar++) {
    const chord = track.chords[bar % track.chords.length];
    const at = bar * beat * 4;
    chord.forEach(midi => note(at + .012, beat * 3.98, midi, .052, true));
    for (let i = 0; i < 8; i++) {
      if (!mellow && i % 2 === 0) drum(at + i * beat / 2, false);
      if (!mellow && i % 2 === 1) drum(at + i * beat / 2, true);
      if (i % 2 === 0) note(at + i * beat / 2, beat * .88, chord[0] - 12, .17);
      const pitch = track.lead[(i + bar * 2) % track.lead.length];
      if (!mellow || i % 2 === 0) note(at + i * beat / 2, beat * (mellow ? .89 : .47), pitch, .12);
    }
  }
  const out = new DataView(new ArrayBuffer(44 + total * 2));
  const write = (start, text) => [...text].forEach((char, index) => out.setUint8(start + index, char.charCodeAt(0)));
  write(0, 'RIFF'); out.setUint32(4, 36 + total * 2, true); write(8, 'WAVE'); write(12, 'fmt ');
  out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 1, true);
  out.setUint32(24, sampleRate, true); out.setUint32(28, sampleRate * 2, true);
  out.setUint16(32, 2, true); out.setUint16(34, 16, true); write(36, 'data'); out.setUint32(40, total * 2, true);
  for (let i = 0; i < total; i++) {
    const amp = Math.min(1, i / 440, (total - i) / 1100);
    out.setInt16(44 + i * 2, Math.max(-1, Math.min(1, samples[i] * amp)) * 32767, true);
  }
  return new Blob([out.buffer], { type: 'audio/wav' });
}
const audio = document.querySelector('audio');
const trackName = document.getElementById('track-name');
let current = 0, source, channel = false;
function listen(index) {
  if (!tracks[index]) return;
  current = index;
  audio.pause();
  if (source) URL.revokeObjectURL(source);
  source = URL.createObjectURL(instrumental(tracks[index]));
  audio.src = source;
  audio.hidden = false;
  trackName.textContent = tracks[index].title;
  audio.play().catch(() => { trackName.textContent = tracks[index].title + ' · Appuyez sur Lecture dans le lecteur.'; });
}
document.querySelectorAll('[data-play]').forEach(button => {
  button.onclick = () => { channel = button.hasAttribute('data-loop'); listen(Number(button.dataset.play)); };
});
audio?.addEventListener('ended', () => { if (channel) listen((current + 1) % tracks.length); });

const events = document.getElementById('schedule');
if (events) {
  const filter = document.getElementById('sport-filter');
  const status = document.getElementById('schedule-status');
  const formats = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  const text = (tag, value, className) => {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    return node;
  };
  const secureURL = url => {
    try { const parsed = new URL(url); return parsed.protocol === 'https:' && !parsed.username && !parsed.password; } catch { return false; }
  };
  const link = (label, url, className) => {
    const anchor = text('a', label, className);
    anchor.href = url; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer';
    return anchor;
  };
  fetch('/assets/vm-audio/matchs.json', { cache: 'no-cache' })
    .then(response => { if (!response.ok) throw Error(); return response.json(); })
    .then(items => {
      const matches = items.filter(row => row && row.sport && row.titre && row.radio && [row.ecoute, row.annonce, row.horaire].every(secureURL)
        && Date.parse(row.debut) < Date.parse(row.retrait)).sort((a, b) => Date.parse(a.debut) - Date.parse(b.debut));
      function render() {
        const now = Date.now();
        const scheduled = matches.filter(row => Date.parse(row.retrait) > now);
        const sports = [...new Set(scheduled.map(row => row.sport))].sort();
        const selected = filter.value;
        filter.replaceChildren(text('option', 'Tous les sports'));
        filter.firstChild.value = '';
        sports.forEach(sport => { const option = text('option', sport); option.value = sport; filter.append(option); });
        filter.value = sports.includes(selected) ? selected : '';
        const visible = scheduled.filter(row => !filter.value || row.sport === filter.value);
        events.replaceChildren();
        status.textContent = visible.length ? 'Heures de Paris · commentaires annoncés par les sources indiquées.'
          : 'Aucun commentaire de match confirmé pour le moment. Les radios restent accessibles plus bas.';
        visible.forEach(row => {
          const card = document.createElement('article');
          card.append(text('p', row.sport + ' · ' + row.competition), text('h3', row.titre));
          const airing = Date.parse(row.debut) <= now;
          const time = text('time', formats.format(new Date(row.debut)));
          time.dateTime = row.debut;
          const info = document.createElement('p');
          info.append(airing ? 'Horaire annoncé passé · ' : 'Coup d’envoi · ', time, ' · ' + row.radio);
          card.append(info, link('Ouvrir ' + row.radio + ' ↗', row.ecoute, 'action'));
          const sources = text('div', '', 'references');
          sources.append(link('Annonce radio', row.annonce), link('Horaire officiel', row.horaire));
          card.append(sources);
          events.append(card);
        });
      }
      filter.onchange = render;
      render();
      setInterval(render, 60000);
    })
    .catch(() => { status.textContent = 'L’agenda est momentanément indisponible. Vous pouvez ouvrir les radios ci-dessous.'; });
}
