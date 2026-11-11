# VM Prono — reprise et audit Claude

Date : 11 novembre 2026. Propriétaire : Romain. Autorisation : application de conseils personnels, public libre, VIP gratuit sur invitation. Aucun pronostic inventé.

## Identité et périmètre

- Projet Sites : `appgprj_6af43b400714819195c05ba7377799b6`.
- URL prévue : https://vm-prono-club.heineguez.chatgpt.site (vérifier le résultat du déploiement, pas seulement ce fichier).
- Application indépendante du site VM Auto. Ne pas modifier VM Auto ou sa configuration DNS.
- Le média principal est https://velocemercato.fr, dépôt `Velocemercato/velocemercato.fr`. Le pouf VM Prono doit pointer vers l’application après vérification du déploiement.
- Le code de cette application est synchronisé dans le dépôt source fourni par Sites. L’ID et les migrations doivent être conservés ; ne pas créer un nouveau projet pour une correction.

## Réalisé dans cette version

- Interface mobile BD/manga originale Vélocé, conseils publics, club VIP, suivi des matchs et installation PWA.
- Invitations aléatoires à usage unique, stockage de leur empreinte uniquement, expiration sept jours par défaut ; consommation atomique via transaction D1. Le code sert à activer un compte, pas à limiter la consultation à une fois.
- Mots de passe PBKDF2-SHA256 100 000 itérations, sel individuel et secret serveur. Sessions aléatoires stockées par empreinte, cookie HttpOnly Secure SameSite=Lax, trente jours. Une nouvelle connexion révoque toutes les précédentes.
- VIP filtré côté serveur, réponses privées sans cache, aucun contenu VIP dans le dépôt ou les notifications. Filigrane propre au membre ; aucune prétention de bloquer les captures d’écran.
- Administration propriétaire : identité ChatGPT fournie par l’hébergeur, vérification côté serveur de l’ID de connexion et de l’adresse propriétaire en secret. Le formulaire client n’est jamais la frontière de sécurité.
- Éditeur : brouillon, conseil public/VIP, match et horaire, expiration, sélection, cote facultative, résultat manuel, aperçu et export PNG du conseil en style BD.
- Une analyse longue est tronquée visuellement sur le PNG avec ellipse ; le texte complet reste dans le conseil. Vérification manuelle du visuel avant publication.
- Validation explicite avant publication et envoi Web Push. Les notifications VIP annoncent seulement la disponibilité du conseil.
- Gestion des invitations, révocation membre et sessions, registre d’envois. Un envoi accepté par le service Push ne prouve pas sa réception sur le téléphone.
- Web Push RFC8291 aes128gcm + VAPID ES256. Abonnements par appareil, choix public/VIP/matchs, désabonnement. Endpoints Push limités aux domaines FCM, Mozilla et Apple ; aucune URL arbitraire envoyée par le visiteur n’est appelée.
- Service worker sans cache de pages ou d’API privées.
- Synchronisation du flux `scores.json` existant du média. Aucun score inventé ; données de plus de trente minutes refusées. Appariement par identifiant de match, alerte lors d’un changement réellement observé. Rappel dans les trente minutes avant le coup d’envoi renseigné.
- Déduplication des alertes par opération et abonnement. Les échecs ambigus ne sont pas automatiquement renvoyés afin d’éviter les doubles notifications.

## Données et secrets

D1 binding `DB`. Schéma dans `db/schema.ts`, migration versionnée sous `drizzle/`. Ne pas initialiser de tables à la volée dans une requête.

Variables de production configurées par l’hébergeur, jamais dans Git :

| Nom | Usage |
| --- | --- |
| APP_SECRET | Secret serveur, empreintes et poivre des mots de passe |
| OWNER_EMAIL | Adresse autorisée à administrer |
| VAPID_PRIVATE_JWK | Signature privée Web Push |
| VAPID_PUBLIC_KEY | Clé publique nécessaire aux abonnements navigateur |
| VAPID_SUBJECT | Contact VAPID |

Ne pas copier un jeton Cloudflare ou un secret Facebook dans un dossier d’audit. Les accès de ChatGPT ne sont pas automatiquement transmis à Claude. Claude doit disposer de ses propres connexions autorisées et du dépôt source exact pour modifier ce projet. Un jeton Cloudflare Pages ne donne pas accès à l’hébergement Sites de cette application ni à tous les services.

Le dépôt média existant contient du code ancien qui semble inclure des identifiants de services encodés. L’encodage n’est pas une protection : auditer ce point séparément, migrer vers les secrets des workflows et faire renouveler les identifiants concernés par le propriétaire. Ne pas reproduire leurs valeurs.

## Vérifications effectuées

`node tests/security.mjs` utilise SQLite en mémoire avec adaptateur D1 transactionnel ; cela ne remplace pas un test de concurrence sur le D1 de production.

