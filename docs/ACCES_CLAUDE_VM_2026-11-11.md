# Accès et reprise pour Claude — VM
Date : 11 novembre 2026. À lire avec [le dossier principal](DOSSIER_CLAUDE_VM_2026-11-11.md).

Ce document fournit les destinations, le fonctionnement et les contrôles nécessaires. Il ne contient aucun mot de passe ni jeton. Les connexions, sessions et tâches ChatGPT ne sont pas transférées à Claude par ce document. Aucun accès Claude n'a été créé ou vérifié durant cette intervention.

## Où reprendre

| Service | Destination vérifiée | Accès et usage |
|---|---|---|
| GitHub média | https://github.com/Velocemercato/velocemercato.fr | Branch main ; code, articles, workflows, rapports, kit |
| GitHub vitrine | https://github.com/Velocemercato/vmunivers | Branch main ; garder la présentation validée |
| Site média | https://velocemercato.fr/ | Accueil bureau validé |
| Foot historique actualisé | https://velocemercato.fr/foot/ | Visuel du 4 novembre ; actualités actuelles |
| Vitrine | https://vmunivers.fr/ | Tableau réseaux corrigé ; pas de refonte demandée |
| Cloudflare | https://dash.cloudflare.com/ | Compte c5227875896e9a281915ed70c146e845 ; Pages velocemercato et vmunivers |
| Metricool | Marque 7762102 | Fuseau Europe/Paris ; TikTok velocemercato, Instagram vmunivers.fr, Facebook VM Actus et Pronos et chaîne YouTube liés à cette marque lors du contrôle |
| Meta direct | Connexions chiffrées du dépôt média | Trois Facebook et deux Instagram, voir ci-dessous |
| Conseils pronos | https://t.me/VMCONSEILSPRONOS | Destination publique du bouton ; aucun droit d'administration Telegram vérifié |
| CapCut | Aucun accès vérifié | Vidéos déjà produites via la chaîne GitHub, pas via CapCut |
| Claude | À connecter dans le propre environnement Claude | Vérifier ses outils réels avant d'annoncer une autonomie |

## Ce que Romain doit connecter dans Claude

1. Connecter GitHub depuis les réglages officiels de Claude, avec accès aux deux dépôts ci-dessus, puis demander une lecture du dossier et de main. La visibilité de ce document seul ne donne pas de droit de modification.
2. Faire vérifier les capacités réellement offertes : lire, proposer/modifier un fichier et consulter les exécutions GitHub Actions. Une connexion GitHub qui ne propose que la lecture ne permet pas de publier du code.
3. Pour déployer le site média, utiliser le workflow existant `.github/workflows/deployer-accueil-cloudflare.yml`. Les secrets GitHub `CLOUDFLARE_API_TOKEN` et `CLOUDFLARE_ACCOUNT_ID` sont déjà utilisés par ce workflow ; ne pas les recopier dans le dossier ou dans une conversation. Aucun droit DNS ou facturation n'est requis pour cette reprise du site.
4. Pour Metricool, vérifier que l'environnement Claude dispose effectivement d'une intégration permettant la programmation sur la marque 7762102. Sinon, l'accès web seul et le dossier ne prouvent pas qu'il peut programmer. Ne pas publier un second lot à l'aveugle.
5. Les autres réseaux ne sont pas automatiquement administrables dans Claude. Vérifier chaque connexion et ses permissions séparément. Aucun accès Snapchat, Discord, Twitch ou administration Telegram n'a été établi par leur simple présence sur le site.

Le compte personnel et l'autorisation de Romain restent nécessaires aux étapes de connexion affichées par chaque service. Ne pas transmettre le mot de passe précédemment écrit dans la conversation ; le modifier depuis le service concerné.

## Meta : identités confirmées et état à conserver

| Connexion interne | Facebook confirmé | Instagram confirmé |
|---|---|---|
| meta | Véloce Mercato, Page ID 1384363904759072 | veloce.mercato |
| meta_pronos | VM Actus et Pronos, Page ID 112294796981981 | Aucun Instagram confirmé pour cette connexion |
| meta_univers | VM Univers, Page ID 1349998758205153 | vmunivers.fr |

Ces identifiants techniques ne sont pas les liens de partage ni nécessairement les identifiants présents dans les URLs publiques des publications. Le programme vérifie l'identité auprès de Meta avant d'envoyer.

Les connexions et les accusés sont dans `broadcast-state/state.enc`, chiffrés avec le secret GitHub `VM_DIFFUSION_STATE_KEY`. Ils sont exploités dans les workflows existants. Ne pas afficher les données déchiffrées, remplacer la clé, effacer les reçus, ou recréer des jetons pour une simple reprise du code. Les secrets GitHub ne sont pas lisibles via le connecteur utilisé ici.

Le bilan public est `studio/editorial-status.json`. Les contrôles distinguent confirmé, tentative et absence de connexion. Il y a deux Instagram vérifiés ; le troisième demandé n'est pas identifié.

## TikTok : ne pas dupliquer le programmateur

La tâche ChatGPT **Programmer les vidéos TikTok VM**, identifiant `Automation_b430a95c1db8819180d7d01ca31231ac`, est activée à 8 h 30, 11 h 30 et 19 h 30 Paris, pour les blocs de 9 h, 12 h et 20 h. Elle vise Foot, Actus, Gaming, trois vidéos espacées par bloc, selon disponibilité réelle.

Cette tâche appartient à ChatGPT. Claude ne la reçoit pas en lisant GitHub. Le fichier `studio/metricool-planning.json` contient les réservations et résultats : le consulter avant chaque envoi. Le workflow `tiktok-metricool.yml` reste en diagnostic manuel privé.

Si Claude doit devenir l'unique programmateur, il faut d'abord vérifier son accès Metricool, consulter le calendrier et les réservations, préparer sa solution, puis désactiver l'ancien programmateur avant d'activer le nouveau. Ne pas laisser deux outils programmer la même vidéo. Une vidéo prête n'est pas une publication confirmée.

## Vérification de reprise et dossier d'audit

Avant tout changement : noter le commit main actuel, lire les derniers rapports et reçus, vérifier les exécutions Actions, puis contrôler le domaine public. Garder les changements des autres assistants ; aucun force-push.

Commencer par l'audit général demandé : téléphone, boutons du bureau, rubrique Foot, articles lisibles, filtres, flux frais, classement, replays et réseaux. Conserver le visuel validé par Romain. Le rapport automatisé actuel trouve zéro 404/410 confirmé, mais 93 liens protégés/non vérifiables et un classement One Piece dans Gaming à examiner. Ce n'est pas une validation complète de tous les parcours.

Fichiers de référence :
- `docs/DOSSIER_CLAUDE_VM_2026-11-11.md`
- `docs/AUDIT_CLAUDE_2026-11-11.json` et `.md`
- `docs/CLAUDE_VIDEO_VM_2026-11-11.md`
- `studio/editorial-status.json`, `studio/teasers.json`, `studio/metricool-planning.json`
- Kit : https://velocemercato.fr/studio/kit-automatique

Reste explicitement ouvert : troisième Instagram, vérifications manuelles de l'audit, refrain chanté original et dixième vidéo promotionnelle. Aucun des accès non vérifiés ne doit être annoncé comme acquis.
