# Programmes automatiques YouTube et Twitch

**Sur Android/Z Flip : suivre `docs/CONNEXION_ANDROID.md`.** Ce parcours utilise Chrome et un retour HTTPS dans Codespaces ; le client Google doit être de type Application Web. Le parcours ordinateur ci-dessous reste disponible.

La demande du propriétaire autorise la publication automatique des programmes prêts. Le raccordement technique est ajouté sur `codex/youtube-twitch-auto`. **Aucun compte YouTube ou Twitch n’est authentifié dans cet environnement ; aucun upload ni direct réel n’y est déclaré effectué.** Le script `python tools/diffuser_jt.py --check` indique les plateformes effectivement configurées, sans afficher de secret. La configuration Google présente dans l’environnement n’est pas un accès OAuth à une chaîne YouTube et n’est pas utilisée.

## Fonctionnement préparé

Les JT Foot, Actus et Gaming existants sont lancés à **7 h, 12 h et 20 h, Europe/Paris**, avec correction été/hiver. Lorsque les accès d’au moins une plateforme sont prêts, le montage conserve en plus un original **1280 × 720 à 24 images/s** par rubrique. Les textes et synthèses vocales sont réutilisés ; aucun second appel Claude n’est nécessaire pour le programme long. Les réglages existants des petites vidéos du site restent compatibles avec leur CDN.

Les trois originaux du même jour et du même créneau sont assemblés sans nouvelle compression, avec chapitres calculés d’après les durées réelles. La durée dépend des informations disponibles, de l’ordre de 24 à 36 minutes pour trois JT de 8 à 12 minutes. Aucune rubrique manquante n’est remplacée par un ancien journal ou un sujet inventé. Les heures sont des lancements de génération : la disponibilité et la diffusion suivent la fin du montage et les files d’attente GitHub, pas une diffusion garantie à la minute exacte.

- **YouTube** : vérification de la chaîne autorisée, upload avec reprise par morceaux, d’abord privé, attente du traitement, passage en public, puis contrôle de la visibilité. Titre daté, description, liens vers les sources VM et chapitres sont produits depuis les métadonnées du programme. La génération par IA est déclarée dans la description et dans le champ YouTube prévu. Un upload privé ou refusé n’est jamais affiché comme public.
- **Twitch** : vérification du compte et d’un éventuel direct existant, titre indiquant « programme enregistré · IA », puis diffusion du MP4 au rythme réel avec ffmpeg. Un direct déjà en cours est préservé. Le démarrage doit être confirmé par Twitch et le flux doit se terminer correctement. Twitch reçoit une diffusion enregistrée, pas un upload de fichier comme YouTube.
- **Sites** : les liens confirmés apparaissent sur l’accueil football, VM Studio, VM Actus et VM Gaming. VM Univers y renvoie depuis sa carte TV/Radio. Aucun lecteur tiers n’est chargé automatiquement. Le lien Twitch ouvre la chaîne ; il ne promet pas un replay permanent.

Les jetons renouvelés, sessions d’upload et accusés sont chiffrés en AES-GCM sur la branche technique `broadcast-state`. La clé reste dans les secrets GitHub. Rien de lisible n’est ajouté au site public ; les liens vers des vidéos privées restent dans l’état chiffré. Ne jamais supprimer cette branche ou remplacer sa clé pour résoudre un échec : cela ferait perdre la reprise et la protection contre les doublons.

## Connexion initiale sur votre ordinateur

Cette étape demande votre autorisation dans les pages officielles Google et Twitch. Elle ne peut pas être remplacée par une conversation IA. Le retour OAuth utilise `localhost` : lancer l’outil sur **l’ordinateur qui ouvre le navigateur**, pas dans Codex cloud avec un navigateur sur un autre appareil. Il faut Python 3 et le client GitHub `gh` connecté au dépôt avec les droits de gérer ses secrets et variables. Aucun paquet Python supplémentaire n’est nécessaire pour l’outil de connexion.

Si `gh` n’est pas déjà connecté sur cet ordinateur, utiliser son parcours officiel `gh auth login`. Un refus réseau de l’API dans Codex cloud ne signifie pas qu’un nouveau jeton GitHub est nécessaire. Les secrets sont transmis à `gh secret set` par l’entrée standard : ils ne sont ni affichés, ni placés dans une commande shell, ni enregistrés dans le dépôt.

### YouTube

1. Dans https://console.cloud.google.com/, utiliser un projet qui vous appartient, activer **YouTube Data API v3**, puis configurer l’écran d’autorisation OAuth. Créer un client OAuth **Application pour ordinateur** et télécharger son JSON **hors du dépôt**.
2. Pour une utilisation quotidienne, vérifier la configuration de publication de l’application OAuth. En mode test externe, Google peut faire expirer les autorisations de ce type au bout de sept jours : ce mode ne convient pas à une promesse d’automatisation permanente.
3. Depuis votre copie du dépôt, lancer :

```sh
python tools/connecter_diffusion.py youtube --client-json /chemin/prive/client-google.json
```

4. Dans la page Google qui s’ouvre, choisir **votre chaîne** et autoriser l’envoi des vidéos et la lecture de ses informations. L’outil vérifie la chaîne sélectionnée, enregistre les secrets nécessaires dans GitHub et active seulement ensuite `VM_AUTO_YOUTUBE=true`.

L’outil utilise `youtube.upload`, `youtube.readonly` et `youtube.force-ssl`.
Le dernier droit est nécessaire à `videos.update`, utilisé pour rendre publique
la vidéo après son traitement. Un ancien jeton limité aux deux premiers droits
doit être reconnecté une fois ; ajouter le droit dans le code ne modifie pas les
autorisations d’un jeton existant. Référence : https://developers.google.com/youtube/v3/docs/videos/update.

