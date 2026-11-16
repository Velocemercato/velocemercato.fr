# VM — Le nouveau studio 3D

Créé pour Romain le 16 novembre 2026. Direction visuelle : bleu nuit, or champagne et cyan. Le robot **VM Pronos** présente un journal avec **Pablo**, **Black**, **Scorpion** et **la créatrice**. Les humains sont des personnages fictifs, sans prétention de ressemblance avec des personnes réelles. Le nom de la créatrice reste à préciser par Romain.

## Les livrables

- `VM-Journal-3D-16-novembre-2026.mp4` : 10 minutes, format 16:9.
- `VM-Pastille-3D-16-novembre-2026.mp4` : 2 min 30, format 16:9.
- `VM-Reel-3D-16-novembre-2026.mp4` : 60 secondes, format 9:16.
- `VM-plateau-3D.blend` : scène 3D avec les cinq personnages, les caméras, le mobilier et les matériaux.
- `scriptpack.json` : textes parlés et sources de l’édition.
- `voice-manifest.json` : attribution des répliques et durées des voix.
- `edit/*/titres.ass` : sous-titres éditables, bandeaux et habillage.

## Direction artistique

Décor circulaire, table flottante, grand mur de rédaction, lignes architecturales dorées, globe animé. La mascotte conserve son casque, son micro, son visage blanc et bleu et son nœud papillon doré. Pablo porte des lunettes et une veste crème ; Black un costume bleu ; Scorpion une veste or ; la créatrice des touches cyan et une chevelure bouclée. Tous portent des micros.

Animation 3D stylisée : mouvements de tête, mains de la mascotte, clignements, expressions de bouche et déplacements de caméra. Les bouches sont animées de façon illustrative, sans synchronisation phonème par phonème. Les plans sont interpolés à 24 images par seconde au montage. Les voix sont synthétiques et ne reproduisent aucune voix personnelle fournie par Romain.

## Fabrication

1. Installer Blender 4.3+, FFmpeg avec libass, les polices DejaVu, Python 3.12+, `piper-tts==1.8.0`, NumPy et SciPy.
2. Placer les modèles français Piper UPMC et SIWIS dans `voices/` à la racine du projet. Les modèles ne sont pas copiés dans cette archive. Le script `production_assets.py` en récupère les versions publiques pour le circuit automatisé.
3. Générer les voix avec `python vm-studio-2026/build_voices.py`.
4. Générer la musique avec `python vm-studio-2026/build_music.py`.
5. Générer les plans avec `blender -b --python vm-studio-2026/build_studio.py`. `VM_SHOTS` sélectionne les plans, `VM_RENDER_FRAMES` leur longueur, `VM_RENDER_WIDTH` et `VM_RENDER_HEIGHT` leur définition native. Le portrait utilise un cadrage distinct.
6. Monter avec `python vm-studio-2026/edit_programmes.py`.

La scène Blender conserve également des clés d’animation, des caméras nommées, des repères de plans et les polices intégrées. Le code de création est inclus dans un bloc texte Blender.

Les sources Blender créent réellement les volumes 3D ; elles ne déplacent pas une image fixe. Les boucles courtes du plateau sont réutilisées au montage. Les titres et sous-titres sont rendus à la définition finale.

## Pour Claude demain

Repartir de cette scène et des scripts, pas d’une reconstruction visuelle. Conserver les noms VM Pronos et Pablo. Pour une nouvelle édition, remplacer les faits et les sources, refaire les voix et adapter les dates d’écran. Le moteur de cette livraison est volontairement limité au 16 novembre : il ne doit pas republier les anciennes nouvelles automatiquement.

Améliorations possibles : rig facial avec visèmes, plusieurs gestes par personnage, nouvelles caméras, actualisation quotidienne structurée et validation éditoriale des résultats. Une musique plus longue peut être composée à partir du code existant. Gemini n’est pas une dépendance de cette production.

## Diffusion

La diffusion ponctuelle réutilise les connexions chiffrées du dépôt existant. Destinations autorisées par Romain : les trois pages Facebook VeloceMercato, VMunivers.fr et VM actus et pronos ; les deux Instagram @veloce.mercato et @vmunivers.fr ; le JT sur la chaîne YouTube configurée. Aucun Instagram n’est associé au jeton de la page Pronos. Les secrets ne figurent dans aucun fichier de ce dossier.

Le script conserve un reçu avant chaque envoi et ne renvoie pas une vidéo déjà tentée. Une confirmation de traitement reste distincte d’une publication confirmée. Les confirmations et les liens sont conservés séparément, sans identifiant de connexion.

## Crédits

Scène, personnages, animation, musique instrumentale et habillage : création originale pour VM. Voix de synthèse Piper : modèle UPMC, corpus sous CC BY-SA 4.0 ; modèle SIWIS, corpus sous CC BY 4.0. Rythme et hauteur modifiés pour distinguer les personnages. Cartes de modèles dans `licenses/`. Respecter ces crédits lors de la réutilisation des voix. Les sources des faits sont dans `scriptpack.json` et la description des publications.
