# Publication et assistants de communication

Le propriétaire a explicitement demandé le 22 octobre 2026 de publier les éléments prêts. L’intégration sur `codex/publication-validee` conserve les actualités et scores ajoutés automatiquement depuis les branches de revue. Les branches initiales restent disponibles pour examiner les changements. L’API GitHub est refusée par le proxy de cet environnement ; les PR et le suivi des déploiements ne peuvent pas y être pilotés par API. Le push Git est disponible. Un push réussi sur `main` ne prouve pas à lui seul la fin du déploiement GitHub Pages.

## Ce qui est raccordé

Les robots existants continuent à produire les brèves Foot, Actus et Gaming et le quiz. Le portail VM Univers garde son domaine et ses cartes de projets ; Véloce Mercato garde ses créations football. Aucun visuel original n’est remplacé. Les compteurs d’audience publics sont retirés ; le choix et l’ouverture d’un compte de statistiques privé restent à effectuer.

La génération des JT est programmée à 7 h, 12 h et 20 h **Europe/Paris** pour les trois rubriques. Ce sont des heures de lancement, avec des retards possibles liés à GitHub et à la génération. Les données de matchs actuellement intégrées couvrent Ligue 1 et Ligue des champions. Les spéciales et débats ne sont déclenchés qu’avec les données confirmées et récentes disponibles.

Les prochains rendus utilisent une narration 12 % plus rapide, moins de pauses et une introduction visuelle de 0,8 seconde. La conclusion est conservée. Les timbres historiques restent en place ; le téléchargement des modèles Piper est bloqué dans cet environnement, donc l’écoute d’un nouvel extrait Piper reste à vérifier dans GitHub Actions. Un échec vocal n’est plus remplacé silencieusement par eSpeak en production.

Les anciennes vidéos peuvent être lues à 1,15× et partagées avec leur page d’épisode. Les anciennes images compressées restent compressées. Le profil CDN conserve les réglages vidéo existants ; le rendu HD à 24 images/s est réservé aux aperçus et aux futurs envois vers un hébergement long. Les fichiers trop gros ne sont pas envoyés au CDN. Les anciens posts sociaux nécessitent un nouveau partage pour bénéficier du nouveau lien ; leur cache n’est pas effacé par une modification du site.

## Communication automatique

`tools/social_publications.py` prépare deux sélections distinctes :

- **Véloce Mercato** : une brève football récente avec attribution et lien permanent, un JT réellement publié lorsqu’il existe, et le quiz du jour.
- **VM Univers** : les dernières brèves disponibles de VM Actus et VM Gaming avec leurs liens, un JT publié de ces rubriques et un lien vers le portail.

Les contenus doivent dater de moins de 24 heures ; les contenus futurs, sans source ou les brouillons vidéo sont exclus. Un même contenu confirmé envoyé n’est pas réutilisé au créneau suivant. Aucun texte d’actualité, score, résultat ou chiffre d’audience n’est créé par ce script. Les titres reprennent les brèves existantes : cela ne constitue pas une nouvelle vérification indépendante de leurs sources.

Le workflow `communication.yml` prévoit **7 h 15, 12 h 15 et 20 h 15 Paris**. Il prépare aussi une sélection dès la publication de cette intégration. Un JT encore en montage peut être repris au passage suivant. Les créneaux sociaux partagent des liens ; ils ne constituent ni un upload natif de vidéo ni un direct.

Le seul envoi implémenté est **Discord**, vers le salon correspondant au secret `DISCORD_WEBHOOK`, déjà référencé par le workflow de scores. Aucune valeur secrète n’est recopiée depuis un autre script. Si ce secret n’est pas disponible, les exports sont conservés et le résultat indique `non_connecte`, avec zéro envoi. La présence du nom dans le code ne prouve pas que le secret existe dans les réglages du dépôt.

L’intention d’envoi est enregistrée avant le contact Discord et l’identifiant du message est conservé après sa confirmation. L’état est sur la branche technique `social-state`, hors du site mais lisible comme le dépôt public. Il contient uniquement les identifiants des contenus/messages et des états techniques, sans webhook ni statistiques de visiteurs. En cas de timeout ou d’arrêt après envoi, l’état reste `uncertain` ou `sending` : vérifier le salon avant toute remise en file. Cela évite les doublons automatiques au prix d’une intervention pour les livraisons ambiguës. Les mentions de masse sont désactivées.

Les exports `publications.txt`, `publications.json` et les résultats disponibles se trouvent dans l’artefact GitHub Actions **vm-communication**, conservé 14 jours. L’accès à cet artefact suit les permissions GitHub du dépôt ; il ne doit contenir aucun secret. Le résultat réel doit être lu dans l’artefact et dans le salon ; aucun envoi connecté n’a été exécuté depuis cette machine.

## Comptes encore à connecter

**YouTube et Twitch** sont les destinations choisies pour les programmes longs. Le générateur et `tools/assembler_jt.py` préparent un MP4 long et ses chapitres, mais aucun upload YouTube ni direct Twitch n’est implémenté. Le direct Twitch devra être identifié comme une rediffusion enregistrée et générée par IA. Les conditions de la chaîne YouTube pour les vidéos longues et les droits sur les contenus doivent être vérifiés dans le compte réel.

**Facebook, Instagram, TikTok et les autres réseaux** ne sont pas connectés. Les boutons de partage présents sur le site ouvrent un partage volontaire ; ils ne donnent pas au site une autorisation de publier sur ces comptes. Il reste à choisir le moyen de connexion officiel ou un outil de programmation compatible avec les comptes réellement détenus, puis à essayer et vérifier les publications. Aucun abonnement payant ni nouveau compte n’a été créé.

ChatGPT, Codex et Claude peuvent préparer des textes, du code et des corrections. Les conversations ne se coordonnent pas automatiquement et ne restent pas actives en arrière-plan. C’est GitHub Actions, ou l’outil de programmation effectivement raccordé, qui exécute le calendrier. La clé Claude existante est utilisée par les robots de rédaction, pas par le script de sélection sociale.

## Étapes pour le propriétaire ou ChatGPT

1. Dans le dépôt `Velocemercato/velocemercato.fr`, ouvrir **Actions → VM - Communication matin midi soir**, consulter le dernier passage et télécharger **vm-communication**. Vérifier les deux textes et le champ de résultat. Un statut `sent` exige un identifiant de message et doit correspondre au salon réel.
2. Si `non_connecte`, vérifier **Settings → Secrets and variables → Actions → DISCORD_WEBHOOK** et les autorisations du salon. Saisir l’accès seulement dans les réglages sécurisés, jamais dans la conversation ou le dépôt. Relancer ensuite le workflow avec `publish=true` pour envoyer les contenus disponibles.
3. Pour YouTube/Twitch et les autres comptes, réaliser la connexion officielle dans un outil disponible, puis un premier essai privé ou en brouillon. Vérifier son résultat avant d’activer le calendrier public. La demande de publication du propriétaire est déjà donnée ; l’accès technique reste nécessaire.
4. Pour les tests en ligne et les PR bloqués ici, autoriser les domaines requis dans les réglages réseau de l’environnement : `api.github.com`, `vmunivers.fr`, `velocemercato.fr`, `huggingface.co`, puis les hôtes de redirection du modèle seulement s’ils sont effectivement nécessaires. Le push Git fonctionne déjà ; un nouveau jeton GitHub ne corrige pas un refus du proxy.

Le message complet à transmettre à ChatGPT est dans `docs/MESSAGE_POUR_CHATGPT.md`. Aucun secret ne doit être collé dans ce message.
