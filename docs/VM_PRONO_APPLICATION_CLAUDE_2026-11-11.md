# VM Prono — application et passation à Claude
Date : 11 novembre 2026. Projet demandé par Romain dans cette conversation. Ce document est une spécification ; il ne signifie pas que l’authentification, les invitations ou les notifications distantes sont déjà déployées.

## Décision produit
Une application web installable VM Prono, liée à velocemercato.fr. Le pouf « Conseils pronos » du bureau doit ouvrir l’application, avec deux entrées : conseils publics sans code et VIP gratuit. Telegram devient facultatif ; aucune migration ni suppression de groupe n’est demandée.

Romain conserve le contrôle éditorial : il saisit ses propres conseils depuis son téléphone et valide chaque publication. L’outil prépare un visuel VM à partir de son texte ; il ne crée ni ne publie spontanément des pronostics.

## Parcours public
- Consulter les conseils publics et leurs dates, matchs et résultats vérifiés.
- Installer VM Prono sur son téléphone et choisir ses notifications.
- Ouvrir la carte d’un match suivi.
- Voir un accès VIP sans recevoir les contenus VIP dans le HTML ou les JSON publics.
- Afficher un état vide si aucun conseil validé n’est disponible. Aucune prédiction de démonstration présentée comme réelle.

## VIP : une invitation, un membre
Un code individuel sert UNE FOIS à activer un compte. Il n’est pas le mot de passe commun d’une page.
- Générer un jeton aléatoire fort, conserver uniquement son condensat, fixer expiration et possibilité de révocation.
- Consommer l’invitation par opération atomique en base, avec une contrainte empêchant deux activations concurrentes.
- Lier l’activation à un membre ; proposer une connexion durable et révocable. Romain veut éviter la redistribution : prévoir une session/appareil actif par membre et une procédure de remplacement du téléphone.
- Un lien copié ne donne aucun accès sans session autorisée. Contrôler côté serveur chaque page, fichier, image et API VIP.
- Cookies Secure, HttpOnly, SameSite ; contrôle d’origine/CSRF ; limitation des tentatives ; journalisation sans jeton ni conseil privé.
- Ne pas utiliser localStorage ou un mot de passe JavaScript comme barrière de confidentialité.
- Ne pas promettre l’impossibilité des captures d’écran, de la copie manuelle ou d’un partage du compte/appareil. Le code à usage unique empêche sa réutilisation, pas toutes les formes de redistribution.

La solution d’identité (lien de connexion par e-mail, passkey ou autre) reste à choisir selon les services effectivement disponibles. Aucun fournisseur mail/OTP ni appareil membre n’a encore été connecté dans cette intervention.

## Tableau de bord de Romain
Accès administrateur distinct, côté serveur ; aucun secret dans les dépôts publics.
1. Nouveau conseil.
2. Choisir le match exact dans la source de calendrier, ou saisir un match manuel clairement sans suivi automatique tant qu’il n’a pas été rapproché.
3. Texte, sélection et cote facultative ; visibilité Public / VIP ; heure de publication.
4. Aperçu du visuel manga VM et du texte.
5. Bouton « Publier et prévenir les abonnés ».
6. Reçu de publication et bilan des notifications réellement envoyées.
7. Corriger/retirer un conseil, archiver, gérer membres et invitations.
8. Message en direct/actualisation dans l’application, sans vidéo ou chat public obligatoire au lancement.

Générer les cartes à partir d’un gabarit contrôlé (Canvas/SVG rendu côté serveur), avec informations exactes fournies par Romain. Une image générative ne doit pas décider ou modifier une sélection ou une cote.

## Notifications
Un vrai serveur Web Push avec clés VAPID, abonnements enregistrés et file d’envoi est nécessaire.
- Consentement explicite ; choix public/VIP et matchs suivis ; désinscription.
- Après publication enregistrée, créer un événement unique et dédupliqué. Réessais bornés, reçus ; ne pas annoncer « tout le monde notifié » sans preuve.
- Le push VIP annonce qu’un conseil est disponible et renvoie vers la page protégée ; pas de sélection privée dans le texte visible sur l’écran verrouillé.
- Invalider les abonnements expirés, gérer les erreurs et les préférences.
- Sur iPhone/iPad, l’installation sur l’écran d’accueil est nécessaire au Web Push compatible, puis l’autorisation se demande après un geste de l’utilisateur.
- La livraison dépend des autorisations et réglages du téléphone ; pas de garantie de réception instantanée.

