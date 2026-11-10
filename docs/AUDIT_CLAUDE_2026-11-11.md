# Audit du site pour Claude

État mesuré le 2026-11-11T00:34:56.441307+01:00.

## Périmètre et limites

179 pages HTML inventoriées. Toutes leurs cibles internes sont contrôlées dans le dépôt. 437 URL uniques issues des liens externes, des cibles internes absentes et des sources des articles sont interrogées en HTTP.

Un statut 404 ou 410 indique une URL introuvable. Les refus 401/403, les limites 429, les erreurs serveur et les délais dépassés demandent une vérification complémentaire. Le test ne valide pas le visionnage géographique des vidéos ni la véracité des articles. Les classements signalés par mots-clés doivent être relus avant déplacement.

## Reprise de la demande de Romain

Retirer les accès transversaux aux anciennes applications et leurs invitations à installer. L’accueil doit commencer directement par le bureau. Garder un retour simple à l’accueil. Corriger tout texte sombre sur fond sombre. Réserver Multisport aux disciplines hors football et aux contenus sportifs réels. Réserver ses Pastilles au genre Multisport. Maintenir les conseils pronos fournis par Romain.

## Résultats

- Liens confirmés introuvables en HTTP, 0.
- Cibles internes absentes du dépôt, 0. Certaines peuvent être servies par Cloudflare, lire leur résultat HTTP avant correction.
- Ancres à vérifier, 219. Certaines sont gérées par JavaScript.
- Articles à relire pour leur classement, 2.
- Replays réellement publiés par genre, {"foot": 40, "actus": 31, "gaming": 17}.

Le fichier JSON associé contient toutes les références, pages et lignes. Les chemins correspondent au commit indiqué dans ce rapport.

## Liens introuvables


## Articles à relire

- multisport/actualites.json — nba — GTA VI explose les attentes en précommandes chez Take-Two, NBA 2K27 en ferait les frais - Xboxygen — Titre hors discipline ou jeu vidéo
- vm-gaming/news.json — rss-v2-fb08bad3c8ffff4fb8746d — One Piece : le chapitre 1199 reporté, la piste du 30e anniversaire — À relire, aucun indice net de la rubrique dans la brève

## Corrections déjà apportées dans cette reprise

- Le rendu Multisport ne charge plus fil.json ni une Pastille Foot. Les titres de jeux vidéo sont filtrés dans la collecte et dans les volets.
- Le style commun de lecture impose des couleurs lisibles et masque les anciennes invitations à installer.
- La préparation de publication applique la navigation simplifiée aux pages historiques et aux nouveaux articles.
- Le filtre Multisport existe dans le catalogue des Pastilles. Compléter les vidéos uniquement avec des publications confirmées.

## Travail restant pour Claude

Corriger les liens confirmés introuvables en s’appuyant sur leur fichier et leur ligne. Relire les anomalies de rubrique avec leurs sources. Contrôler les liens protégés depuis un accès autorisé. Vérifier ensuite l’accueil et les lecteurs sur téléphone. Refaire cet audit après les corrections et publier la version contrôlée.

L’en-tête ajouté par une éventuelle transformation Cloudflare doit aussi rester masqué sur le domaine. Les consignes et le contexte sont dans docs/PASSATION_VM_2026-11-10.md.
