# Minute VM manga — 16 novembre 2026

Format livré : 58,64 secondes, 720 × 1280, H.264/AAC. Budget demandé : zéro achat, zéro abonnement supplémentaire.

Heineguez présente en veste dorée. Pablo est chauve. Black conserve sa veste marine. Scorpions est un homme âgé en veste turquoise. La créatrice est retirée.

Les 15,168 premières secondes utilisent une animation HeyGen avec un audio français fourni (vidéo source `773d59527582c025aaa8dad488c62ac1`). Les autres interventions sont des portraits manga fixes montés avec sous-titres et voix distinctes. Ce fichier n'est pas un JT de dix minutes ni une animation complète des quatre personnages.

## Fichiers et reprise

- `prepare.py` : voix françaises Edge TTS à vitesse naturelle, sans transformation de hauteur.
- `manifest.json` : textes, voix et temps des mots.
- `render.py` : montage vertical et sous-titres. Requiert FFmpeg, DejaVu Sans et les images `../assets/{heineguez,pablo,black,scorpions}-presentateur.png`.
- `publish.py` : diffusion ponctuelle vers les trois pages Facebook et deux comptes Instagram autorisés, avec vérification des identités, empreinte SHA-256 et reçus chiffrés avant chaque envoi.
- `.github/vm-manga-free-release.json` : demande datée et média examiné.

Les médias ne sont pas tous inclus dans Git. Le fichier final est conservé à l'adresse publique suivante : https://resource2.heygen.ai/video/9877ffba2fa34c0a95f0f21b4eaf143b/original.mp4

Avatars/source images importées dans HeyGen : Heineguez `74ebaf546eb24b8fbbde04df5079875a`, Pablo `623179956b9d49f5870d6a3828983adc`, Black `59d13c11c4214ad29110c5d4a0359b4a`, Scorpions `562e2b1337c94dccb21053901b1bcd2e`. Récupérer ces médias autorisés avant une reprise; le dépôt seul n'est pas autonome.

## Vérifications effectuées

Décodage vidéo/audio complet sans erreur; dimensions, durée et codecs vérifiés; images représentatives inspectées; niveau maximal audio mesuré à −4 dBFS. L'écoute subjective et une vérification intégrale de la synchronisation labiale n'ont pas été réalisées. Actualités vérifiées auprès de la FFF, de Rockstar et des comptes rendus du classement rugby, avec sources dans la légende.

## Diffusion

Exécution dédiée : https://github.com/Velocemercato/velocemercato.fr/actions/runs/43932124571

Consulter son artefact et les reçus pour connaître le résultat réel. Ne pas recréer une publication dont l'état est incertain. Aucune publication récurrente des JT longs n'est configurée par ce workflow ponctuel.
