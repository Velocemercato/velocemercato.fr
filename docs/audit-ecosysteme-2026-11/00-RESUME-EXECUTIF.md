# Dossier d’audit et d’exécution — Écosystème VM
**Véloce Mercato (média) · VM Univers (studio de création)** — 13 novembre 2026

## Comment lire ce dossier

| Fichier | Contenu |
|---|---|
| `00-RESUME-EXECUTIF.md` | Résumé, 10 problèmes critiques, 10 opportunités, questions à trancher |
| `01-AUDIT-VELOCEMERCATO.md` | Audit détaillé : positionnement, UX, SEO technique, contenu, monétisation, légal |
| `02-AUDIT-VMUNIVERS.md` | Audit détaillé : positionnement commercial, architecture, offres, conversion |
| `03-ECOSYSTEME-VM.md` | Architecture de marque, liens entre les sites, stratégie à 12 mois, erreurs à éviter |
| `04-PLAN-30-60-90.md` | Plan d’action priorisé : tableaux action / priorité / effort / KPI |
| `05-VM-SEO-30-PAGES-PILIERS.md` | Arborescence SEO, clusters, 30 pages piliers détaillées |
| `06-VM-MODELES-CONTENUS.md` | Les 14 modèles d’articles et de pages, avec exemples |
| `07-VM-MONETISATION-PAGES.md` | 5 offres, pages /publicite et /partenaires, formulaire annonceur, chartes |
| `08-VM-LEGAL-CONFORMITE.md` | Mentions légales, confidentialité, cookies, CGU, rédaction, IA, pronostics |
| `09-VM-CHECKLISTS-SOCIAL-KPI.md` | Checklists technique et éditoriale, Discord, newsletter, vidéos courtes, KPI hebdo |
| `10-VMUNIVERS-OFFRES-PAGES.md` | Repositionnement, arborescence, offres, 11 pages prêtes à publier |
| `11-VMUNIVERS-ACQUISITION.md` | Google Business Profile, prospection, scripts, devis, qualification, KPI mensuel |

### Légende utilisée partout

- **[FAIT]** : constaté dans le code des sites, le 13/11/2026.
- **[HYPOTHÈSE]** : à vérifier avant d’agir. Cela concerne les données d’audience, la concurrence et les positions Google.
- **[À COMPLÉTER]** : information que seul le propriétaire possède (nom, adresse, téléphone…).
- **Priorité** : Critique > Haute > Moyenne > Basse.
- **Effort** : Faible (moins d’une demi-journée), Moyen (1 à 3 jours), Élevé (plus de 3 jours).

> **Limite de l’audit.** Il est fait à partir du code source des deux sites, sans accès à Google Search Console, aux statistiques Cloudflare ni aux revenus. Aucun chiffre de trafic, de position ou de revenu n’est donné : chacun est à mesurer, et le plan dit comment.

---

## 1. Résumé exécutif

**Le constat en une phrase :** l’écosystème VM a une vraie capacité de production technique (robots de publication, scores en direct, studio de création avec paiement, plus de 1 300 pages), mais il se disperse. Le média n’a pas de promesse claire. Le studio n’a pas de vitrine commerciale autonome. Les bases de confiance (mentions légales, confidentialité, auteurs) ne sont pas au niveau d’un média qui veut vendre de la publicité.

**Les trois décisions qui changent tout :**

1. **Recentrer Véloce Mercato sur le football**, avec une niche défendable : *le foot vu de l’Est de la France et du foot amateur, et le mercato expliqué vite et sourcé*. Multisport, gaming et mangas restent, mais comme rubriques secondaires. Il faut sortir du menu principal tout ce qui n’est ni du sport ni du média : immobilier, emploi, CV, recettes, comparateur, boutique, livres, investisseurs.
2. **Faire de vmunivers.fr un vrai site de studio**, et non un portail de 28 applications. La page d’accueil doit vendre une seule chose : *« Votre site, votre carte et votre visibilité locale, à prix fixe, vus en direct avant de payer »*. L’annuaire des projets VM descend en bas de page ou part sur une page dédiée.
3. **Remettre la conformité à niveau avant de vendre de la publicité.** Il faut nommer un directeur de la publication, mettre à jour l’hébergeur et la politique de confidentialité (le studio stocke maintenant des données clients et Stripe encaisse), signer les articles, et étiqueter clairement l’IA et le sponsoring. C’est peu d’effort, et c’est indispensable pour tout annonceur sérieux comme pour Google.

**Ce qu’il faut garder :**
- les robots de publication sourcés ;
- les scores en direct ;
- la Pastille TV ;
- le studio VM Studio (aperçu en direct, prix affiché, paiement 50/50) ;
- les 11 démos métiers ;
- l’identité visuelle noir, rouge et or ;
- la mention 18+ et Joueurs Info Service sur les pronostics.

