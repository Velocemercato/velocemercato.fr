const essentials = [
  ['#feed-title', '⚽', 'Actus foot'],
  ['/scores/', '📊', 'Scores'],
  ['/multisport/', '🏆', 'Multisport'],
  ['/actus/', '📰', 'VM Actus'],
  ['/vm-gaming/', '🎮', 'VM Gaming'],
  ['#pastille-tv', '▶', 'Pastilles']
];

const more = [
  ['/foot-amateur/', 'Foot des régions'], ['/belfort/', 'VM Belfort'],
  ['/mangas/', 'Mangas'], ['/series/', 'Séries'], ['#videos', 'Buts et vidéos'],
  ['#agenda', 'Agenda'], ['#quiz', 'Quiz'], ['#flash-title', 'Flash infos'],
  ['/pronos/#pronos-du-jour', 'Analyse sportive 18+'], ['#reseaux', 'Nos réseaux'],
  ['/notifications/', 'Mes alertes'], ['/reportages/loic-tanzi', 'Reportage Loïc Tanzi'],
  ['/services/', 'Services'], ['/soutenir', 'Soutenir VM'], ['https://vmunivers.fr/', 'Tous les projets VM']
];

export const compactHeader = `<section class="vm-essentiel" aria-labelledby="vm-essentiel-title">
  <div class="vm-essentiel-heading">
    <img src="/img/logo-vm-192.png" width="44" height="44" alt="">
    <div><h1 id="vm-essentiel-title">Véloce <span>Mercato</span></h1><p>Le foot, les scores et les univers VM.</p></div>
    <a class="vm-essentiel-univers" href="https://vmunivers.fr/">VM Univers ↗</a>
  </div>
  <nav class="vm-essentiel-grid" aria-label="Rubriques principales">${essentials.map(([url, icon, label]) =>
    `<a href="${url}"><span aria-hidden="true">${icon}</span> ${label}</a>`).join('')}</nav>
  <details class="vm-essentiel-more"><summary>Autres rubriques</summary><nav aria-label="Autres rubriques VM">
    ${more.map(([url, label]) => `<a href="${url}">${label}</a>`).join('')}
    <a id="vm-resume-sport" href="/multisport/" hidden>Mon sport favori</a>
  </nav></details>
  <div id="vm-essentiel-install"></div>
</section>`;

export const compactStyle = `<style id="vm-home-mobile">
.vm-essentiel{box-sizing:border-box;width:min(100% - 24px,1180px);margin:10px auto 14px;padding:14px;background:linear-gradient(125deg,#181829,#101222 70%);color:#fff;border:1px solid #66334f;border-top:3px solid #e03f56;border-radius:13px;font:650 1rem/1.25 system-ui,sans-serif}
.vm-essentiel-heading{display:flex;align-items:center;gap:9px;min-width:0;margin-bottom:10px}
.vm-essentiel-heading img{flex:none;width:44px;height:44px;object-fit:contain}
.vm-essentiel-heading h1{margin:0;font:bold italic clamp(1.35rem,6.2vw,2.2rem)/1 system-ui,sans-serif}
.vm-essentiel-heading h1 span{color:#dcff86}
.vm-essentiel-heading p{margin:3px 0 0;font-size:.78rem;color:#d7d9e5}
.vm-essentiel-univers{margin-left:auto;color:#ffe08a;font-size:.78rem;text-align:right;flex:none}
.vm-essentiel-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
.vm-essentiel-grid a,.vm-essentiel-more a{display:flex;align-items:center;gap:4px;color:#f5f4ff;text-decoration:none}
.vm-essentiel-grid a{min-height:42px;box-sizing:border-box;padding:5px 7px;background:#23263d;border:1px solid #464c6d;border-radius:7px;font-size:clamp(.73rem,2.75vw,1rem)}
.vm-essentiel-grid a:hover,.vm-essentiel-more a:hover{color:#ffe08a}
.vm-essentiel-more{margin-top:8px;font-size:.83rem;color:#ffe08a}
.vm-essentiel-more summary{cursor:pointer;min-height:29px;padding-block:4px}
.vm-essentiel-more nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px 12px;margin:4px 0 0}
.vm-essentiel-more a{min-height:32px}
.vm-essentiel-more [hidden]{display:none}
.home-simple>.vm-flash-toggle{display:none!important}
#vm-essentiel-install #vmInst,#reseaux #vmFab{position:static!important;transform:none!important;margin-top:8px}
#feed-title,#pastille-tv,#reseaux{scroll-margin-top:16px}
.home-main{padding-top:0!important}
@media(max-width:380px){.vm-essentiel{padding:10px}.vm-essentiel-heading img{width:36px;height:36px}.vm-essentiel-univers{display:none}}
@media(min-width:720px){.vm-essentiel-grid{grid-template-columns:repeat(6,minmax(0,1fr))}}
</style>`;

export function compactHome(rewriter) {
  return rewriter
    .on('body > #vm-reseaux-bar, body > .vu-strip, body > .home-flash-top, body > .vmbar, body > header.sticky, #vm-cinema-home, body > aside[aria-label="Nouveau VM MANGAS"], #vm-choisir-sport, body > section.v2, script[src^="/assets/vm-cinema-foot.js"], script[src="/pronos/bandeau.js"]', {
      element(element) { element.remove(); }
    })
    .on('body > .vu-pub, .home-content > .vu-pub-jt, .home-news > .vu-pub-carte, .home-content > section[aria-label="Grand reportage Loïc Tanzi"]', {
      element(element) { element.remove(); }
    })
    .on('.home-professional', {
      element(element) { element.append(' <a href="/pub/#packs">Les offres publicitaires →</a>', { html: true }); }
    })
    .on('#pastille-tv .ptv-head p', {
      element(element) { element.setInnerContent('Les JT Multisport à 8 h, 13 h et 20 h. Débrief sport à 23 h, heure de Paris.'); }
    });
}
