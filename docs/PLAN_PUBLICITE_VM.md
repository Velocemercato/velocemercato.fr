# Campagne VM : trouver le bon public et donner une raison de revenir

VM Univers sert d’annuaire central. Véloce Mercato garde sa promesse football ; VM Actus et VM Gaming ont leurs pages dédiées. Chaque vidéo mène vers le projet présenté. Aucun chiffre d’audience, résultat sportif ou classement promotionnel n’est inventé.

## Les premières publications

Publier les clips progressivement : l’annuaire VM, le football, le gaming, les actus, puis les projets de studio et de bureaux. Épingler la présentation de chaque marque sur son propre profil. Les vues du studio et des bureaux sont des concepts virtuels ; conserver cette précision dans le texte de publication.

Garder les comptes VM Univers distincts de ceux de Véloce Mercato. En attendant leur création, les liens Facebook, Instagram et TikTok du portail restent ceux de Véloce Mercato, avec leur nom clairement indiqué. L’existence d’un lien ne signifie pas que le compte est connecté au système de publication.

## Une cadence tenable

- Conserver les actualités et les JT dans leur calendrier éditorial existant.
- Ajouter deux ou trois présentations de projet par semaine, plutôt que six publicités le même jour.
- Réutiliser les clips en stories avec une question simple et pertinente : « Quel projet veux-tu découvrir ? » ou « Foot, actus ou gaming ? ».
- Sur un profil VM Univers, mettre l’annuaire en lien de présentation ; sur un profil Véloce Mercato, mettre le site football. Les publications ciblées renvoient directement au projet concerné.

## Ce qui fera progresser les sites

1. Une promesse claire par page, un bouton principal et une bonne vitesse sur téléphone.
2. Des informations sourcées et à jour, des titres précis, des vidéos courtes et lisibles sans son.
3. Des retours réels : demander quel service manque et corriger les points de friction observés.
4. Des liens de campagne par réseau pour distinguer les clics quand les statistiques privées seront reliées. Ne pas confondre vues d’une vidéo, clics vers le site et visiteurs uniques.

Les fichiers `PUBLICATIONS_RESEAUX.csv` donnent des liens balisés par réseau. Les paramètres de campagne ne collectent aucun nom de visiteur. Aucun tableau de fréquentation n’a été activé dans cette modification, et aucun résultat de campagne n’est revendiqué.

## Diffusion et formats

Six clips de 20 secondes, chacun en MP4 H.264/AAC, 30 images/s : vertical 1080 × 1920 pour les réseaux ; horizontal 1280 × 720 pour les lecteurs des sites. Textes intégrés, fichiers VTT/SRT et musique originale. Les clips ne contiennent pas de narration vocale.

La page `decouvrir.html` de chaque site permet la lecture volontaire et le téléchargement. Les vidéos ne démarrent pas automatiquement et ne sont pas préchargées sur l’accueil.

La mise en ligne sur GitHub Pages ne publie pas un Reel Facebook, Instagram ou TikTok. Ces plateformes nécessitent les comptes et leurs autorisations officielles ; aucun nouvel envoi natif sur ces réseaux n’est confirmé par cette campagne.

## Reproduire le montage

Depuis le dépôt VM Univers, avec Python, NumPy, Pillow et ffmpeg :

```sh
python tools/creer_musique_promo.py --output media/projets/musique-originale.wav
python tools/creer_promos.py --manifest tools/campagne.json --assets media/projets/sources --music media/projets/musique-originale.wav --output media/promos --vm-root . --veloce-root ../velocemercato.fr
```

Les captures des pages sont des supports de présentation ; les refaire si l’interface change. Les sources des projets restent les sites eux-mêmes.