Sources officielles :
https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers
https://webkit.org/blog/13878/

## Matchs suivis
Une source de données sportives avec droit d’usage, clé et quota vérifiés est nécessaire. Prévoir le lien conseil → identifiant immuable de match.
- Choix d’alertes : rappel avant match, coup d’envoi, score, mi-temps, résultat final.
- N’envoyer que les événements pertinents aux abonnés concernés ; gérer reports, annulations, corrections VAR et doublons.
- Une synchronisation serveur continue est nécessaire pour notifier application fermée. Éviter une simple minuterie dans la page du navigateur.
- Tous les championnats ne fournissent pas les mêmes événements ; un retard du fournisseur est possible. Ne pas promettre du zéro délai.
- Le statut gagné/perdu/en attente est distinct du score et des règles du pari. Validation manuelle par Romain au lancement ; ne pas déduire automatiquement un règlement sans marché et règles fiables.
- Le multisport demandera des sources adaptées supplémentaires.

Repère fournisseur, pas une connexion établie :
https://www.api-football.com/documentation-v3
Les clés, quotas, droits et coût éventuel ne sont pas vérifiés ici. Ne pas engager un abonnement payant sans budget autorisé.

## Existant contrôlé dans GitHub
Dépôt : Velocemercato/velocemercato.fr, branche main.
- pronos/index.html et pronos/acces.json existent.
- pronos/acces.json décrit aujourd’hui un VIP gratuit demandé par e-mail, pas un compte activé par invitation.
- pronos/selection.json contient une sélection expirant le 5 novembre 2026. Ne pas la représenter comme un conseil actuel.
- La note de selection.json interdit les contenus VIP dans ce dépôt public : conserver cette protection.
- notifications/alertes.js vérifie les mises à jour pendant la visite. Son message indique expressément « Pas encore de push lorsque le navigateur est fermé ».
- notifications/sw.js ne reçoit pas encore de push distant : notifications locales uniquement.
- Le pouf pointait vers https://t.me/VMCONSEILSPRONOS ; changer sa destination seulement quand l’application cible est vérifiée et utilisable.

## Architecture à valider avant production
- Interface mobile installable, manifeste et service worker.
- API protégée et base privée durable : membres, invitations, sessions, conseils, publications, abonnements, événements et reçus.
- Protection atomique des invitations ; stockage privé des visuels VIP.
- Gestion serveur des publications et de la distribution.
- Source sportive et ordonnanceur serveur/webhook selon les capacités réelles.
- Hébergement sur l’infrastructure disponible, sans supposer que les secrets Pages Cloudflare donnent des droits Workers/D1/DNS.
- Si un sous-domaine séparé est nécessaire, le préparer puis le faire valider avant de modifier le pouf. Un chemin /pronos/ doit conserver les routes existantes ou des redirections explicites.

## Répartition ChatGPT / Claude
Les deux assistants peuvent développer, relire et tester le même dépôt, avec petites modifications et contrôle du HEAD. Les accès de l’un ne se transmettent pas à l’autre.
- Claude : implémentation ciblée API/base/invitations et tests de concurrence si ses outils le permettent.
- ChatGPT : intégration du bureau, parcours mobile, gabarits et vérification de publication ; répartition ajustable.
- Romain : conseils, audience Public/VIP, validation de publication et liste des membres.
Cette répartition est proposée ; aucun message ni tâche n’a été envoyé à Claude automatiquement.

Avant de commencer : lire ce document et docs/DOSSIER_CLAUDE_VM_2026-11-11.md ; observer main ; conserver l’accueil validé et les autres changements ; ne pas faire de force-push. Choisir un seul responsable de déploiement et un seul expéditeur par événement, pour éviter les doubles notifications.

## Critères d’acceptation
1. Un visiteur anonyme voit le public et aucun contenu VIP.
2. Deux requêtes simultanées sur le même code ne créent qu’une activation.
3. Le même code échoue ensuite ; révocation effective côté serveur.
4. Un lien/image VIP copié reste protégé sans session.
5. Publier le même événement deux fois ne double ni le conseil ni les notifications.
6. Une session expirée ou révoquée n’accède plus aux données.
7. Les notifications sont vérifiées sur de vrais appareils consentants, application fermée ; iPhone et Android selon équipements disponibles.
8. Un match reporté, un score corrigé et une absence de couverture sont correctement affichés.
9. Aucune vieille sélection n’est montrée comme nouvelle.
10. L’interface distingue brouillon, publié, envoyé, erreur et en attente. Aucun statut fictif.