---

## 2. Les 10 problèmes les plus critiques

| # | Problème | Site | Preuve | Priorité | Effort |
|---|---|---|---|---|---|
| 1 | **Le sitemap ne liste pas le contenu.** Il contient 32 adresses, dont 4 articles seulement, pour environ 1 194 fichiers dans `/a/`. `/foot/`, la rubrique principale, est absente, alors que des pages hors sujet y figurent (`/cv/`, `/emploi/`, `/investisseurs.html`). | VM | [FAIT] `sitemap.xml` | Critique | Faible |
| 2 | **Les mentions légales sont incomplètes et inexactes.** Pas de directeur de la publication, pas d’adresse ni de téléphone de l’éditeur. Elles indiquent « GitHub Pages » comme hébergeur, alors que le site est publié sur Cloudflare Pages. Elles affirment qu’aucune donnée personnelle n’est enregistrée, alors que VM Studio stocke maintenant des commandes, des contacts et des paiements Stripe. | VM + VMU | [FAIT] `mentions-legales.html`, workflow de déploiement, `apps/vm-atelier` | Critique | Faible |
| 3 | **Il n’y a pas de politique de confidentialité dédiée sur vmunivers.fr**, alors que le site collecte des demandes de devis et charge Metricool (avec consentement, ce qui est bien). | VMU | [FAIT] pas de page confidentialité | Critique | Faible |
| 4 | **La page d’accueil de Véloce Mercato n’a pas de promesse.** Titre « Véloce Mercato — Aperçu de l’accueil », pas de meta description, 7 balises H1, environ 160 Ko de HTML, des dizaines d’accès concurrents (VM Prono, Studio, Pastille, Mangas, Gaming…). | VM | [FAIT] `index.html` | Haute | Moyen |
| 5 | **Les articles sont signés « Véloce Mercato » (organisation), sans auteur ni page rédaction.** Ils partagent tous la même image de partage. C’est un signal E-E-A-T faible pour de l’actualité, surtout avec une rédaction assistée par IA. | VM | [FAIT] JSON-LD `author: Organization`, `og:image` générique | Haute | Moyen |
| 6 | **La marque est dispersée.** Plus de 50 dossiers de premier niveau (immo, emploi, cv, recettes, météo, allolivre, comparateur, boutique, shop, vente, produits-locaux, investisseurs…) diluent le sujet du site aux yeux de Google comme des visiteurs. | VM | [FAIT] arborescence | Haute | Moyen |
| 7 | **vmunivers.fr est un portail, pas un site de vente.** L’accueil liste environ 28 projets et applications. L’offre B2B est reléguée sur `/professionnels/`. Il n’y a pas de page Tarifs, Réalisations, FAQ ni À propos dédiée. | VMU | [FAIT] `index.html`, sitemap à 6 adresses | Haute | Moyen |
| 8 | **Les prix ne sont pas cohérents d’une page à l’autre.** Les packs web-studio vont de 290 à 1 490 €. L’atelier en ligne propose un site à 290, 410 ou 540 €. vmunivers annonce « Carte QR 49 € » et « Dès 9,90 €/mois ». Un même prospect peut voir trois grilles. | VM + VMU | [FAIT] `web-studio.html`, `apps/vm-atelier/src/prix.js`, `professionnels/` | Haute | Faible |
| 9 | **Pronostics et paris sont visibles depuis le média principal** (« VM Prono », « Les jeux d’argent » sur l’accueil, pouf VM Prono). Ce n’est pas compatible avec une cible jeune ni avec des annonceurs familiaux ou locaux. Et cela crée une confusion de marque. | VM | [FAIT] accueil | Haute | Faible |
| 10 | **Le volume technique est fragile.** 64 workflows et environ 190 commits automatiques en 24 h. Le risque : pannes silencieuses, quotas GitHub, historique illisible, déploiements trop fréquents. | VM | [FAIT] `.github/workflows`, `git log` | Moyenne | Moyen |

Autres points relevés, détaillés dans les audits :
- Google Fonts chargées depuis les serveurs de Google, ce qui transfère l’adresse IP des visiteurs hors UE. Il vaut mieux les héberger sur le site.
- Vidéos YouTube intégrées sans mode « nocookie » partout.
- 27 pages `/a/` en `noindex` qui redirigent vers `/foot/`.
- Pas de données structurées sur l’accueil.
- Ancien nom « Véloce Web Studio » encore présent dans les mentions légales.

---

## 3. Les 10 opportunités les plus rentables

