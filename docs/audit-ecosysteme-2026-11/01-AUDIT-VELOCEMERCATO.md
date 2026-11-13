# 01 — Audit détaillé de velocemercato.fr

## A. Positionnement et proposition de valeur

### Promesse actuelle
[FAIT] Le titre de l’accueil est « Véloce Mercato — Aperçu de l’accueil ». La page n’a pas de meta description. Le site se présente comme « la maison-mère de l’univers VM ». Il propose environ 14 accès sur l’accueil (VM Foot, Multisport, Actus, Mangas, Gaming, Studio, Pastille, Prono, Région, Pro, Shop…).

**Diagnostic :** le visiteur ne sait pas en 5 secondes pourquoi il est là. « Maison-mère de l’univers VM » parle de l’organisation, pas du bénéfice pour le lecteur. Un média se choisit pour **un sujet, un angle et un rythme**.

### Promesse idéale (recommandation)
> **« Le foot qui bouge, vite et sourcé. Mercato, Ligue 1 et foot de l’Est, en 2 minutes chrono. »**

Ce qui compose cette promesse :
- **Vite** : des brèves courtes, la Pastille TV et les scores en direct. C’est déjà la force du site.
- **Sourcé** : chaque brève cite sa source avec un lien. C’est déjà le cas : il faut le **montrer** comme un argument.
- **Foot de l’Est et foot amateur** : une niche locale (Franche-Comté, Alsace, Lorraine) que les grands médias nationaux couvrent peu. **[HYPOTHÈSE]** à valider avec les requêtes réelles de la Search Console.

### Cible et personas prioritaires

| Persona | Qui | Besoin | Ce que VM lui offre |
|---|---|---|---|
| **Le scrolleur mercato** (P1) | 16-35 ans, mobile, réseaux sociaux | Savoir en 30 secondes « qui va où », vrai ou rumeur | Brèves sourcées, statut « officiel / rumeur », Pastille TV |
| **Le supporter local** (P1) | 25-60 ans, suit un club de l’Est ou un club amateur | Résultats, convocations, actus du club, où regarder | Pages club, foot amateur, agenda, « où regarder » |
| **Le fan du match du soir** (P2) | Tous âges | Heure, chaîne, compos probables, score en direct | Pages match, bandeau des scores, alertes but |
| **L’annonceur local** (P2) | Commerce, club, marque régionale | Toucher des fans de foot locaux à petit budget | Sponsoring Pastille, partenaire local, brève sponsorisée |

### Différence avec les grands médias

| Média | Force | Où VM ne peut pas lutter | Où VM peut gagner |
|---|---|---|---|
| L’Équipe, RMC Sport | Rédaction, droits, exclusivités | Infos exclusives, matchs en direct, interviews | — |
| Foot Mercato, Foot01, Le10Sport | Volume mercato, référencement ancien | Volume brut d’articles mercato | La **vérification affichée** (rumeur ou officiel, source primaire) et la **brièveté** |
| Made in Foot, BeFoot | Ton, vidéo, communauté | Production vidéo humaine | **Format JT court automatisé** (Pastille) et communauté Discord |
| Presse régionale (L’Est Républicain, DNA…) | Terrain local | Correspondants, accès aux clubs | **Agrégation rapide et gratuite** du foot de l’Est + amateur, avec résultats et pages club |

**La niche réaliste** : *agrégateur éditorialisé, rapide et transparent, du mercato et du foot de l’Est de la France, en format court (texte, Pastille, réseaux)*. Ne pas chercher à concurrencer l’exclusivité nationale.

### Les 3 messages à communiquer partout
1. **« Vite »** : l’essentiel en 2 minutes (brèves, Pastille, scores).
2. **« Vrai »** : chaque info est sourcée, et les rumeurs sont étiquetées comme telles.
3. **« Proche »** : le foot de l’Est et le foot amateur, que les autres ne couvrent pas.

---

## B. Structure, UX et navigation

### Analyse de la page d’accueil actuelle
[FAIT] Ce qui a été relevé dans le code :
- environ 160 Ko de HTML ;
- 7 balises `<h1>` (VM Foot, VM Multisport, VM Actus…) ;
- un bandeau de scores ;
- des volets par rubrique ;
- des accès « cadre » (bureau, fauteuil, pouf, microphone) vers Facebook, VM Prono, Studio, Pastille ;
- des liens vers les Pages Facebook ;
- une vidéo Pastille.

