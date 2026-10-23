# JT : préparer avant l’heure annoncée

## Constat du 23 octobre

Le workflow du matin était programmé à 8 h Paris. GitHub l’a démarré à 8 h 26, puis les vidéos ont été produites successivement. Les fichiers de Foot et Gaming portent respectivement les horodatages 8 h 53 et 9 h 01, correspondant au début de leurs rendus ; ces heures ne sont pas des preuves d’une disponibilité à 8 h. Le rendu Actus a échoué sur la limite CDN, corrigée séparément.

Les MP4 de Foot et Gaming du 23 octobre ont été vérifiés directement : réponse HTTP 200 du CDN, téléchargement complet et décodage ffmpeg sans erreur. Foot : 14 310 318 octets, 276 secondes, H.264 1280 × 720. Gaming : 10 796 604 octets, environ 226 secondes, H.264 1280 × 720. Cette vérification concerne les fichiers sur les sites ; elle ne prouve pas une publication YouTube ou Twitch. `studio/diffusions.json` ne contient aucun accusé public de diffusion à la date du contrôle.

Liens de lecture :

- [Foot, édition du matin du 23 octobre](https://velocemercato.fr/studio/episodes/foot-edition-20261023-0853.html).
- [Gaming, édition du matin du 23 octobre](https://velocemercato.fr/studio/episodes/gaming-edition-20261023-0901.html).

L’accès direct au domaine du site reste filtré dans cet environnement. Les contrôles de présentation utilisent un serveur local et les données du dépôt ; le contrôle des MP4 utilise leurs véritables liens CDN. Une vérification locale du widget confirme que les pages sélectionnent la dernière émission publiée de leur univers.

## Nouveau calendrier

| Édition | Première préparation visée, Paris | Rattrapage visé, Paris |
| --- | --- | --- |
| Matin | 6 h 45 | 8 h |
| Midi | 10 h 45 | 12 h |
| Soir | 18 h 45 | 20 h |

La préparation est avancée de 75 minutes pour laisser du temps au déclenchement GitHub, aux voix, au montage et à l’envoi. Les vidéos sont publiées dès qu’elles sont validées ; aucune attente artificielle sur un runner n’est ajoutée pour atteindre l’heure pile. Une vidéo peut donc être disponible avant l’heure cible.

Les variantes UTC couvrent l’été et l’hiver. Les déclenchements supplémentaires qui trouvent les trois éditions déjà publiées n’installent pas les outils et n’effectuent pas de nouveaux appels de rédaction. Si Actus manque, son rattrapage reste éligible ; les éditions déjà publiées conservent leur protection contre les doublons.

Le filtre qui écartait les départs de 8 h, 12 h ou 20 h après la minute 29 est supprimé. Un départ à 12 h 35 peut désormais produire l’édition du midi au lieu d’être ignoré. Les retards restent bornés à la fenêtre de l’édition pour éviter une production hors de son créneau.

GitHub Actions n’offre pas de ponctualité garantie. Ce calendrier améliore la disponibilité attendue ; il ne constitue pas une garantie contractuelle de diffusion à 8 h, midi et 20 h. La diffusion longue reste soumise aux connexions et autorisations des plateformes, à la présence des originaux et à la validation d’un programme complet.

## Validation

Trois tests supplémentaires vérifient les fenêtres de préparation et de retard, les variantes UTC d’été/hiver, les changements d’heure de mars et octobre, les doublons complets et le rattrapage d’un Actus manquant. Les onze tests existants de production passent également. Les expressions cron du workflow ont été comparées à celles du planificateur. Le test de présentation des dernières émissions par univers passe dans Chromium.

L’avancement est appliqué aux prochains créneaux ; il ne peut pas rendre disponibles à 8 h des vidéos produites plus tard ce matin. Il ne prouve pas non plus qu’une édition du midi a commencé ou a été publiée : l’exécution et les liens du jour doivent être contrôlés séparément.

## Lancement manuel de secours

Si le créneau est en retard, le propriétaire peut ouvrir [le workflow La Pastille TV](https://github.com/Velocemercato/velocemercato.fr/actions/workflows/emissions.yml), choisir **Run workflow**, branche **main**, univers **tous**, format **edition**, moment **midi** (ou le créneau souhaité), qualité **auto** et cocher **Publier après validation**. Cette action produit les éditions manquantes selon les garde-fous existants ; elle ne garantit pas un programme long si les trois originaux ne sont pas disponibles.

Le lancement manuel depuis cet environnement reste indisponible : l’accès à l’API GitHub renvoie Forbidden. Le calendrier est modifiable par Git, et les exécutions publiques peuvent être vérifiées, mais aucun déclenchement manuel réussi n’est annoncé sans réponse positive de GitHub.
