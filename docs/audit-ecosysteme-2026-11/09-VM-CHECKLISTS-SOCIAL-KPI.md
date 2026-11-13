# 09 — Véloce Mercato : checklists, stratégie éditoriale, Discord, newsletter, vidéos courtes, KPI

## 1. Stratégie éditoriale hebdomadaire réaliste
Hypothèse : 1 personne, aidée par les robots. Environ 1 h par jour pour la relecture et la publication, et 3 h par semaine pour le dossier.

| Jour | Site | Pastille TV | Réseaux | Newsletter / Discord |
|---|---|---|---|---|
| Lundi | Bilan du week-end : 1 article « Ce qu’il faut retenir » (L1 + Est + amateur) | Pastille « Le week-end en 2 min » | 1 Short résultats | Discord : sondage « joueur du week-end » |
| Mardi | Brèves + 1 page match LDC (si soir de match) | Pastille du jour | 1 Reel mercato (Officiel / Rumeur) | — |
| Mercredi | Brèves + **dossier de la semaine** (original) | Pastille | 1 carrousel « dossier en 5 images » | — |
| Jeudi | Brèves + mise à jour des pages mercato club | Pastille | 1 Short « vrai ou faux mercato » | **Newsletter « Le Mercato en 5 minutes »** (envoi à 18 h) |
| Vendredi | Pages match du week-end + « Où regarder » | Pastille « Programme du week-end » | 1 Reel « où regarder ce week-end » | Discord : prédictions **sans paris** (score exact pour le fun, avec classement) |
| Samedi | Scores en direct + brèves | — | Stories résultats | Discord : salon live des matchs |
| Dimanche | Résultats + foot amateur (envois des clubs) | — | 1 Short « le but du week-end » (sans images télé) | — |

**Volume conseillé :**
- 8 à 15 brèves par jour, à forte valeur ;
- 1 dossier par semaine ;
- 1 Pastille par jour en semaine.

**Mieux vaut moins, mais mieux** que 50 brèves de reformulation.

## 2. Checklist technique avant mise en ligne (chaque page ou modèle)
- [ ] Un seul H1, des H2 logiques
- [ ] Title de 50 à 60 caractères et meta description de 140 à 155 caractères, uniques
- [ ] Canonical sur l’URL de la page elle-même
- [ ] Page présente dans le bon sitemap ; `noindex` seulement si c’est voulu
- [ ] JSON-LD valide (outil de test des résultats enrichis de Google)
- [ ] Open Graph : titre, description, **image propre à la page** (1200 × 630)
- [ ] Images en WebP/AVIF, avec `width`/`height`, `alt` rempli, `lazy` sous la ligne de flottaison
- [ ] Contenu principal visible en HTML sans JS
- [ ] Pas d’état « Chargement… » visible sans contenu de secours
- [ ] PageSpeed mobile : LCP < 2,5 s, CLS < 0,1, INP < 200 ms *(objectifs Google)*
- [ ] Aucune requête vers Google Fonts ; YouTube en nocookie et au clic
- [ ] Liens internes : fil d’Ariane, page pilier, « À lire aussi »
- [ ] Test à 320, 390, 768 et 1300 px : pas de débordement
- [ ] Navigation au clavier possible, focus visible
- [ ] Liens externes vérifiés (pas de 404)
- [ ] Mentions légales, confidentialité et cookies liées dans le pied de page

## 3. Checklist qualité avant publication d’un article
- [ ] **Le fait est-il vrai ?** Au moins 1 source fiable ; 2 si le sujet est sensible ; la source primaire si elle existe
- [ ] Étiquette mercato correcte (Officiel / En discussion / Rumeur)
- [ ] Conditionnel pour les infos non confirmées ; aucun montant sans source
- [ ] **Valeur ajoutée** par rapport à la source : contexte, conséquence ou lien utile
- [ ] Titre précis, sans piège à clics ; le mot-clé au début
- [ ] Chapô qui répond à qui, quoi, quand
- [ ] Noms, clubs et dates vérifiés (orthographe incluse)
- [ ] Image avec droits ; alt rempli
- [ ] Lien vers la page pilier + bloc « À lire aussi »
- [ ] Auteur, date et mention IA si l’IA a été utilisée
- [ ] Aucun contenu de paris, aucune cote, aucun lien d’opérateur
- [ ] Contenu payé ? Étiquette + `rel="sponsored"`
- [ ] Pas de vie privée, pas de données de mineurs

## 4. Checklist de publication (après mise en ligne)
- [ ] URL accessible, aperçu du partage correct (image et titre)
- [ ] Présent dans le sitemap et dans le sitemap News si l’article a moins de 48 h
- [ ] Partagé sur les réseaux (texte adapté, étiquette partenariat si besoin)
- [ ] Lien posté dans le bon salon Discord
- [ ] Ajouté à la sélection de la newsletter si c’est un sujet fort
- [ ] Anciennes rumeurs liées mises à jour (si c’est un transfert officiel)