**Problèmes de hiérarchie :**
- 7 H1 : Google et les lecteurs d’écran ne savent pas quel est le sujet de la page.
- Les accès décoratifs (« Pouf en cuir — VM Prono », « Microphone — ouvrir la Page Facebook ») sont des objets de décor qui mènent hors du site, avant même la première actualité.
- **CTA en concurrence** : Discord, Facebook, Pastille, Prono, Studio, Soutenir, Notifications, Shop… Aucun n’est le principal.
- **Bruit** : pronostics et jeux d’argent sur l’accueil d’un média grand public ; projets non sportifs (studio de création, pro local) au même niveau que l’actualité.
- **Rubriques redondantes** :
  - `foot/` et `foot-amateur/` et `sport/` et `multisport/` ;
  - `actus/` et `pronos/` (« VM Actus & Pronos ») ;
  - `shop/`, `boutique/` et `vente/` ;
  - `studio.html`, `web-studio.html` et `studio/` ;
  - `pro/`, `pro-auto/` et `services/`.

### Modules : décision par module

| Module | Décision | Raison |
|---|---|---|
| Brèves foot récentes | **Garder, en tête de page** | C’est le cœur de la promesse |
| Bandeau des scores (avec réglage par sport) | **Garder** | Utile, différenciant, fait revenir les visiteurs |
| La Pastille TV | **Garder, en position 2** | Format signature |
| Volets Multisport, Actus | **Garder plus bas**, 6 éléments maximum chacun | Contenu secondaire |
| VM Gaming, VM Mangas | **Déplacer** dans un bloc « Les univers VM » en bas de page | Hors sujet foot, mais l’audience existe |
| VM Prono, « jeux d’argent » | **Retirer de l’accueil** ; garder `prono.velocemercato.fr` séparé (18+) | Crédibilité, mineurs, annonceurs |
| Accès décoratifs (pouf, fauteuil, micro) | **Supprimer** ou remplacer par des liens texte | Bruit, liens sortants avant le contenu |
| Studio de création, VM Pro local, Shop, Immo, Emploi, CV | **Retirer de l’accueil et du menu** ; un seul lien en pied de page « Les projets VM » vers vmunivers.fr | Ce n’est pas le métier du média |
| Liens Facebook, TikTok, YouTube | **Regrouper** en pied de page | Bruit en haut de page |
| Soutenir, Notifications | **Garder** un seul bouton « 🔔 Alertes but » dans l’en-tête | Fidélisation |

### Nouvelle arborescence recommandée

```
velocemercato.fr/
├── /                        Accueil : promesse + dernières infos + Pastille + scores
├── /mercato/                Pilier mercato (rumeurs / officiels / bilans)
│   ├── /mercato/officiels/          Transferts confirmés
│   └── /mercato/[club]/             Mercato d'un club (pages de soutien)
├── /ligue-1/                Pilier compétition : classement, calendrier, actus
├── /ligue-des-champions/
├── /equipe-de-france/
├── /foot-amateur/           Pilier régional (Est + amateur)
│   └── /foot-amateur/[district]/
├── /clubs/[club]/           Pages club (FC Sochaux, RC Strasbourg, FC Metz…)
├── /joueurs/[joueur]/       Pages joueur (uniquement les joueurs suivis régulièrement)
├── /match/[date]-[equipe-a]-[equipe-b]/  Pages match
├── /ou-regarder/            Programme TV foot + pages « où regarder [match] »
├── /resultats/              Scores en direct (actuel /scores/)
├── /pastille/               La Pastille TV (archives vidéo)
├── /a/                      Articles (URL stable, archive)
├── /multisport/  /gaming/  /mangas/   Univers secondaires (sous-menu « Plus »)
├── /newsletter/  /discord/  (/alertes/)
├── /publicite/   /partenaires/
├── /a-propos/  /redaction/  /sources-et-corrections/  /contact/
└── /mentions-legales/  /politique-de-confidentialite/  /cookies/  /cgu/
```

