# Connecter YouTube et Twitch depuis votre Z Flip

Le système de publication est installé. Il reste à autoriser vos comptes. Le parcours ci-dessous s’effectue dans **Chrome sur Android**, avec un espace GitHub Codespaces dans le navigateur. Il n’installe pas de programme sur le téléphone et ne publie pas une vidéo à lui seul.

Les retours OAuth ont été testés avec un serveur local et des réponses de contrôle. **Le parcours complet sur un téléphone réel et les comptes Google/Twitch ne sont pas encore validés.** Les plateformes peuvent demander des réglages de compte ou d’application supplémentaires, décrits dans le guide général.

## 1. Ouvrir le dépôt dans Chrome

1. Ouvrir https://github.com/codespaces dans Chrome et utiliser votre compte GitHub.
2. Ouvrir un Codespace existant du dépôt **Velocemercato/velocemercato.fr**, ou en créer un sur la branche **main** : https://codespaces.new/Velocemercato/velocemercato.fr?ref=main. Codespaces utilise votre quota GitHub ; consulter le quota et les conditions affichés avant de créer un espace. Aucun espace payant n’est créé par Codex.
3. Dans Chrome, le menu **⋮ → Version pour ordinateur** peut rendre l’éditeur plus accessible. Ouvrir **Terminal → New Terminal** dans l’éditeur GitHub.
4. L’espace préparé fournit Python et GitHub CLI. Si vous réutilisez un ancien Codespace, vérifier qu’il contient la version actuelle de la branche `main`, sans écraser votre travail local.

## 1 bis. Donner à GitHub CLI le droit d’écrire les secrets

Le jeton automatique d’un Codespace ne peut pas créer les secrets Actions. Dans le terminal :

```sh
unset GITHUB_TOKEN
gh auth login
```

Choisir **GitHub.com → HTTPS → Login with a web browser**, ouvrir le lien et saisir le code affiché. L’outil de connexion vérifie ce droit **avant** d’ouvrir la page Google.

## Accord avant publication

Après connexion, les vidéos sont envoyées sur YouTube en **privé** uniquement (`VM_YOUTUBE_PUBLIC=false`). Vous les regardez dans YouTube Studio et les passez vous-même en public. Pour autoriser plus tard la mise en public automatique : GitHub → Settings → Secrets and variables → Actions → Variables → `VM_YOUTUBE_PUBLIC` = `true`.

## 2. Obtenir l’adresse de retour du téléphone

Dans le terminal du Codespace, coller :

```sh
python tools/connecter_diffusion.py youtube --codespaces --adresse
```

Copier l’adresse HTTPS affichée, qui ressemble à `https://nom-de-votre-espace-8765.app.github.dev/callback`. Ce n’est pas un secret. **Cette adresse propre à votre espace doit être enregistrée dans les applications Google et Twitch**, à la place de `localhost`.

Le port 8765 est préparé dans la configuration du Codespace. Garder le port **privé**. Si GitHub demande de vous connecter lors du retour depuis Google/Twitch, utiliser le même compte GitHub dans Chrome. Ne pas fermer ni supprimer le Codespace avant la fin des deux connexions, car son adresse de retour changerait à la recréation.

## 3. Connecter YouTube

1. Dans un autre onglet Chrome, ouvrir https://console.cloud.google.com/ avec le compte qui gère votre chaîne.
2. Réutiliser votre projet, activer **YouTube Data API v3** et configurer l’application OAuth si ce n’est pas déjà fait.
3. Créer ou réutiliser un client OAuth de type **Application Web** pour ce parcours Codespaces. Ajouter l’adresse HTTPS obtenue à l’étape 2 dans les **URI de redirection autorisés**. Le client « Application pour ordinateur » du guide local est réservé au parcours sur ordinateur avec retour local.
4. Copier son **Client ID** public et lancer dans le terminal :

```sh
python tools/connecter_diffusion.py youtube --codespaces --client-id VOTRE_CLIENT_ID_GOOGLE
```

5. Le terminal demande le secret du client : le saisir seulement dans cette **saisie masquée**, jamais dans une conversation, un fichier du dépôt ou une commande visible.
6. Ouvrir le lien Google affiché dans Chrome, choisir votre chaîne et autoriser les droits demandés. Le retour HTTPS rejoint le programme dans le Codespace.
7. Revenir au terminal : le message doit confirmer le compte et l’enregistrement des accès dans GitHub. Une autorisation seule ne signifie pas qu’une vidéo a déjà été envoyée.

Les restrictions Google restent applicables : autorisation des vidéos longues, durée des autorisations OAuth de test et éventuelle limitation des projets API non audités aux vidéos privées. Le script ne contourne pas ces restrictions et ne présente pas un upload privé comme une publication publique. Voir `YOUTUBE_TWITCH_CONNEXION.md`.

## 4. Connecter Twitch

1. Ouvrir https://dev.twitch.tv/console/apps dans Chrome avec le compte de votre chaîne.
2. Créer ou réutiliser une application disposant d’un Client Secret. Enregistrer **la même adresse HTTPS de retour Codespaces** dans ses redirections OAuth.
3. Copier le Client ID public et lancer :

```sh
python tools/connecter_diffusion.py twitch --codespaces --client-id VOTRE_CLIENT_ID_TWITCH
```

4. Saisir le Client Secret dans la saisie masquée, ouvrir le lien officiel Twitch et autoriser la chaîne.
5. Vérifier la confirmation dans le terminal. Pour conserver des replays Twitch, activer aussi « Stocker les diffusions précédentes » dans les réglages du créateur.

Si GitHub refuse l’écriture des secrets, vérifier les droits du Codespace et de `gh` sur le dépôt. Il ne faut pas copier les jetons OAuth dans une conversation pour résoudre ce problème. Le refus réseau de l’API dans Codex cloud et les droits du compte GitHub sont deux causes distinctes.

## 5. Après les confirmations

Arrêter le Codespace depuis la page GitHub Codespaces une fois les connexions terminées. Le programme quotidien tourne ensuite dans **GitHub Actions**, indépendamment du téléphone et du Codespace. Les éditions sont lancées à 7 h, 12 h et 20 h Paris, puis diffusées après montage ; les spéciales et débats utilisent les matchs confirmés disponibles.

Dans le dépôt, consulter **Actions → VM - YouTube et Twitch automatiques**. Les confirmations attendues sont `youtube : published` et `twitch : ended`. Sans ces confirmations, ne pas considérer une vidéo ou une diffusion comme publiée. Les liens du site ne sont ajoutés qu’après confirmation.