| # | Opportunité | Pourquoi c’est rentable | Effort | KPI |
|---|---|---|---|---|
| 1 | **Sitemap complet + sitemap Google News** (articles de moins de 48 h) | Les 1 100 pages existantes deviennent découvrables. C’est le gain SEO le moins cher possible. | Faible | Pages indexées (Search Console) |
| 2 | **Pages « Où regarder [match] »** générées depuis les données de scores déjà présentes | Requêtes très recherchées et répétées chaque semaine. Les données sont déjà dans `scores/`. | Moyen | Clics organiques sur `/ou-regarder/` |
| 3 | **Pages club pour l’Est de la France** (FC Sochaux, ASM Belfort, RC Strasbourg, FC Metz, AS Nancy, Dijon FCO, Besançon) + foot amateur régional | Une niche où les grands médias couvrent peu. Le contenu local est difficile à copier. | Moyen | Impressions sur les requêtes « [club] actu » |
| 4 | **Pack « Partenaire local »** : bannière + brève sponsorisée + Pastille, vendu aux commerces qui achètent aussi un site VM Univers | Un même client achète deux fois, et l’écosystème justifie sa raison d’être. | Faible | Partenaires actifs, revenu mensuel récurrent |
| 5 | **Newsletter hebdomadaire « Le Mercato en 5 minutes »** | La seule audience qui appartient vraiment à VM. Elle se vend aussi aux sponsors. | Moyen | Abonnés, taux d’ouverture |
| 6 | **Google Business Profile VM Univers** + 10 avis | Le canal n°1 des clients locaux qui cherchent « création site internet + ville ». Gratuit. | Faible | Appels, clics site, demandes |
| 7 | **Études de cas** sur les vrais projets VM (Véloce Mercato, VM Detailing, VM Menu QR) et sur les démos | Transforme le média en preuve de savoir-faire sans le mélanger à l’offre. | Faible | Taux de conversion de `/realisations` |
| 8 | **Le studio en ligne (aperçu en direct + prix + paiement 50/50) comme argument central** | Un vrai différenciateur face aux agences génériques : « vous voyez avant de payer ». | Faible (déjà construit) | Demandes envoyées depuis le studio |
| 9 | **Kit média `/publicite` avec audience vérifiée** (statistiques Cloudflare + réseaux) | Sans chiffres vérifiables, aucun annonceur n’achète. Avec eux, la Pastille à 49 € devient facile à vendre. | Faible | Demandes annonceurs |
| 10 | **Formats courts récurrents** (Shorts, Reels, TikTok) tirés de la Pastille et des brèves | Les robots produisent déjà les vidéos. Il faut une grille fixe et un appel vers le site ou la newsletter. | Moyen | Abonnés, clics vers le site |

---

## 4. Questions à trancher pour affiner le dossier

**Identité et légal**
1. Qui est **directeur de la publication**, et quelle adresse et quel téléphone faire figurer dans les mentions légales ? Pour un entrepreneur individuel, l’adresse peut être une domiciliation.
2. Dans quelle **ville ou zone** VM Univers veut-il trouver ses clients en priorité ? Belfort, Montbéliard, Nord Franche-Comté, ou toute la France à distance ?
3. Préférez-vous signer les articles de votre prénom, d’un pseudonyme constant (« La rédaction VM » + une page qui l’explique), ou les deux ?

**Données à fournir**

4. Statistiques Cloudflare Web Analytics des 30 derniers jours : visites, pages vues, pays, appareils.
5. Accès à Google Search Console : le site est-il vérifié ? Quelles requêtes apparaissent ?
6. Nombre d’abonnés et de membres par canal : Discord, Facebook (Pages), Instagram, TikTok, YouTube.
7. Revenus actuels : nombre de sponsors de la Pastille à 49 €/mois, articles partenaires vendus, clients VM Studio.

**Stratégie**

8. Les pronostics : les garder sur un sous-domaine séparé (`prono.velocemercato.fr`, ce qui est déjà le cas) et **les retirer de l’accueil du média** ? C’est ma recommandation.
9. Les projets hors sport (immo, emploi, CV, recettes, comparateur, boutique, allolivre, investisseurs) : on les **sort du menu et du sitemap** (ils restent accessibles), on les déplace sur vmunivers.fr, ou on les arrête ?
10. Quelle grille de prix VM Univers fait foi ? Je recommande les **packs Mini, Starter, Business et Max**, avec le studio en ligne comme porte d’entrée pour les visuels seuls. À confirmer.
11. Combien d’heures par semaine pouvez-vous consacrer à l’éditorial (relire, signer, publier), et combien à la vente (appels, rendez-vous) ?
12. Combien de temps pouvez-vous consacrer à une newsletter hebdomadaire, et quel outil préférez-vous ? Brevo (gratuit jusqu’à 300 envois par jour) ou Substack ?