**Navigation recommandée :**
- **Mobile** (barre du haut) : Logo · Mercato · Ligue 1 · Résultats · ☰. Le menu ☰ contient : Ligue des champions, Équipe de France, Foot amateur, Où regarder, Pastille TV, Plus (Multisport, Gaming, Mangas), Newsletter, Discord.
- **Ordinateur** : Mercato · Ligue 1 · Ligue des champions · Équipe de France · Foot amateur · Résultats · Où regarder · Pastille TV · Plus ▾ — avec à droite les boutons « 🔔 Alertes » et « Newsletter ».
- **Pied de page** : À propos · Rédaction · Sources et corrections · Publicité · Partenaires · Contact · Mentions légales · Confidentialité · Cookies · « Un média du réseau VM Univers ».

### Accueil simplifié (de haut en bas)
1. En-tête : logo + menu + 🔔.
2. **Bandeau promesse**, une ligne : « Le foot qui bouge, vite et sourcé. »
3. **À la une** : 1 grande info + 4 brèves (titre, source, heure).
4. **Bandeau des scores du jour.**
5. **La Pastille du jour** (vidéo + 3 titres).
6. **Mercato** : 6 dernières, avec étiquette Officiel ou Rumeur.
7. **Foot de l’Est et amateur** : 6 dernières.
8. **Où regarder ce soir** : 3 matchs.
9. **Newsletter + Discord** : un seul bloc, une seule phrase.
10. Multisport / Gaming / Mangas : 3 cartes compactes.
11. Pied de page.

Une seule balise H1 : « Véloce Mercato — actualité foot, mercato et foot de l’Est ». Les titres de blocs passent en H2.

### Parcours utilisateurs idéaux

| Visiteur | Entrée | Parcours | Conversion visée |
|---|---|---|---|
| **Visiteur Google** | Article ou page « où regarder » | Article → encadré « À lire aussi » (même club) → page club | 2e page vue, puis inscription aux alertes |
| **Fan de foot** | Accueil ou réseaux | À la une → Pastille → Résultats | Retour quotidien, alertes but |
| **Amateur de mercato** | `/mercato/` ou article | Article → page mercato du club → « Officiels » | Newsletter « Mercato en 5 min » |
| **Membre Discord** | Lien posté sur Discord | Article → bloc « Discute-en sur Discord » | Message sur Discord, retour sur le site |
| **Annonceur potentiel** | Pied de page « Publicité » ou démarchage | `/publicite/` (audience, formats, prix) → formulaire | Demande de devis annonceur |
| **Partenaire** (club, asso) | `/partenaires/` | Offres club / local → exemples → formulaire | Rendez-vous |

### Hiérarchie des contenus
- **Priorité 1** : mercato, Ligue 1, foot de l’Est et amateur, résultats, où regarder, Pastille.
- **Priorité 2** : Ligue des champions, Équipe de France, newsletter, Discord.
- **Priorité 3** : Multisport, Gaming, Mangas, Véloce Arena, Pépite FC.
- **Hors média** (à déplacer vers vmunivers.fr ou à mettre en pause) : studio de création, pro local, immobilier, emploi, CV, recettes, comparateur, boutique, allolivre, investisseurs, produits locaux, météo.

---

## C. SEO technique — checklist

