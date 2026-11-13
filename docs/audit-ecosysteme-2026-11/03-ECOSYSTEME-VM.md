# 03 — Audit de cohérence de l’écosystème VM

## 1. Positionnement de chaque marque

| | Véloce Mercato | VM Univers |
|---|---|---|
| **Rôle** | Média : informer, fidéliser une audience | Studio : vendre des prestations aux pros |
| **Public** | Fans de foot (grand public, mobile) | Commerces, artisans, clubs, indépendants |
| **Modèle économique** | Publicité, sponsoring, partenariats | Prestations (packs, options, maintenance) |
| **Ton** | Rapide, direct, fun (manga, Pastille) | Rassurant, clair, concret (prix, délais) |
| **Promesse** | « Le foot qui bouge, vite et sourcé » | « Votre site et votre image pro, vus en direct avant de payer » |

## 2. Cohérence actuelle
[FAIT] Les liens entre les deux sites :
- les deux sites se renvoient constamment (vmunivers liste les médias ; Véloce Mercato affiche Studio, Pro local et Fauteuil VM Univers) ;
- les mentions légales communes citent « Véloce Mercato, VM Univers, Véloce Web Studio » (ancien nom) ;
- les démos du studio sont hébergées sur velocemercato.fr ;
- les pronostics sont présents sur les deux (VM Prono).

**Le risque de confusion est élevé :**
- un fan de foot se voit proposer un site internet ;
- un artisan atterrit sur un portail avec des pronostics ;
- un annonceur ne sait pas qui il paie (le média ou le studio).

## 3. Architecture de marque recommandée : « marque ombrelle discrète »

```
                 VM (signature commune, pas un site à part entière)
                 │
   ┌─────────────┴──────────────┐
VÉLOCE MERCATO               VM UNIVERS
(média, velocemercato.fr)    (studio, vmunivers.fr)
 ├ Foot (cœur)                ├ Création de sites
 ├ Multisport / Gaming /      ├ Identité visuelle
 │   Mangas (rubriques)       ├ Visibilité locale
 ├ La Pastille TV             └ Atelier en ligne (atelier.velocemercato.fr
 └ Discord / Newsletter          → à terme atelier.vmunivers.fr)
     ↘ VM Prono : prono.velocemercato.fr (18+, séparé, jamais en accueil)
```

**Les règles :**
1. **Chaque site a son propre en-tête, son propre menu et son propre appel à l’action.** Aucun menu commun.
2. **Les liens croisés se limitent au pied de page :**
   - sur Véloce Mercato : « Un média du réseau VM Univers » + « Annoncer » ;
   - sur VM Univers : « Réalisation : le média Véloce Mercato », dans les réalisations.
3. **La signature visuelle commune est légère** : couronne VM, noir, rouge et or. **Les typographies et le ton diffèrent** : sportif et manga pour le média, sobre et rassurant pour le studio.
4. **Le nom « Véloce Universe » est banni**, tout comme « Véloce Web Studio » : partout « VM Univers » et « Véloce Mercato ». À corriger dans les mentions légales.
5. **L’atelier** doit, à terme, passer sur un sous-domaine de vmunivers.fr (`atelier.vmunivers.fr`), avec une redirection 301 depuis l’ancienne adresse. Aujourd’hui, `atelier.velocemercato.fr` lie le studio au média. **[HYPOTHÈSE]** Cette migration demande un changement DNS : à faire avec ton accord.

## 4. Parcours entre les deux sites (sans cannibalisation)

| Depuis | Vers | Où | Pourquoi |
|---|---|---|---|
| Véloce Mercato, page `/publicite/` | VM Univers `/communication-publicite/` | Encadré « Pas encore de site ? Notre studio VM Univers peut le créer » | Un annonceur local a souvent aussi besoin d’un site |
| VM Univers `/realisations/` | Véloce Mercato | Étude de cas « Un média foot complet, construit par VM » | Preuve de savoir-faire |
| VM Univers `/communication-publicite/` | Véloce Mercato `/publicite/` | Option « Visibilité auprès des fans de foot de la région » | Vente croisée |
| Véloce Mercato, accueil | VM Univers | **Seulement** en pied de page | Ne pas polluer le média |

## 5. Synergies
1. **Le pack « Club & sponsors »** : VM Univers crée le site du club, Véloce Mercato couvre ses matchs (foot amateur), et les sponsors du club achètent de la visibilité sur le média. **[HYPOTHÈSE]** à tester avec 2 ou 3 clubs.
2. **Le pack « Commerce supporter »** : un commerce local achète son site (VM Univers) et une bannière ou la Pastille (Véloce Mercato) à un prix groupé.
3. **Le savoir-faire technique commun** : robots, scores, studio. C’est une vitrine pour VM Univers (« nous savons automatiser »).

