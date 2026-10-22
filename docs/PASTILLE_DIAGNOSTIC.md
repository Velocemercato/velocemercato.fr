# La Pastille : image, rythme, partage et programmes longs

Préparation initiale sur `codex/pastille-video-voix`, puis intégration sur `codex/publication-validee` après la demande explicite « publie tout ce que tu peux déjà ». Aucun upload YouTube ni direct Twitch n’a été exécuté ici. Le profil de production reste compatible avec le transport existant ; le profil HD est réservé aux aperçus.

## Constats vérifiés

Un exemplaire réel du journal Foot du 22 octobre 2026 à 13 h 09 a été téléchargé depuis son URL publique jsDelivr et analysé avec ffprobe : 1280 × 720, H.264 à 12 images/s, environ 62 kbit/s pour l’image et 60 kbit/s pour l’audio mono à 22 050 Hz. Le fichier fait 6 900 755 octets pour 440 secondes. L’encodeur utilisait CRF 31. Ce réglage économise beaucoup de place au prix des détails ; une nouvelle compression sociale peut accentuer les défauts. Les plateformes sociales elles-mêmes n’ont pas été testées avec un compte connecté.

Le serveur répond HTTP 206 aux requêtes partielles et fournit le bon type `video/mp4`. Le fichier possède déjà `faststart`. Aucun défaut de prise en charge des portions n’a donc été établi sur cet exemplaire.

Le partage générique supprimait le fragment `#tv=...`, ce qui perdait l’émission sélectionnée. Les robots sociaux reçoivent une page générale et ignorent habituellement les fragments. La miniature existante était souvent en 640 × 360. Les vidéos étaient aussi reliées au SHA de la dernière publication, tandis que l’historique de la branche média était réécrit : des liens partagés longtemps auparavant pouvaient dépendre de commits devenus inaccessibles.

Les horaires GitHub étaient exprimés en UTC avec des commentaires ne couvrant pas correctement été/hiver. Gaming ne figurait pas dans les programmes du matin et du midi. Les pages Actus et Gaming annonçaient encore des émissions « en préparation » malgré la présence de journaux publiés.

## Corrections préparées

- Deux profils explicites : en production, le profil CDN conserve 12 images/s, CRF 31 et AAC 56 kbit/s ; les aperçus HD utilisent 24 images/s, CRF 22 et AAC 96 kbit/s. L’audio est traité à 48 kHz, la musique est abaissée et `faststart` est conservé. `VM_VIDEO_PROFILE=auto` choisit CDN en production et HD en aperçu. HD avec publication CDN est refusé avant tout appel de rédaction. Les dessins, portraits et polices existants restent les sources du montage. La netteté des anciennes vidéos n’est pas rétablie par le nouveau lecteur.
- Narration Piper accélérée de 12 %, pauses réduites, prononciation de quelques sigles facilitée. Introduction visuelle de 0,8 seconde, conclusion de 5 secondes conservée et consigne d’entrée immédiate dans les actualités. Le rythme est réglable par `VM_SPEECH_RATE`.
- Les distributions vocales historiques sont conservées sur la branche de publication ; les changements de timbre préparés dans la branche initiale restent à auditionner. Piper 1.8.0 est installé explicitement dans le workflow. Un échec Piper arrête la production ; le repli eSpeak est réservé à un aperçu local explicitement demandé et ne peut pas être publié par le parcours émissions.
- Paroles normalisées et musique de fond plus discrète. Les nouveaux fichiers radio utilisent une piste M4A dédiée quand elle est disponible.
- Pages HTML statiques permanentes pour les émissions existantes (14 au moment de l’intégration), avec titre, image et métadonnées de partage propres à l’épisode, accessibles sans JavaScript. Les affiches sont servies depuis le site. Une affiche a été extraite en 720p de la vidéo Foot effectivement analysée ; les autres affiches historiques conservent leur définition d’origine. Les futures affiches sont produites en 1280 × 720.
- Le lecteur garde l’émission sélectionnée, propose des vitesses, signale les erreurs et n’interrompt pas une lecture en réaffectant la même source. Les anciens liens avec fragment restent compris. Les anciens épisodes ont une lecture initiale à 1,15× ; les nouveaux rendus déjà accélérés commencent à 1×, sauf préférence du visiteur.
- Le partage ouvre l’adresse permanente de l’épisode. La vidéo d’accueil attend d’approcher de la zone visible avant de charger son média. Les compteurs publics de vues du lecteur ont été retirés.
- Le transport GitHub existant ne force plus la réécriture de sa branche. Les liens déjà enregistrés ne sont pas réattribués au nouveau SHA. Les anciens partages cassés ne sont pas réparés rétroactivement : le nouveau lien permanent doit être partagé après publication autorisée.

## Journaux et couverture

Les lancements prévus sont 7 h, 12 h et 20 h, **Europe/Paris**, pour Foot, Actus et Gaming. Le filtre d’horaire couvre les changements d’heure. Le temps de génération et les files d’attente GitHub peuvent retarder la disponibilité : ce ne sont pas des garanties de diffusion à la seconde.

Une spéciale est déclenchée uniquement avec un match à venir confirmé dans des données récentes ; un débat à 23 h 30 exige un résultat final confirmé du jour. Les données de scores actuelles couvrent **Ligue 1 et Ligue des champions**. Cette branche ne prétend pas couvrir automatiquement tous les matchs de Ligue Europa, National ou d’autres compétitions : une source fiable couvrant ces compétitions reste à choisir et valider.