| # | Point | Constat / problème éventuel | Impact | Action exacte | Priorité | Effort |
|---|---|---|---|---|---|---|
| 1 | Indexation | [FAIT] 27 pages `/a/` en `noindex,follow`, avec canonical vers `/foot/`. [HYPOTHÈSE] Le nombre de pages indexées est inconnu. | On ne sait pas ce que Google voit | Vérifier le site dans la Search Console (domaine) et lire le rapport « Pages » | Critique | Faible |
| 2 | Sitemap XML | [FAIT] 32 adresses, 4 articles, `/foot/` absent, pages hors sujet présentes | Les articles sont découverts lentement ou jamais | Générer `sitemap-index.xml` qui pointe vers `sitemap-pages.xml` (rubriques), `sitemap-articles.xml` (tous les `/a/` indexables, avec `lastmod`) et `sitemap-news.xml` (articles de moins de 48 h, format Google News). Le régénérer à chaque build. | Critique | Faible |
| 3 | Robots.txt | [FAIT] Correct : bloque `/demos/`, `/stats/`, brouillons | — | Ajouter la ligne `Sitemap:` du nouvel index ; bloquer les pages techniques (`/push/`, `/notifications/` si non utiles) | Basse | Faible |
| 4 | Canonical | [FAIT] Présent sur les articles et l’accueil | — | Vérifier que chaque page de rubrique a un canonical sur elle-même, et non sur l’accueil | Moyenne | Faible |
| 5 | Redirections | [FAIT] `/belfort/` redirige vers `/region/` par meta refresh | Une meta refresh est moins forte qu’une 301 | Utiliser un fichier `_redirects` Cloudflare Pages avec de vraies 301 (`/belfort/ /region/?r=bourgogne-franche-comte 301`) | Moyenne | Faible |
| 6 | HTTPS | [HYPOTHÈSE] OK via Cloudflare | — | Activer HSTS dans Cloudflare après vérification | Basse | Faible |
| 7 | URLs propres | [FAIT] `/a/rss-v2-0ed726893ca9ccf996d30a.html` : URL illisible pour les brèves automatiques | Moins de clics, aucun mot-clé | Nouveau format : `/a/AAAA-MM-JJ-titre-court.html` (comme `2026-10-17-balde-barca-janvier`) ; garder les anciennes URL (ne rien casser) | Haute | Moyen |
| 8 | Structure Hn | [FAIT] 7 H1 sur l’accueil, 2 sur `/foot/` | Sujet de page flou | 1 seul H1 par page ; les titres de blocs en H2 | Haute | Faible |
| 9 | Maillage interne | [HYPOTHÈSE] Les articles n’ont pas de liens vers des pages club ou compétition (ces pages n’existent pas encore) | Le « jus » SEO reste bloqué dans les brèves | Bloc automatique « À lire aussi » (3 articles du même club ou de la même compétition) + lien vers la page pilier | Haute | Moyen |
| 10 | Données structurées | [FAIT] `NewsArticle` présent sur les articles ; aucune sur l’accueil | Pas d’éligibilité aux résultats enrichis | Ajouter `WebSite` + `SearchAction` et `NewsMediaOrganization` sur l’accueil, `BreadcrumbList` partout, `SportsEvent` sur les pages match, `SportsTeam` sur les pages club, `Person` sur les pages auteur | Haute | Moyen |
| 11 | Auteur | [FAIT] `author: Organization` | E-E-A-T faible | `author: Person`, avec un lien vers `/redaction/[auteur]/` | Haute | Faible |
| 12 | Open Graph / Twitter Cards | [FAIT] `og:image` générique et identique pour tous les articles | Faible taux de clic sur les réseaux | Image de partage par article (la carte Instagram générée par les robots existe déjà) + `twitter:card=summary_large_image` | Moyenne | Moyen |
| 13 | Images, alt | [HYPOTHÈSE] Alt à contrôler | Accessibilité, Google Images | Alt descriptif obligatoire (règle de build : échec si alt vide sur une image de contenu) | Moyenne | Faible |
| 14 | Compression / formats | [FAIT] Images en WebP pour une partie | — | Tout passer en WebP/AVIF, avec `width`/`height` sur chaque image | Moyenne | Moyen |
| 15 | Lazy loading | [HYPOTHÈSE] | LCP | `loading="lazy"` sous la ligne de flottaison ; **jamais** sur l’image principale (au contraire `fetchpriority="high"`) | Moyenne | Faible |
| 16 | LCP | [HYPOTHÈSE] 160 Ko de HTML et beaucoup de blocs dynamiques | Lenteur sur mobile | Mesurer avec PageSpeed Insights (accueil, `/foot/`, un article) ; viser un LCP inférieur à 2,5 s ; servir la « À la une » en HTML statique (et non en JS) | Haute | Moyen |
| 17 | INP | [HYPOTHÈSE] Bandeau, alertes et volets en JS | Réactivité | Différer les scripts non essentiels (`defer`) ; un seul `setInterval` pour les scores | Moyenne | Moyen |
| 18 | CLS | [HYPOTHÈSE] Bandeau des scores et volets chargés après coup | Les éléments sautent pendant le chargement | Réserver la hauteur (`min-height`) des blocs dynamiques et des embeds vidéo | Haute | Faible |
| 19 | Mobile-first | [FAIT] 115 pages testées sans débordement (audit précédent) | — | Garder ce test dans la CI | Basse | Faible |
| 20 | Scripts tiers | [FAIT] Cloudflare Insights (sans cookie), OneSignal, YouTube (123 références), Google Fonts | Vie privée, vitesse | Polices hébergées sur le site ; YouTube en `youtube-nocookie` avec chargement au clic (façade) ; OneSignal seulement sur la page des alertes | Haute | Moyen |
| 21 | Cache / CDN | [FAIT] Cloudflare Pages | — | En-têtes `Cache-Control` longs sur `/assets/` et `/img/` (fichier `_headers`), avec noms de fichiers versionnés | Moyenne | Faible |
| 22 | Minification | [HYPOTHÈSE] CSS et JS en ligne non minifiés | Poids | Minifier au build (`prepare_public_site.py`) | Basse | Faible |
| 23 | Polices | [FAIT] Google Fonts depuis `fonts.googleapis.com` | RGPD (transfert d’IP), rendu | Héberger Barlow / Anton en `woff2` sur le site, avec `font-display: swap` et un préchargement de la police du titre | Haute | Faible |
| 24 | Vidéos | [FAIT] Pastille en MP4 et YouTube | LCP, cookies | Image de prévisualisation (poster) + lecture au clic ; `VideoObject` en JSON-LD sur `/pastille/` | Moyenne | Moyen |
| 25 | 404 | [FAIT] 0 lien cassé sur 2 211 liens (audit précédent) | — | Page 404 utile (recherche + dernières infos) ; contrôle hebdomadaire des liens | Basse | Faible |
| 26 | Pages dupliquées | [FAIT] Rubriques redondantes (shop / boutique / vente, studio ×3, pro ×3) | Cannibalisation | Une seule page par sujet ; 301 pour les autres | Haute | Moyen |
| 27 | Contenu fin | [FAIT] Pages « Brève archivée » de 556 octets en noindex | Bon choix (noindex) | Garder le noindex ; éviter d’en générer d’autres | Basse | Faible |
| 28 | Pages sans valeur SEO | [FAIT] cv, emploi, immo, recettes, comparateur, investisseurs dans le sitemap | Dilution du sujet | Les retirer du sitemap ; `noindex` ou déplacement vers vmunivers.fr | Haute | Faible |
| 29 | Title et meta description | [FAIT] Accueil sans description ; titre « Aperçu de l’accueil » | Taux de clic | Titre : « Véloce Mercato — Actu foot, mercato et foot de l’Est en direct » ; description de 150 caractères avec la promesse | Critique | Faible |
| 30 | Fil d’Ariane | [HYPOTHÈSE] Absent | Navigation, résultats enrichis | Accueil › Mercato › Article, en HTML et en `BreadcrumbList` | Moyenne | Faible |
| 31 | Pagination | [HYPOTHÈSE] Les listes de rubrique se chargent en JS | Les vieux articles sont inaccessibles aux robots | Pages de liste statiques `/mercato/page/2/` en HTML, avec liens Suivant / Précédent | Moyenne | Moyen |
| 32 | Contenu généré dynamiquement | [FAIT] Blocs remplis par JS depuis du JSON | Google exécute le JS, mais en différé | Pré-rendre en HTML au build les 20 dernières infos de chaque rubrique | Haute | Moyen |
| 33 | Pages « Chargement… » | [HYPOTHÈSE] Des blocs affichent « Chargement » avant le JS | Contenu vide pour les robots et pendant les pannes | Contenu de secours en HTML, remplacé ensuite par le JS | Haute | Moyen |
| 34 | Accessibilité | [FAIT] Bon socle (aria, contrastes) | — | Liens d’évitement, `lang`, focus visible, sous-titres de la Pastille (déjà en `.vtt`) | Moyenne | Faible |
| 35 | Volume de commits / déploiements | [FAIT] Environ 190 commits automatiques par jour | Fragilité, quotas | Regrouper les mises à jour de données dans une branche `donnees`, ou les stocker dans Cloudflare KV / R2 ; ne déployer que si le contenu a changé | Moyenne | Élevé |