Cas vérifiés : refus anonyme VIP et administration ; adresse administrateur sans ID refusée ; activation concurrente du même code : un succès ; code réutilisé refusé ; mot de passe avec espaces conservés ; connexion remplaçant la précédente ; contenu VIP absent du JSON public ; origine étrangère refusée ; membre révoqué immédiatement bloqué ; chiffrement Push déchiffrable avec la clé du destinataire ; signature VAPID valide ; endpoint arbitraire refusé.

Compilation TypeScript et build Vinext à réaliser après chaque correction. Ne pas confondre réussite de compilation, déploiement, souscription Push et réception réelle d’une notification.

## Tests de recette restant sur appareils réels

1. Connexion propriétaire via `/admin`, publication d’un brouillon de test, aperçu sur petit écran ; supprimer ou remettre en brouillon après test.
2. Créer un code, activer un membre, réutiliser le code sur un second téléphone ; vérifier le refus. Se reconnecter au même compte sur le second appareil ; vérifier la fermeture de la session précédente.
3. Révoquer le membre ; vérifier le refus d’accès au contenu et l’annulation des prochaines notifications VIP.
4. Android Chrome : installer et autoriser Push ; tester application fermée. iPhone : installer sur l’écran d’accueil depuis Safari et tester les permissions prises en charge. Les permissions du système et la connectivité peuvent empêcher la réception.
5. Vérifier les en-têtes d’identité garantis par Sites en production, l’absence d’usurpation des en-têtes transmis directement par le visiteur, et les limites de débit.
6. Flux de scores actuellement vide/ancien lors de la préparation : vérifier le workflow du média, son authentification fournisseur et la fraîcheur. Ne jamais publier les anciens conseils du 4 novembre comme nouveaux conseils.
7. Suivre un vrai match associé à une publication. Vérifier rappel, premier instantané silencieux, changement de score, correction et déduplication ; le délai dépend du flux et de la cadence du déclencheur.
8. Tester perte réseau pendant publication : conserver le même identifiant d’opération pour une relance de notification incertaine, inspecter l’outbox ; ne pas renvoyer aveuglément les états `sending`/`uncertain`.

## Limites connues et suites utiles

- Pas de blocage des captures d’écran dans la PWA. Filigrane et révocation dissuadent le partage sans le rendre impossible.
- La session peut être copiée sur un appareil compromis : une session active n’est pas une garantie physique d’un appareil unique.
- Pas de réinitialisation autonome de mot de passe ni de récupération par email. Le contact propriétaire est indiqué ; mettre en place un vrai parcours avant un grand lancement.
- L’envoi est traité par lots de 35 par appel ; prévoir des relances périodiques. Traiter avec soin l’état `sending` après interruption et ajouter des délais/reprises idempotentes avant forte audience.
- Nettoyage périodique des anciennes limites/sessions/événements et politique de conservation à compléter ; mécanisme de suppression de données sur demande actuellement via contact.
- Pas de paiement, bookmaker intégré, diffusion de mises ni pronostic automatique.
- Pas de promesse de temps réel : les flux existants et leur couverture font foi.

## Commandes et routes

- Installer/build via les helpers Sites fournis, en conservant `sites()` dans Vite et l’identité du manifeste.
- Tests : `node tests/security.mjs` ; types : `node node_modules/typescript/bin/tsc --noEmit`.
- `/` public et VIP ; `/admin` espace propriétaire.
- `/api/me`, `/api/public`, `/api/vip`, `/api/redeem`, `/api/login`, `/api/logout`.
- `/api/subscribe`, `/api/unsubscribe`, `/api/scores`, `/api/sync`.
- `/api/admin/dashboard`, `/api/admin/invites`, `/api/admin/revoke`, `/api/admin/posts`, `/api/admin/result`, `/api/admin/drain`, `/api/admin/fixtures`.
- `/api/sync` accepte uniquement la lecture du flux fixe et le traitement d’événements connus, sans corps de publication arbitraire. Appel périodique à relier après publication ; l’endpoint ne fournit aucun contenu VIP.

## État du déploiement confirmé

Déployé et rendu public le 11 novembre 2026. Version source : `19edc839f37b21ff8672d22d5faef66ea649a80f`. Le navigateur a affiché l’interface publique, la barrière d’invitation VIP et la connexion propriétaire requise à `/admin`. La recette connectée propriétaire et la réception Push sur un téléphone réel restent à faire.

Le workflow `.github/workflows/vm-prono-sync.yml` traite le suivi et la file d’alertes toutes les cinq minutes selon la disponibilité des exécuteurs GitHub ; ce n’est pas une garantie de temps réel. Il vérifie aussi les refus anonymes VIP/admin.


## Recette serveur en production

Le workflow GitHub `VM Prono — suivi et alertes`, exécution 43003154213 du 11 novembre 2026, a réussi : `/api/public` répond 200 avec uniquement des publications publiques ; `/api/vip` répond 401 sans connexion ; `/api/admin/dashboard` répond 403 sans identité propriétaire ; `/api/sync` répond 200. Résultat de synchronisation : source indisponible, aucun match, aucun envoi ni message en attente. Cela ne prouve pas la réception Push sur téléphone. Le déploiement Cloudflare du média, exécution 43003052097, a réussi avec le nouveau lien du pouf.