Les JT utilisent les vraies brèves disponibles, avec leurs dates. Les actualités futures sont exclues ; le repli de fraîcheur est limité à 24 heures. Une insuffisance de sources est signalée. Les échecs d’un des univers font échouer le passage plutôt que d’annoncer une réussite globale. Les productions déjà publiées pour le même créneau et la même date ne sont pas dupliquées.

L’accueil Foot, VM Actus, VM Gaming et la page Belfort proposent le dernier JT disponible de leur rubrique. Belfort renvoie au **JT général VM Actus**, sans le présenter comme un journal local. VM Univers conserve son lien vers TV/Radio et son identité de portail.

## Longs programmes YouTube et Twitch

Le choix du propriétaire est YouTube **et** Twitch. Le mode aperçu `univers=tous`, format `edition`, génère les trois rubriques puis les assemble sans réencoder en un programme long, avec un fichier de chapitres et une description datée. L’assemblage exige les trois JT du même jour et du même créneau, ainsi que des formats compatibles. Il ne remplit pas une rubrique manquante avec de faux sujets ou un vieux journal.

La cible proposée est un programme matinal, un programme du midi et un programme du soir : chaque programme regroupe les journaux Foot, Actus et Gaming. La durée dépend des sources et des voix ; les formats unitaires actuels visent environ 8 à 12 minutes, soit de l’ordre de 24 à 36 minutes pour les trois rubriques, sans remplissage artificiel. YouTube convient aux replays longs ; Twitch convient à leur diffusion programmée, annoncée comme un programme enregistré et généré par IA.

**La connexion et l’automatisation YouTube/Twitch ne sont pas implémentées ni activées par cette branche.** Les comptes ne sont pas connectés à cet environnement et aucune capacité de ces services n’y est disponible. Les fichiers et chapitres sont préparés pour l’étape d’intégration, qui doit suivre une authentification autorisée et un essai privé. La chaîne YouTube et le canal Twitch déjà référencés sur les sites peuvent être réutilisés ; aucun nouveau compte n’est créé.

La qualité HD des longs programmes ne doit pas être réinjectée dans le transport GitHub/jsDelivr limité à 20 Mo par fichier et 150 Mo par paquet. Des contrôles arrêtent ce parcours avant un envoi dépassant ces limites. Les rendus longs restent récupérables en aperçu. **Le transport HD des longs JT reste à intégrer et valider. Il n’est pas activé en production.** La conservation de l’instantané CDN est limitée à 24 vidéos et à moins de 150 Mo : seuls les médias les plus anciens quittent le dernier instantané, tandis que leurs versions restent dans l’historique Git pour leurs liens immuables. L’historique Git grossit ; ce transport reste provisoire.

Pour un rendu local déjà généré :

```sh
python tools/assembler_jt.py --moment soir
```

Un aperçu complet GitHub Actions peut être demandé, avec l’autorisation d’exécuter la génération et d’utiliser les services déjà configurés :

```sh
gh workflow run emissions.yml --repo Velocemercato/velocemercato.fr --ref codex/pastille-video-voix -f univers=tous -f format=edition -f moment=soir -f publish=false
```

Cette commande n’a pas été exécutée ici. Les aperçus se trouvent dans l’artefact `pastille-apercus`. Le mode manuel ne publie rien par défaut ; la sauvegarde de production exige `main` et le drapeau de publication explicite.

## Validation et limites

Les commandes sont `python3 tests/test_pastille.py`, `python3 tests/test_pastille_browser.py` et `python3 tests/test_site.py`.

Les tests exercent un encodage et un décodage ffmpeg réels, le codec, les dimensions, les proportions, les durées audio/vidéo, le démarrage progressif, l’introduction raccourcie, la piste radio, la concaténation des trois rubriques, la fraîcheur des données, l’heure de Paris, les protections de publication, les métadonnées sociales et la stabilité des liens. Les tests navigateur utilisent un vrai MP4 H.264 de contrôle et des requêtes partielles simulées localement pour vérifier la lecture, les erreurs, le partage, les vitesses et les widgets à 390 et 1440 px. Les tests du site couvrent aussi 320 et 768 px, les thèmes et le mode hors connexion.

Un extrait local de 17,92 secondes a aussi été rendu avec la **voix d’un enregistrement existant, accélérée**, pour auditionner le rythme et vérifier l’encodage. Il ne constitue pas une synthèse vocale avec les nouveaux profils Piper ni un nouveau journal. Il a été décodé sans erreur.

Piper 1.8.0 et son interface en ligne de commande fonctionnent dans un environnement virtuel de test. Le téléchargement des modèles depuis `huggingface.co` est refusé ici (HTTP 403 du proxy). La naturalité des nouveaux profils reste donc à écouter et valider. La clé de rédaction n’est pas injectée dans cette machine ; les logs montrent qu’elle a déjà été utilisée dans GitHub Actions, où il faut vérifier les bindings existants avant d’en demander une autre.

L’API GitHub ainsi que les deux domaines publics restent bloqués depuis cet environnement. Git et le CDN vidéo fonctionnent. Les PR ne peuvent donc pas être ouvertes automatiquement, les réglages publics ne sont pas contrôlés, et aucun test dans les applications Facebook, Instagram, WhatsApp ou Twitch/YouTube connectées n’est déclaré réalisé.

Référence des limites CDN : https://github.com/jsdelivr/jsdelivr#limitations

Le propriétaire a ensuite autorisé la publication des éléments validés. Voir `docs/PUBLICATION_ET_RESEAUX.md` pour la portée livrée, les capacités réellement disponibles et les étapes restantes. Cette autorisation ne constitue pas une preuve de livraison sur un compte non connecté.