## 5. Checklist de conformité (trimestrielle)
- [ ] Mentions légales à jour (éditeur, directeur de la publication, hébergeur)
- [ ] Politique de confidentialité à jour (prestataires, durées)
- [ ] Aucun nouveau traceur sans consentement (contrôle des requêtes du navigateur)
- [ ] Étiquettes publicitaires présentes sur 100 % des contenus payés
- [ ] Mentions IA présentes (brèves, Pastille, YouTube)
- [ ] Pronostics : 18+, Joueurs Info Service, pas sur l’accueil ni sur les réseaux
- [ ] Demandes RGPD et corrections traitées et tracées
- [ ] Droits des images vérifiés (échantillon de 20 articles)

## 6. Stratégie Discord
**Rôle** : le salon des fidèles, et la source de contenus originaux (avis, prédictions, résultats amateurs).
- **Structure** :
  - `#annonces` (lecture seule) ;
  - `#mercato` ;
  - `#ligue-1` ;
  - `#foot-de-l-est` ;
  - `#foot-amateur-resultats` ;
  - `#match-en-direct` ;
  - `#gaming-fc` ;
  - `#mangas` ;
  - `#suggestions` ;
  - `#règlement`.
- **Rituels** :
  - sondage du lundi ;
  - prédictions du vendredi **sans argent**, avec un classement mensuel et un badge ;
  - live chat des matchs.
- **Retour vers le site** : chaque annonce = 1 lien article ; le meilleur message de la semaine est cité dans la newsletter (avec l’accord de son auteur).
- **Modération** : règlement épinglé (pas de haine, pas de paris, pas de données personnelles), 2 modérateurs bénévoles à recruter.
- **KPI** : membres, membres actifs par semaine, messages par semaine, clics vers le site.

## 7. Stratégie newsletter — « Le Mercato en 5 minutes »
- **Outil** : Brevo (français, plan gratuit) *(alternative : Substack)*. Double confirmation de l’inscription.
- **Rythme** : chaque jeudi à 18 h.
- **Contenu** :
  1. Les 3 officiels de la semaine.
  2. Les 3 rumeurs qui montent, avec notre niveau de confiance.
  3. Le foot de l’Est (2 infos).
  4. La Pastille de la semaine.
  5. Le sondage Discord.
  6. 1 encart partenaire étiqueté (quand il y en a un).
- **Points d’inscription** : en bas des articles, sur `/mercato/`, sur l’accueil, sur Discord, en bio des réseaux.
- **Promesse d’inscription** : « Tout le mercato de la semaine en 5 minutes, chaque jeudi. Gratuit, sans spam. »
- **KPI** : abonnés, taux d’ouverture, taux de clic, désinscriptions.

## 8. Plan de contenu TikTok / Shorts / Reels
**Règle d’or** : jamais d’images de matchs ni de logos utilisés sans droit. Les visuels viennent de VM (cartes, Pastille, motion design).

| Format | Durée | Fréquence | Structure | CTA |
|---|---|---|---|---|
| **Officiel ou Rumeur ?** | 20-30 s | 3 par semaine | Accroche « Vrai ou faux ? » → 3 infos avec étiquette → verdict | « Tout le mercato : lien en bio » |
| **La Pastille express** | 45-60 s | Quotidien (découpe de la Pastille) | 3 sujets, sous-titres | « JT complet sur velocemercato.fr » |
| **Où regarder ce week-end** | 15-20 s | Vendredi | Liste des 5 matchs + chaînes | « Programme complet en bio » |
| **Le foot de l’Est en 30 s** | 30 s | Lundi | Résultats des clubs de l’Est | « Résultats amateurs sur le site » |
| **Le dossier en 5 images** | Carrousel | Mercredi | 1 chiffre ou idée par image | « Lire le dossier » |
| **Question Discord** | 15 s | Samedi | Question polémique (sans paris) | « Réponds sur Discord » |

**Toujours** : sous-titres incrustés, accroche dans les 2 premières secondes, mention « contenu généré avec IA » si la voix est synthétique (étiquette de la plateforme), lien en bio vers une page « liens » qui mène au site, à la newsletter et au Discord.

## 9. Tableau de bord KPI hebdomadaire (Véloce Mercato)
| Indicateur | Source | Sem. 1 | Sem. 2 | Sem. 3 | Sem. 4 | Tendance |
|---|---|---|---|---|---|---|
| Visites du site | Cloudflare Web Analytics | | | | | |
| Pages vues par visite | Cloudflare | | | | | |
| Pages indexées | Search Console | | | | | |
| Impressions Google | Search Console | | | | | |
| Clics Google | Search Console | | | | | |
| Top 5 requêtes | Search Console | | | | | |
| Articles publiés / dont dossiers | Site | | | | | |
| Corrections publiées | `/sources-et-corrections/` | | | | | |
| Vues Pastille (YouTube + réseaux) | Plateformes | | | | | |
| Abonnés par réseau | Plateformes | | | | | |
| Clics réseaux vers le site | Cloudflare (sources) | | | | | |
| Abonnés newsletter / ouverture / clic | Brevo | | | | | |
| Membres Discord actifs | Discord Insights | | | | | |
| Abonnés alertes but | OneSignal | | | | | |
| Demandes annonceurs | Formulaire | | | | | |
| Revenu publicitaire du mois | Comptabilité | | | | | |
| LCP / CLS mobile (accueil) | PageSpeed | | | | | |

**Décision chaque lundi** : quelle rubrique a progressé, laquelle stagne, et une seule action pour la semaine.