La chaîne doit accepter les vidéos longues. Les projets API YouTube non audités peuvent être limités aux vidéos privées par YouTube ; mettre l’application OAuth en production et obtenir l’autorisation API d’envois publics sont deux sujets distincts. Si YouTube refuse le passage public, la vidéo reste privée et le workflow signale l’échec ; ne pas annoncer un succès public ni réencoder une autre copie pour contourner le refus. Référence : https://developers.google.com/youtube/v3/docs/videos/insert.

### Twitch

1. Dans https://dev.twitch.tv/console/apps, créer ou réutiliser votre application, avec l’adresse de retour exacte **http://localhost:8765/callback**.
2. Récupérer son **Client ID** et disposer de son **Client Secret**. Ne jamais les coller dans une conversation. Lancer :

```sh
python tools/connecter_diffusion.py twitch --client-id VOTRE_CLIENT_ID_PUBLIC
```

3. Saisir le secret de l’application dans le terminal lorsque la saisie masquée le demande, puis autoriser votre chaîne dans Twitch. Les droits demandés sont `channel:manage:broadcast` et `channel:read:stream_key`.
4. L’outil vérifie l’identité connectée, enregistre les secrets dans GitHub et active seulement ensuite `VM_AUTO_TWITCH=true`. La clé de diffusion est récupérée au moment de chaque émission, sans être copiée dans le dépôt ou les logs.
5. Si vous voulez aussi des replays Twitch, activer **Stocker les diffusions précédentes** dans les réglages du créateur. La conservation et la disponibilité dépendent de Twitch ; les replays longs durables sont prévus sur YouTube.

Le flux utilise l’ingestion Twitch officielle `rtmp://live.twitch.tv/app/` et le protocole RTMP attendu par ce service. Les autorisations et appels d’API passent par HTTPS. La destination contenant la clé n’est jamais imprimée, y compris en cas d’erreur ffmpeg. La catégorie choisie est « Just Chatting », adaptée à ce programme d’actualité mixte.

## Après la connexion

Le prochain lancement complet de **VM Studio - La Pastille TV** crée l’artefact `pastille-masters`, conservé deux jours. Le workflow **VM - YouTube et Twitch automatiques** récupère uniquement cet artefact depuis le lancement de production qui l’a déclenché. Les aperçus, branches de travail et lots incomplets ne déclenchent pas ces programmes longs. Les spéciales avant-match et débats validés sont diffusés séparément avec leur propre original HD ; les données structurées de matchs couvrent actuellement Ligue 1 et Ligue des champions. Les pages Actus/Gaming ne les présentent pas comme leurs journaux. Une rubrique déjà publiée plus tôt n’est pas artificiellement régénérée : après une activation tardive, attendre le prochain créneau complet.

Les variables et secrets sont créés par l’outil. Pour vérification, leurs noms sont :

| Plateforme | Secrets | Variable d’activation |
| --- | --- | --- |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CHANNEL_ID` | `VM_AUTO_YOUTUBE=true` |
| Twitch | `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `TWITCH_REFRESH_TOKEN`, `TWITCH_BROADCASTER_ID` | `VM_AUTO_TWITCH=true` |
| État chiffré commun | `VM_DIFFUSION_STATE_KEY` | aucune |

Une plateforme peut fonctionner indépendamment de l’autre. Pour la suspendre, passer sa variable à `false`. Ne pas supprimer sa clé de chiffrement ni ses accusés. Le renouvellement des jetons Twitch est conservé chiffré, car un nouveau refresh token peut être retourné par le service.

## Vérifier ou reprendre un échec

Dans **Actions**, consulter les deux workflows. Une génération réussie n’est pas une confirmation de diffusion. Les lignes finales doivent indiquer `youtube : published` ou `twitch : ended`, et les liens du site n’apparaissent qu’après cette confirmation. Vérifier ensuite la vidéo réelle et son affichage HD sur YouTube ainsi que la chaîne Twitch.

Une session YouTube interrompue est reprise depuis les octets confirmés par l’API, sans nouvel upload du même programme. Une vidéo encore en traitement reste privée ; un nouveau lancement du workflow de diffusion peut reprendre cette session tant que ses originaux frais sont encore acceptés. Les programmes anciens de plus de trois heures sont refusés pour éviter de présenter un vieux journal comme une émission actuelle.

Un état Twitch `starting` ou `live` après une interruption exige une vérification du canal avant toute remise en file ; le script ne redémarre pas aveuglément un direct ambigu. `skipped_live` signifie qu’un direct existant a été préservé. Les erreurs ne doivent pas être « corrigées » en effaçant les accusés ou en publiant des secrets dans les logs.

## Validation disponible

Les 38 méthodes locales réussies couvrent notamment le chiffrement, le retour OAuth réel sur boucle locale avec PKCE Google, le stockage sécurisé via `gh`, les reprises YouTube (réponses API de contrôle), la confirmation publique, les restrictions de compte, le renouvellement des jetons, les gardes Twitch et l’assemblage ffmpeg réel. Les tests navigateur vérifient les liens publics et l’absence de liens privés. **Ces tests ne valident pas des comptes connectés, un upload réel, une ingestion Twitch réelle, les droits Google de publication publique ou l’écoute d’un nouveau modèle vocal.** Ces contrôles nécessitent le raccordement décrit ci-dessus.

Sources techniques : https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol ; https://dev.twitch.tv/docs/authentication/refresh-tokens/ ; https://dev.twitch.tv/docs/api/reference/#get-stream-key ; configuration des ingestions utilisée par OBS : https://github.com/obsproject/obs-studio/blob/master/plugins/rtmp-services/data/services.json. Les pages Google/Twitch sont bloquées par le proxy de cet environnement ; la configuration OBS publique a été lue.
