# Trois JT VM — 16 novembre 2026

Trois éditions complètes en français, réalisées sans achat ni génération payante.
Portraits manga illustrés : il ne s’agit pas d’animations labiales. Les quatre
personnages parlent avec des voix de synthèse distinctes. Heineguez présente ;
Pablo est chauve, Black porte une veste bleu nuit et Scorpions est un homme âgé.

| Édition | Durée | Fichier public |
|---|---:|---|
| Actus | 10 min 07 | [MP4](https://resource2.heygen.ai/video/089b27955f034257b9b0269ff0faf3f2/original.mp4) |
| Sport | 10 min 05 | [MP4](https://resource2.heygen.ai/video/95b8f810b2bc4474af676d5faafbc1e7/original.mp4) |
| Gaming | 10 min 02 | [MP4](https://resource2.heygen.ai/video/760423b7aa544b2fb30e1c88260c99a0/original.mp4) |

## Contenu et sources

- [Actus](actus.txt) : textes par intervenant et sujet.
- [Sport](sport.txt) : textes par intervenant et sujet.
- [Gaming](gaming.txt) : textes par intervenant et sujet.
- [Sources](sources.json) : liens officiels et médias consultés le 16 novembre.
- [Production](production.json) : distribution, voix, durées, URLs et empreintes SHA-256.
- [Portraits](portraits.json) : images approuvées et empreintes.

Les exemples pédagogiques sont annoncés comme fictifs. Les résultats et annonces
sont distingués des rendez-vous à venir. Les éditions sont enregistrées et datées,
pas en direct. Aucune séquence d’actualité tierce n’a été réutilisée.

## Reproduire le montage

Python avec edge-tts, FFmpeg et FFprobe sont nécessaires. Les fichiers PNG indiqués
dans portraits.json doivent être placés dans ../assets/ sous leur nom de personnage
suivi de -presentateur.png. Vérifier leurs empreintes après téléchargement.

Exécuter `python prepare.py actus`, puis `python render.py actus` et
`python verify.py actus`. Répéter avec sport et gaming. Les textes déterminent
les scènes ; les durées proviennent de la narration à sa vitesse naturelle.
Les exports sont en H.264/AAC, 720 × 1280, 25 images/s, audio stéréo 48 kHz.

Le décodage intégral des trois exports a réussi. Les crêtes audio restent sous
0 dBFS. Des images représentatives des trois éditions ont été examinées.
Le contrôle audio est technique ; il ne prétend pas être une écoute humaine.

## Publication autorisée

Le workflow ponctuel vm-jt-manga-free-20261116.yml lit uniquement le manifeste
.github/vm-jt-manga-free-20261116.json. Les trois vidéos sont destinées aux pages
VeloceMercato, VMunivers et VM actuspronos, ainsi qu’aux comptes Instagram
@veloce.mercato et @vmunivers.fr. Aucun horaire récurrent n’est créé par ce workflow.
Les reçus sont conservés avant et après chaque écriture. Un envoi incertain n’est
pas répété automatiquement. Les jetons restent dans l’état chiffré existant.

Deux tests hors réseau couvrent les quinze destinations, la protection contre
les doublons et l’absence de nouvel envoi après une réponse incertaine.
Les quinze confirmations réelles sont conservées dans publication-results.json.

## Publications

Les 15 publications ont été confirmées le 16 novembre 2026. Le dernier contrôle a abouti à 20 h 38, heure de Paris.

| Compte | Actus · 10 min 07 | Sport · 10 min 05 | Gaming · 10 min 02 |
|---|---|---|---|
| Facebook · VeloceMercato | [Voir](https://www.facebook.com/reel/1094681160197529/) | [Voir](https://www.facebook.com/reel/1470937031839541/) | [Voir](https://www.facebook.com/reel/2184827615762017/) |
| Facebook · VMunivers | [Voir](https://www.facebook.com/reel/1530488685567560/) | [Voir](https://www.facebook.com/reel/1454241309466274/) | [Voir](https://www.facebook.com/reel/4814386852163113/) |
| Facebook · VM actuspronos | [Voir](https://www.facebook.com/reel/1934537214620661/) | [Voir](https://www.facebook.com/reel/2330848407676795/) | [Voir](https://www.facebook.com/reel/2995374254170669/) |
| Instagram · @veloce.mercato | [Voir](https://www.instagram.com/reel/Df0FUL8EpCC/) | [Voir](https://www.instagram.com/reel/Df0GCzIjoqj/) | [Voir](https://www.instagram.com/reel/Df0G9CUD-rw/) |
| Instagram · @vmunivers.fr | [Voir](https://www.instagram.com/reel/Df0FssAnEL6/) | [Voir](https://www.instagram.com/reel/Df0GkSxj4__/) | [Voir](https://www.instagram.com/reel/Df0HV3CCZru/) |

[Exécution de publication réussie](https://github.com/Velocemercato/velocemercato.fr/actions/runs/43937200715) · [Reçus](publication-results.json).
