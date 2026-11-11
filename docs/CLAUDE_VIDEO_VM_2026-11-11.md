# Vidéos VM — dossier de production pour Claude

Demande de Romain du 11 novembre 2026. Ce fichier distingue ce qui est en production de ce qui reste à créer. Il complète le dossier général `docs/DOSSIER_CLAUDE_VM_2026-11-11.md`.

## Référence et identité

Romain a joint `14282.mp4` dans sa conversation : 46,58 secondes, 576 × 1024, piste audio présente. La vidéo montre une illustration manga dans une ville nocturne, une tenue sportive, des accents dorés, une lumière rouge et bleue et des mouvements de caméra. Elle contient un marquage tiers. La garder comme référence de direction artistique ; créer les personnages, illustrations, musique et paroles VM, sans recopier le fichier, son watermark ni sa bande-son.

L'identité souhaitée est Véloce Mercato / VM Univers. Utiliser le logo VM fourni par Romain, disponible dans `img/logo-vm-univers-officiel.png`. Palette : noir, rouge, or, touches de vert. Le présentateur est virtuel ; les informations doivent rester factuelles et sourcées.

## Ce qui est préparé automatiquement

`tools/teasers_vm.py` sélectionne une brève récente, sourcée et encore inutilisée par genre : Foot, Actus, Gaming. Il produit un MP4 vertical original, avec illustration VM, voix française Piper et musique VM en fond, contrôle le format et le niveau sonore, puis ajoute l'entrée à `studio/reseaux.json`. Un échec vocal ou audio empêche la publication du fichier. Ce rendu utilise les illustrations du média ; ce n'est pas encore une animation musicale nouvelle au niveau de la référence.

Le workflow `teasers-vm.yml` prépare les trois blocs quotidiens en amont. Les vidéos sont rangées sur la branche technique `reseaux`, avec une URL figée par commit. Le kit visible est `/studio/kit-automatique.html`. Les résultats du dernier rendu sont dans `studio/teasers.json`.

Le nombre de vidéos prêtes se lit dans ces fichiers. Ne pas annoncer neuf nouveaux rendus tant que les neuf fichiers ne sont pas réellement prêts.

## Planning demandé

| Bloc, heure de Paris | Vidéo 1 | Vidéo 2 | Vidéo 3 |
|---|---|---|---|
| Matin | Foot 9 h | Actus 9 h 03 | Gaming 9 h 06 |
| Midi | Foot 12 h | Actus 12 h 03 | Gaming 12 h 06 |
| Soir | Foot 20 h | Actus 20 h 03 | Gaming 20 h 06 |

Objectif : neuf vidéos distinctes par jour. La dixième serait une promotion de la marque, avec son propre montage et sa propre réservation. Elle n'est pas comprise dans les neuf envois automatiques actuels. Ne jamais remplir un créneau en republiant le même JT ou en inventant une information.

La tâche ChatGPT `Automation_b430a95c1db8819180d7d01ca31231ac` est le seul expéditeur automatique TikTok retenu, via Metricool marque `7762102`, compte `@velocemercato`. Elle prépare les blocs à 8 h 30, 11 h 30 et 19 h 30 Paris. Le workflow GitHub TikTok reste un diagnostic privé, sans expédition concurrente.

Avant un envoi : vérifier l'identité, les fichiers, le calendrier, les réservations de `studio/metricool-planning.json` et l'ancien journal `studio/tiktok.json`. Réserver d'abord l'édition et le bloc, puis enregistrer le reçu Metricool. Un statut incertain bloque une nouvelle tentative. Un reçu Metricool confirme la programmation, pas encore la publication TikTok.

## Nouvelle version musicale à réaliser

Le chant demandé n'est pas encore rendu. Préparer une mélodie originale, une interprétation autorisée et un mix adapté aux réseaux. Une voix Piper parlée ne doit pas être présentée comme une chanson. Ne pas imiter la voix d'une personne réelle à partir de la référence.

Paroles originales proposées pour le refrain :

> Véloce Mercato, les nouvelles prennent de l'avance,
> VM Univers, nos projets entrent dans la danse.
> Du sport aux jeux vidéo, l'info fait le tour,
> Véloce Mercato, ton rendez-vous du jour.

Le texte reste une proposition de production. Prévoir une version instrumentale seule et une version chantée. Garde la voix intelligible, les sous-titres lisibles et le nom des sources à l'écran.

## Plan de montage, compatible avec un travail dans CapCut

| Temps indicatif | Image et mouvement | Texte / son |
|---|---|---|
| 0–3 s | Ville manga nocturne, apparition du logo VM | Accroche factuelle courte ; entrée du motif musical |
| 3–12 s | Personnage original VM, léger travelling | Titre et premier fait vérifié, sous-titres |
| 12–24 s | Décor propre au sujet : stade, rédaction ou gaming | Deuxième phrase du résumé ; source identifiable |
| 24–32 s | Changement de plan, rythme plus marqué | Refrain court de marque, distinct du commentaire d'actualité |
| 32–40 s | Logo VM et illustration originale du thème | Lien du site et appel à suivre la page correspondante |

Format de livraison : MP4 H.264, 1080 × 1920, 30 i/s, AAC, sous-titres SRT et miniature JPG. Les durées s'adaptent à la voix ; éviter de couper les phrases. Contrôler le niveau audio avec FFmpeg et écouter un extrait. Les paroles, les droits musicaux et le nom de la page doivent être validés dans le dossier avant diffusion.

Aucun accès CapCut de Claude n'a été vérifié depuis cette conversation. Une connexion à TikTok ne lui donne pas automatiquement un outil de montage CapCut. S'il n'a pas cet outil, utiliser la chaîne de rendu existante ou livrer les pistes et le plan de montage sans prétendre avoir créé un projet CapCut natif.

## Sources techniques primaires

- TikTok, limites et règles Direct Post : https://developers.tiktok.com/docs/en/content-sharing-guidelines
- TikTok, statut des publications : https://developers.tiktok.com/docs/en/content-posting-api-reference-get-video-status
- Les limites varient selon le compte et les clients API. Ne pas promettre un volume illimité ni contourner un refus.
