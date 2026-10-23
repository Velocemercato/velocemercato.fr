# Démonstrations illustrées — reprise VM Univers / Véloce Web Studio

Demande : intégrer les images directement dans les démonstrations existantes, avec une présentation claire, en conservant les créations et les offres déjà ajoutées par Claude. Branche de travail : `codex/demos-images-vm`.

## Périmètre

- Sept démonstrations : `demos/coiffeur.html`, `beaute.html`, `restaurant.html`, `snack.html`, `artisan.html`, `drive.html`, `cbd.html`.
- Illustration manga du projet VM sur `investisseurs.html`.
- Aperçus photographiques des sept modèles sur `web-studio.html#modeles`.
- Kit partagé : `demos/kit/vm-demo.js` et `demos/kit/vm-demo.css`.

Les noms fictifs, palettes, offres, prix et parcours de réservation / commande / devis proviennent des modèles existants. Les pages d’accueil VM Univers et Véloce Mercato gardent leur rangement par annuaire et par média.

## Visuels et chemins

La commande contient **74 images distinctes** : huit images principales en portrait 4:5, vingt-cinq images de galerie carrées, quarante et une photos de produits en paysage 16:10. Création une par une dans l’ordre fourni, sans texte ni marque dans les images. Le visuel « investir » est une illustration manga ; les autres sont photoréalistes.

Les fichiers utilisés par les sites sont des WebP optimisés, sous `demos/img/<métier>/`. Les chemins prévus par les modèles sont conservés : par exemple `coiffeur-hero` correspond à `demos/img/coiffeur/hero.webp`, et `snack-pizza-orientale` à `demos/img/snack/pizza-orientale.webp`. Le registre `demos/img/catalogue.json` répertorie les noms demandés, les chemins, les dimensions réelles et les poids mesurés.

Les originaux PNG portant les noms demandés sont conservés dans le dossier de travail `/workspace/vm-demo-assets/images/`, à part du dépôt publié. Une archive de reprise reste dans `/workspace/vm-demo-assets/`. Ces chemins locaux sont destinés à l’environnement de travail ; les WebP sont accessibles dans le dépôt GitHub.

## Choix d’intégration

- Charger immédiatement la photo principale ; charger progressivement les galeries et les produits.
- Garder le portrait 4:5 sur téléphone et les produits entiers dans leurs cartes.
- Réutiliser les galeries pertinentes pour les prestations et les cartes cadeaux afin d’éviter les images cassées.
- Présenter les membres fictifs de l’équipe par leurs icônes lorsque leur portrait n’a pas été demandé, sans attribuer une photo de client à un membre d’équipe.
- Conserver les exemples avant / après de l’artisan dans un volet secondaire : ils attendent les vrais visuels du futur client.
- Les fichiers vidéo manquants portent `data-video-pending`. Ils restent dans un volet secondaire avec « Vidéo à venir », sans lecture factice ni requête vers un MP4 absent. Pour activer une vraie vidéo, fournir le fichier, remplacer l’attribut par `data-video` et ajouter son poster réel.
- Les photos des galeries s’ouvrent aussi au clavier ; la touche Échap ferme l’agrandissement et rend le focus à la photo.
- Les avis et les entreprises restent explicitement fictifs. L’analyse de laboratoire en image est identifiée comme une illustration, sans valeurs ni certification inventées.
- Le bandeau de chaque démo donne un accès direct à VM Univers. Les scripts et styles modifiés ont une URL versionnée pour actualiser les caches.

## Vérifications et reprise

Depuis la racine du dépôt, avec les dépendances de `tests/requirements.txt` et Chromium :

```sh
PYTHONPATH=tests python -m unittest test_demo_media test_professional
node --check demos/kit/vm-demo.js
git diff --check
```

Les tests des médias contrôlent les chemins d’images, huit pages à 320 / 390 / 1440 pixels, l’agrandissement au clavier, les vidéos à venir et le panier après recherche d’un produit. Les tests professionnels contrôlent les formulaires et les offres.

Avant une nouvelle modification, récupérer la dernière version de `main` et lire son diff : plusieurs outils et les robots d’actualités peuvent écrire sur le dépôt. Préserver les images de cette livraison et les fonctionnalités des modèles en réconciliant les changements fichier par fichier.
