(() => {
  const {esc, mail, json, val} = window.VMP;
  const $ = id => document.getElementById(id);
  const PROG = {
    debutant: ['Débutant · 3 séances par semaine (corps entier)', [
      ['Lundi', 'Squat au goblet 3×10 · pompes (genoux si besoin) 3×8 · tirage élastique 3×12 · gainage planche 3×20 s'],
      ['Mercredi', 'Fentes 3×8 par jambe · développé haltères 3×10 · tirage 3×10 · pont fessier 3×12'],
      ['Vendredi', 'Soulevé de terre roumain haltères 3×8 · pompes inclinées 3×8 · élévations latérales 3×12 · mollets 3×15']],
      'Progression : ajoute une répétition par semaine, puis augmente la charge quand tu tiens toutes les séries.'],
    inter: ['Intermédiaire · 4 séances (haut / bas)', [
      ['Lundi (haut)', 'Développé couché 4×8 · rowing 4×8 · développé épaules 3×10 · curl 3×12'],
      ['Mardi (bas)', 'Squat 4×6-8 · soulevé de terre roumain 3×8 · fentes 3×10 · mollets 4×12'],
      ['Jeudi (haut)', 'Tractions ou tirage 4×8 · développé incliné 3×10 · élévations 3×12 · triceps 3×12'],
      ['Vendredi (bas)', 'Presse 3×12 · hip thrust 4×10 · leg curl 3×12 · gainage 3×45 s']],
      'Repos d’au moins 48 h entre deux séances du même groupe musculaire.'],
    avance: ['Avancé · 5 séances (push / pull / legs)', [
      ['Lundi (push)', 'Développé couché 5×5 · développé militaire 4×6 · dips 3×8 · élévations latérales 4×15'],
      ['Mardi (pull)', 'Tractions lestées 5×5 · rowing barre 4×6 · face pull 3×15 · curl 3×10'],
      ['Mercredi (legs)', 'Squat 5×5 · presse 3×10 · fentes marchées 3×12 · mollets 4×12'],
      ['Jeudi (push)', 'Développé incliné 4×6 · écarté 3×12 · développé nuque 3×8 · triceps barre 3×10'],
      ['Vendredi (pull + bras)', 'Soulevé de terre 4×5 · tirage poitrine 4×8 · curl marteau 3×12 · gainage 3×60 s']],
      'Suis une charge sur chaque exercice et note-la. Ajoute de la charge seulement quand la technique reste propre.']
  };
  function muscu(niv) {
    const [titre, seances, note] = PROG[niv];
    $('muscu').innerHTML = `<p class="lead">${esc(titre)}</p>` + seances.map(([j, t]) => `<article><b>${esc(j)}</b><p>${esc(t)}</p></article>`).join('') + `<p class="pnote">${esc(note)}</p>`;
  }
  document.querySelectorAll('[data-niv]').forEach(button => button.onclick = () => {
    document.querySelectorAll('[data-niv]').forEach(b => b.setAttribute('aria-selected', String(b === button)));
    muscu(button.dataset.niv);
  });
  muscu('debutant');
  let chemins = [];
  function rendre() {
    const reg = $('fCheReg').value, type = $('fCheType').value;
    const list = chemins.filter(c => (!reg || c.region === reg) && (!type || c.type === type));
    $('chemins').innerHTML = list.length ? list.map(c => `<article class="pcard"><h3>${esc(c.nom)}</h3><p>📍 ${esc(c.region)} · ${esc(c.type)}${c.mesures ? ' · ' + esc(c.mesures) : ''}</p><p>${esc(c.desc)}</p>${c.par ? `<p class="pnote">Proposé par ${esc(c.par)}</p>` : ''}${c.lien && /^https:/.test(c.lien) ? `<p><a href="${esc(c.lien)}" target="_blank" rel="noopener nofollow">Voir la trace</a></p>` : ''}</article>`).join('')
      : '<p class="vide">Pas encore de chemin pour ce filtre. Propose le tien ci-dessous.</p>';
  }
  $('fCheReg').onchange = rendre; $('fCheType').onchange = rendre;
  json('/sport/chemins.json').then(list => { chemins = list.filter(c => c && c.nom && c.region); rendre(); });
  $('formChemin').onsubmit = event => {
    event.preventDefault();
    const f = event.target;
    mail(`Sport – chemin proposé : ${val(f, 'nom')}`, `Nom : ${val(f, 'nom')}\nRégion : ${val(f, 'region')}\nActivité : ${val(f, 'type')}\nMesures : ${val(f, 'mesures')}\nPar : ${val(f, 'par')}\n\nDescription et accès :\n${val(f, 'desc')}\n\n(Joins le fichier GPX ou le lien de ta trace à cet e-mail.)`);
  };
})();
