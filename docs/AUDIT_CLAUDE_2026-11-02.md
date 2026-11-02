# Audit Claude — 2 novembre 2026 (soir)

Périmètre : `velocemercato.fr` (main à `92dce0639`, après PR #114 à #124) et `vmunivers` (main à `272093a`).
PR ouvertes examinées : #117 (VM Services), #125 (bouton VMUNIVERS.FR), #110 (filtres foot, ancienne).

Méthode : lecture du code et des diffs, suite de tests complète (Python + Node) avec Chromium,
captures d'écran 390 px (mobile) et 1366 px (ordinateur) servies en local, contrôle des liens
internes, contrôle des données JSON, revue sécurité manuelle (secrets, injection HTML, workflows).

Limites : le site en ligne n'était pas joignable depuis l'environnement d'audit (proxy) ; les
images et vidéos YouTube externes n'ont pas pu être chargées. **Les maquettes envoyées par
Heineguez ne sont pas dans les dépôts** : la comparaison visuelle porte sur l'identité commune
(noir, rouge néon, or) adoptée dans la PR #113 et VM Univers #25, pas sur un pixel-à-pixel.
Les tests automatiques ne remplacent pas un audit de sécurité complet.

## 1. Ce qui fonctionne

- Aucun lien interne cassé sur l'accueil, Foot amateur, Belfort, Actus, Mangas (+ 8 épisodes),
  Séries, Services, Multisport (11 sports), Pro, Découvrir, Soutenir — ni sur VM Univers.
- Aucune erreur JavaScript, aucun débordement horizontal à 390 px et 1366 px sur ces pages.
- **Foot amateur** : 36 titres du jour, filtre par région et par niveau opérationnel
  (`?region=BFC` → 4 titres), choix mémorisé, aucune position envoyée, titres échappés.
- **VM Belfort** : 46 titres frais (mise à jour 17 h 26), lien vers le foot amateur BFC.
- **VM Actu** : flux à jour, choix de région présent (PR #116).
- **VM MANGAS** : 8 pages épisodes avec lecteurs YouTube officiels (nocookie, au clic),
  8 séries annoncées « à venir », lien de repli vers YouTube.
- **VM Séries** : catalogue de 40 séries avec avertissement clair (aucun épisode hébergé).
- **VM Services (en ligne)** : recherche CBD / cavistes / taxis vers Google Maps, entrée bornée
  et encodée ; 5 tests Node passent.
- **Sécurité** : aucun secret ni jeton dans les dépôts ; les flux RSS sont échappés avant
  affichage et seuls les liens `https://` sont acceptés ; les 46 workflows déclarent leurs
  permissions ; Studio Express passe le corps d'issue par variable d'environnement et est
  réservé au propriétaire.

## 2. Ce qui est cassé ou incomplet

### Bloquant visuel
1. **Le bouton VMUNIVERS.FR n'est visible ni sur mobile ni sur ordinateur.** Les PR #123, #124
   et #125 modifient l'en-tête `header.sticky`, or `assets/vm-cinema-foot.css` le masque
   (`body.home-simple>header.sticky{display:none!important}`), tout comme la barre `.vmbar`.
   L'en-tête réellement affiché est `.vm-cinema-top`, qui n'a pas de lien VM Univers.
   Les premiers liens VM Univers visibles sont à ~8 400 px de haut sur mobile.
2. **PR #125 à ne pas fusionner** : elle ajoute `position:relative` en ligne sur un en-tête
   `sticky` (casse le collage) et positionne le bouton en absolu sur un élément… masqué.

### Identité visuelle
3. **L'accueil empile plusieurs décors** : `vm-reference-home`, `vm-mother-design`,
   `vm-cinema-home`, plus l'ancien thème bleu marine en dessous. Sur mobile, la première
   moitié est noir/rouge néon/or, puis à partir de ~4 800 px on retombe sur l'ancien
   bleu marine (Pastille TV, réseaux, pied de page).
4. **Six en-têtes différents** selon les rubriques (accueil, Mangas, Séries, Services,
   Foot amateur/Belfort, Actus) : logo, menu et couleurs changent d'une page à l'autre.
   Services affiche « VM UNIVERS » comme marque alors qu'il est sur velocemercato.fr.
5. Le menu du haut de l'accueil ne propose ni Foot amateur, ni VM Séries, ni VM Services, ni
   VM Univers (seulement via les tuiles).
6. Le « 87 » reste présent (héros de l'accueil, pastille de VM MANGAS). Une branche
   `fix/vm-mangas-marque-sans-87-2026-11-02` n'a jamais été fusionnée : décision à prendre.

### Contenus
7. **Pastille TV à l'arrêt depuis le 1er novembre** : les 9 dernières émissions sont
   `publie: false`, sans vidéo ; seule `foot-buts-20261101-1108` est publiée. Pas de page de
   partage pour elles. VM Belfort met encore en avant « La Pastille Actus : 23 octobre ».
8. Foot amateur : 5 régions sans aucun titre aujourd'hui (Hauts-de-France, Île-de-France,
   Nouvelle-Aquitaine, Occitanie, Outre-mer), Corse sur-représentée (14 / 36).
9. Multisport : 6 sports sur 11 vides (MotoGP, cyclisme, NHL, MLB, ski ; MMA 1 titre) ;
   dernière mise à jour 14 h 29.
10. VM Séries est un catalogue sans lien : rien à regarder ni à lire au clic.
11. VM MANGAS : 8 séries sur 24 cartes renvoient vers « à venir ».

### PR #117 (VM Services) — à corriger avant fusion
12. Supprime les catégories CBD et caviste alors que `/pro/` y renvoie toujours
    (`?categorie=cbd`, `?categorie=caviste`) : ces liens tomberaient silencieusement sur
    « Garages ».
13. Le choix « 10 / 20 / 40 minutes » est calculé puis ignoré (variable `m` inutilisée) :
    l'utilisateur croit filtrer par trajet, ce n'est pas le cas.
14. Aucun test navigateur ni capture fournis.

### Tests
15. **20 tests échouent sur velocemercato.fr et 8 sur VM Univers, mais ils échouaient déjà
    avant les PR de ChatGPT** (vérifié sur `d56708ec6` et `2a67d3e`) : ils visent l'ancien
    accueil (`.v2-hero`, version de cache `v6`, 28 projets…). Conséquence : plus aucun test
    ne protège l'accueil actuel. Plusieurs tests dépendent aussi des données du jour
    (émissions, identifiants Facebook) et échouent au gré des robots.
16. Hors CI, `pytest` et `playwright` ne sont pas installés par `tests/requirements.txt`
    seul (Playwright 1.62 épinglé).

### Hygiène du dépôt
17. ~100 branches distantes, dont beaucoup déjà fusionnées ; PR #110 ouverte depuis le matin.
18. Les robots poussent sur `main` toutes les quelques minutes : toute PR humaine doit être
    rebasée juste avant fusion.

## 3. Corrections prioritaires (dans l'ordre)

1. **Fermer #125 sans fusionner.** Ajouter le lien VMUNIVERS.FR dans `.vm-cinema-top`
   (l'en-tête réellement affiché), à droite du logo, mobile et ordinateur.
2. **Un seul décor d'accueil** : garder le bloc cinéma (noir / rouge néon / or), supprimer les
   styles morts (`vm-reference-home`, `vm-mother-design`, en-tête masqué, `.vmbar` masquée)
   et passer la moitié basse (Pastille TV, réseaux, pied de page) aux mêmes couleurs —
   **après validation sur les maquettes**, que Heineguez doit ajouter au dépôt
   (`maquettes/`) pour que Claude et ChatGPT travaillent sur la même référence.
3. **Un en-tête commun** pour toutes les rubriques (même logo, même menu incluant Foot,
   Actu, Multisport, Mangas, Séries, Services, VM Univers).
4. **Relancer la Pastille TV** : diagnostiquer pourquoi les émissions depuis le 1er novembre
   ne sont pas publiées (workflow `emissions.yml` / `diffusion.yml`) ; retirer l'encart
   « 23 octobre » de VM Belfort tant qu'il n'y a pas d'émission récente.
5. **PR #117** : garder CBD / caviste / taxi en plus des nouvelles catégories (ou mettre à jour
   `/pro/`), retirer le sélecteur de minutes ou l'assumer comme simple texte.
6. **Remettre les tests d'accueil à jour** sur l'accueil actuel et rendre les tests de données
   indépendants du contenu du jour.
7. Élargir les sources du foot amateur pour les 5 régions vides ; compléter Multisport.

## 4. Ce qui peut être publié sans risque excessif

- Déjà en ligne et sans régression détectée : Foot amateur, VM Belfort, VM Actu (région),
  VM MANGAS, VM Séries (catalogue), VM Services (version CBD / caviste / taxi).
- Publiable après une petite correction : le lien VMUNIVERS.FR dans l'en-tête cinéma
  (une ligne, facile à annuler).
- **À ne pas publier** : PR #125 (casse l'en-tête collant, sans effet visible), PR #117 en l'état,
  toute refonte de décor sans maquette de référence dans le dépôt.

## Règles de reprise pour Claude et ChatGPT

- Une PR = un sujet ; capture mobile 390 px **et** ordinateur avant/après dans la PR.
- Avant de modifier un élément, vérifier qu'il est visible (`getComputedStyle(...).display`).
- Ne pas ajouter de nouveau bloc `<style>` dans `index.html` par-dessus les anciens : modifier
  ou supprimer l'existant.
- Rebaser sur `main` juste avant fusion (robots actifs).