## 6. Les réponses aux questions clés

**Véloce Mercato doit-il rester multithématique ?**
Non. **Il faut le recentrer sur le football.** Multisport, gaming et mangas restent comme rubriques secondaires dans un menu « Plus », sans place sur l’accueil au-delà d’un bloc compact. Le reste (immo, emploi, CV, recettes, comparateur, boutique, livres, investisseurs, produits locaux, météo) sort du média.

**Quels sous-univers garder, mettre en pause ou fusionner ?**

| Sous-univers | Décision | Raison |
|---|---|---|
| VM Foot | **Prioritaire** | Cœur de promesse |
| Foot amateur / Région | **Prioritaire, à fusionner** en « Foot de l’Est et amateur » | La niche |
| La Pastille TV | **Prioritaire** | Format signature, monétisable |
| VM Actu | **Fusionner** dans l’accueil (actu générale) ou mettre en pause | Doublon avec les grands médias |
| VM Multisport | **Garder, secondaire** | Audience complémentaire, scores multisport |
| VM Gaming | **Garder, secondaire** (EA FC et jeux de foot en priorité) | Lien foot via FC |
| VM Mangas | **Garder, secondaire** (Olive et Tom, École des champions) | Identité manga, lien foot |
| Véloce Arena | **Pause** si l’activité est faible ; sinon dans Discord | Communauté |
| Pépite FC | **Garder si actif**, en page jeunes talents | Lien foot |
| VM Studio (sur le média) | **Retirer du média**, il appartient à VM Univers | Cohérence |
| VM Prono | **Sous-domaine séparé**, jamais en accueil, pas sur les réseaux | Mineurs, annonceurs, ANJ |

**Quel client VM Univers doit-il cibler ?**
Les TPE de proximité qui vivent de la réservation ou de la commande (restauration rapide, coiffure et beauté, garages, artisans), plus les clubs amateurs.

**Quelle promesse commerciale ?**
« Votre site et votre image pro, à prix fixe, vus en direct avant de payer. »

**Comment éviter l’agence générique ?**
- montrer le direct (atelier) ;
- montrer les démos métiers testables ;
- publier les prix ;
- parler métier (« vos rendez-vous », « vos commandes ») plutôt que technique ;
- assumer un style visuel fort (noir et or, manga) en option.

**Comment utiliser Véloce Mercato comme preuve sans nuire au sérieux ?**
En **étude de cas** sur `/realisations/` : besoin, solution technique (robots, scores, vidéos automatiques), chiffres **mesurés** uniquement. Jamais en mélangeant les menus, et jamais avec les pronostics.

## 7. Stratégie de marque VM à 12 mois

| Période | Véloce Mercato | VM Univers |
|---|---|---|
| Mois 1-3 | Conformité, sitemap, accueil recentré, pages piliers, newsletter | Accueil commercial, tarifs unifiés, CGV, fiche Google, 3 études de cas |
| Mois 4-6 | Pages club de l’Est, « où regarder », 1 dossier par semaine, kit média avec audience réelle | 10 avis Google, prospection régulière, 2 pages locales, atelier sur `vmunivers.fr` |
| Mois 7-9 | Offres partenaires locales, sponsor de la Pastille, newsletter sponsorisée | Offre « Club & sponsors », partenariats (comptables, imprimeurs) |
| Mois 10-12 | Bilan : garder ce qui rapporte, arrêter les rubriques sans audience | Maintenance récurrente comme base de revenu, cas clients chiffrés |

## 8. Erreurs stratégiques à éviter
1. Ajouter de nouveaux sous-projets avant que le foot et le studio ne rapportent.
2. Publier plus de brèves automatiques sans valeur ajoutée (risque de déclassement pour « contenu à grande échelle »).
3. Vendre de la publicité sans chiffres d’audience vérifiables.
4. Mélanger les pronostics et paris avec le média grand public ou avec le studio.
5. Inventer des avis, des clients ou des chiffres (tromperie commerciale, et perte de confiance définitive).
6. Laisser coexister plusieurs grilles de prix.
7. Changer de domaine ou d’URL sans redirections 301.
8. Multiplier les comptes sociaux. Mieux vaut 1 Page Véloce Mercato et 1 Page VM Univers bien tenues, et des profils personnels utilisés seulement pour partager.
