# Audit du site pour Claude

État mesuré le 2026-11-14T10:52:11.943765+01:00.

## Périmètre et limites

1397 pages HTML inventoriées. Toutes leurs cibles internes sont contrôlées dans le dépôt. 1644 URL uniques issues des liens externes, des cibles internes absentes et des sources des articles sont interrogées en HTTP.

Un statut 404 ou 410 indique une URL introuvable. Les refus 401/403, les limites 429, les erreurs serveur et les délais dépassés demandent une vérification complémentaire. Le test ne valide pas le visionnage géographique des vidéos ni la véracité des articles. Les classements signalés par mots-clés doivent être relus avant déplacement.

## Reprise de la demande de Romain

Retirer les accès transversaux aux anciennes applications et leurs invitations à installer. L’accueil doit commencer directement par le bureau. Garder un retour simple à l’accueil. Corriger tout texte sombre sur fond sombre. Réserver Multisport aux disciplines hors football et aux contenus sportifs réels. Réserver ses Pastilles au genre Multisport. Maintenir les conseils pronos fournis par Romain.

## Résultats

- Liens confirmés introuvables en HTTP, 11.
- Cibles internes absentes du dépôt, 76. Certaines peuvent être servies par Cloudflare, lire leur résultat HTTP avant correction.
- Ancres à vérifier, 3120. Certaines sont gérées par JavaScript.
- Articles à relire pour leur classement, 0.
- Replays réellement publiés par genre, {"foot": 44, "gaming": 16, "actus": 30}.

Le fichier JSON associé contient toutes les références, pages et lignes. Les chemins correspondent au commit indiqué dans ce rapport.

## Liens introuvables

- https://velocemercato.fr/a/rss-v2-0fe323c23f7a612ca6c326.html — HTTP 404 — a/rss-v2-65cd3432c413223448c834.html ligne 98
- https://velocemercato.fr/a/rss-v2-15cc0d0c1fb945e13acd04.html — HTTP 404 — a/rss-v2-6ab3de48dc62885beb0171.html ligne 98, a/rss-v2-66cd7ed54591009030f93b.html ligne 98, a/rss-v2-0e56b6523267e7888732b1.html ligne 98, a/rss-v2-a743813a8606f84a2f669b.html ligne 98
- https://velocemercato.fr/a/rss-v2-380707bcad068798301a11.html — HTTP 404 — a/rss-v2-c8fa11a66a1d4139905c49.html ligne 98, a/rss-v2-f6167c62a059f48c78c4b8.html ligne 98, a/rss-v2-e1d41ac5a71fabc8bdbdc5.html ligne 98
- https://velocemercato.fr/a/rss-v2-3d83d83e0a726382cf996f.html — HTTP 404 — a/rss-v2-65cd3432c413223448c834.html ligne 98
- https://velocemercato.fr/a/rss-v2-587df4721e1335551ef209.html — HTTP 404 — a/rss-v2-b65c9934943d806d9f1e07.html ligne 98, a/rss-v2-8646e7ce0963c32f39b1c4.html ligne 98, a/rss-v2-2ce2d9fab9ff0b8a423f0d.html ligne 98, a/rss-v2-92403cd6641532d005bdf2.html ligne 98, a/rss-v2-32c1cf9bc59edfdf838d25.html ligne 98, a/rss-v2-800049823dcd3f491efd0a.html ligne 98
- https://velocemercato.fr/a/rss-v2-61ccacd34ff367c1df1757.html — HTTP 404 — a/rss-v2-f906a43aa7939d2654e241.html ligne 98, a/rss-v2-766a655299e667b214a29f.html ligne 98, a/rss-v2-0bb48e2f5a2faee7e82fc3.html ligne 98, a/rss-v2-bbb701c167e3becab2e807.html ligne 98
- https://velocemercato.fr/a/rss-v2-810130c2ef3b3da48fb47f.html — HTTP 404 — a/rss-v2-b65c9934943d806d9f1e07.html ligne 98, a/rss-v2-8646e7ce0963c32f39b1c4.html ligne 98, a/rss-v2-2ce2d9fab9ff0b8a423f0d.html ligne 98, a/rss-v2-92403cd6641532d005bdf2.html ligne 98, a/rss-v2-32c1cf9bc59edfdf838d25.html ligne 98, a/rss-v2-800049823dcd3f491efd0a.html ligne 98
- https://velocemercato.fr/a/rss-v2-841da3198387c4bdf91a03.html — HTTP 404 — a/rss-v2-1252c0be11fe03ddab891d.html ligne 98, a/rss-v2-e141cfb3bdbb9780ad7959.html ligne 98, a/rss-v2-7c81de61dd2de44c21eaa9.html ligne 98, a/rss-v2-4b1444d2ece96ff3ec6149.html ligne 98, a/rss-v2-bcd7c0c57e2919025383b0.html ligne 98, a/rss-v2-bc7566ccf219a65c687066.html ligne 98
- https://velocemercato.fr/a/rss-v2-be40daf45e2ddae12fdf85.html — HTTP 404 — a/rss-v2-ac4c29696df906c79462d1.html ligne 98, a/rss-v2-e6c865520eebb34fd34d74.html ligne 98, a/rss-v2-6dbd59cb85d4514f745cf9.html ligne 98, a/rss-v2-1ab5f194879d8575932335.html ligne 98, a/rss-v2-f6b6af0c2c170ed5c07372.html ligne 98, a/rss-v2-874b393dbb6477e67fd0b1.html ligne 98
- https://velocemercato.fr/a/rss-v2-d35d05b8dc173e17198673.html — HTTP 404 — a/rss-v2-50b89266996a4a99045a00.html ligne 98
- https://velocemercato.fr/a/rss-v2-eb6dfe25fa63d6afffd5a5.html — HTTP 404 — a/rss-v2-b65c9934943d806d9f1e07.html ligne 98, a/rss-v2-8646e7ce0963c32f39b1c4.html ligne 98, a/rss-v2-2ce2d9fab9ff0b8a423f0d.html ligne 98, a/rss-v2-92403cd6641532d005bdf2.html ligne 98, a/rss-v2-32c1cf9bc59edfdf838d25.html ligne 98, a/rss-v2-800049823dcd3f491efd0a.html ligne 98

## Articles à relire


## Corrections déjà apportées dans cette reprise

- Le rendu Multisport ne charge plus fil.json ni une Pastille Foot. Les titres de jeux vidéo sont filtrés dans la collecte et dans les volets.
- Le style commun de lecture impose des couleurs lisibles et masque les anciennes invitations à installer.
- La préparation de publication applique la navigation simplifiée aux pages historiques et aux nouveaux articles.
- Le filtre Multisport existe dans le catalogue des Pastilles. Compléter les vidéos uniquement avec des publications confirmées.

## Travail restant pour Claude

Corriger les liens confirmés introuvables en s’appuyant sur leur fichier et leur ligne. Relire les anomalies de rubrique avec leurs sources. Contrôler les liens protégés depuis un accès autorisé. Vérifier ensuite l’accueil et les lecteurs sur téléphone. Refaire cet audit après les corrections et publier la version contrôlée.

L’en-tête ajouté par une éventuelle transformation Cloudflare doit aussi rester masqué sur le domaine. Les consignes et le contexte sont dans docs/PASSATION_VM_2026-11-10.md.