---

## D. SEO éditorial (résumé, détail dans le fichier 05)

**Intentions de recherche à viser :**
- **Actualité chaude** (« transfert X », « blessure Y ») : brèves rapides + Google News.
- **Récurrent** (« PSG OM chaîne », « classement Ligue 1 », « calendrier ») : pages piliers mises à jour, très forte valeur.
- **Local** (« FC Sochaux actu », « résultats district Haut-Rhin ») : niche avec peu de concurrence.
- **Evergreen** (« règle du hors-jeu », « comment fonctionne le mercato », « fair-play financier ») : trafic stable.

**Clusters :**
1. Mercato
2. Ligue 1
3. Ligue des champions
4. Équipe de France
5. Foot de l’Est
6. Foot amateur
7. Où regarder
8. Comprendre le foot (evergreen)

**E-E-A-T, les leviers concrets :**
1. Page `/redaction/` avec une vraie personne ou un pseudonyme constant, son rôle et sa méthode.
2. Page `/sources-et-corrections/`.
3. Étiquette « Rumeur / En discussion / Officiel » sur chaque info mercato.
4. Lien vers la source **primaire** (communiqué officiel du club) dès qu’elle existe.
5. Mention « Rédigé avec l’aide de l’IA, vérifié par la rédaction » sur les brèves concernées.
6. Date de mise à jour visible.

