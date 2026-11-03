# Campagne quotidienne VÉLOCE TEAM — mode d'emploi

Chaque jour vers **17 h 41** (heure de Paris), le robot `VM - Campagne quotidienne VÉLOCE TEAM` publie le jour prévu dans
[`calendrier.json`](calendrier.json) sur **Facebook et Instagram** de **Véloce Mercato** et **VM Univers** :

- jour avec `"reel": true` : vidéo Facebook + Reel Instagram + story Instagram ;
- sinon : photo Facebook + photo Instagram + story Instagram ;
- `"youtube_short": true` (le dimanche seulement, jour sans Short de JT) : Short YouTube public.

La page RQ Pronos n'est jamais utilisée. Un jour déjà publié ne l'est **jamais** une seconde fois.
Les liens publics obtenus s'ajoutent à [`journal.json`](journal.json).

## Corriger (sur GitHub, depuis le téléphone ou l'ordinateur)

1. Ouvre `campagnes/calendrier.json` puis le crayon ✏️ « Edit ».
2. Change ce que tu veux **avant 17 h 40** le jour concerné :
   - le texte d'un jour : champ `"texte"` (garde les `\n` pour les retours à la ligne) ;
   - sauter un jour : `"statut": "pause"` ;
   - **tout arrêter** : `"actif": false` en haut du fichier.
3. « Commit changes ».

Un texte modifié change la légende, pas l'image. Pour changer l'image (titre, points, illustration),
dis-le à Claude ou ChatGPT : ils régénèrent les visuels avec `python tools/campagne_quotidienne.py --visuels`.

## Préparer les jours suivants

Ajouter de nouveaux jours à la fin de `"jours"` (même format), puis générer leurs visuels avec la commande ci-dessus.
Sans jour prévu, le robot ne publie rien et le signale dans GitHub Actions.

## TikTok

Pas de connexion automatique TikTok dans le projet : les vidéos verticales des jours « reel »
(`assets/social/campagne/AAAA-MM-JJ-reel.mp4`) et leur texte sont prêts à publier à la main dans l'appli TikTok.