---

## E. Contenu (formats, fréquence, sources)

[FAIT] Brèves automatiques sourcées (robots), Pastille TV générée, Instagram et Facebook automatiques.

**Recommandations :**
- **Réduire le volume, augmenter la valeur** : mieux vaut 8 à 15 brèves par jour, regroupées et enrichies (contexte, étiquette, lien vers la page club), que 50 brèves qui ne font que reformuler.
- **Chaque brève doit apporter quelque chose de plus que la source** : contexte (âge, contrat, stats de la saison à vérifier), conséquence (« ce que ça change »), lien interne. Sinon, Google peut juger le contenu peu utile (« contenu à grande échelle »).
- **1 contenu original par semaine** : dossier, bilan mercato d’un club de l’Est, top 5 des jeunes du coin.
- **Fréquences** : voir la grille hebdomadaire du fichier 09.

---

## F. Conversion et monétisation (résumé, détail dans le fichier 07)

[FAIT] Les offres actuelles :
- sponsoring de la Pastille à 49 €/mois ;
- articles partenaires ;
- page `/pub/` « espaces & tarifs » ;
- « VM Pro Local dès 9,90 €/mois » (sur vmunivers) ;
- page Soutenir et page Investisseurs.

**Problèmes :**
- Pas de chiffres d’audience publiés : un annonceur ne peut pas évaluer l’offre.
- Les offres sont dispersées entre `/pub/`, `/pro/`, `/soutenir.html` et `/investisseurs.html`.
- Pas d’étiquetage normalisé des contenus sponsorisés.

**Cible :** 5 offres claires sur `/publicite/`, une page `/partenaires/`, un formulaire annonceur, une charte de transparence. Tous les prix sont **des fourchettes de départ, à ajuster avec l’audience mesurée**.

---

## G. Confiance, légal et conformité (résumé, textes dans le fichier 08)

| Point | Constat | Action | Priorité |
|---|---|---|---|
| Mentions légales | [FAIT] Pas de directeur de la publication, pas d’adresse ni de téléphone ; hébergeur indiqué « GitHub Pages » au lieu de Cloudflare ; ancien nom « Véloce Web Studio » | Remplacer par le texte du fichier 08 | Critique |
| Confidentialité | [FAIT] Section intégrée aux mentions légales, devenue fausse (VM Studio stocke des données, Stripe, OneSignal) | Page dédiée `/politique-de-confidentialite/` | Critique |
| Cookies | [FAIT] Cloudflare Insights sans cookie ; YouTube ; OneSignal (abonnement explicite) | Page `/cookies/` ; YouTube en nocookie + au clic. Avec ces réglages, un bandeau n’est pas nécessaire tant qu’aucun traceur soumis à consentement n’est chargé. **À valider** si une régie publicitaire est ajoutée. | Haute |
| IA | [FAIT] Mentionnée dans les mentions légales seulement | Page `/politique-ia/` + mention sur chaque brève et chaque Pastille (« vidéo générée par IA ») | Haute |
| Pronostics | [FAIT] Mention 18+ et 09 74 75 13 13 présentes | Retirer de l’accueil ; ne jamais lier un opérateur de paris sans contrat ni agrément ANJ ; pas de pronostics sur les réseaux | Haute |
| Publicité | [HYPOTHÈSE] Pas d’étiquette normalisée | Étiquettes « Publicité », « Contenu sponsorisé », « Partenariat » (fichier 07) | Haute |
| Droits d’auteur | [FAIT] Liens vers les sources ; images de partage génériques | Pas d’image de presse ou de photo de joueur sans licence ; utiliser des visuels créés par VM, des banques libres ou des photos officielles avec autorisation | Haute |
| Corrections | [FAIT] Adresse e-mail pour les signalements | Page `/sources-et-corrections/` avec un délai de traitement et un historique des corrections | Moyenne |
