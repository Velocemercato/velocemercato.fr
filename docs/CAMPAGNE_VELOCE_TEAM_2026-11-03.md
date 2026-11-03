# Campagne « VÉLOCE TEAM — Deux univers, une passion » — 3 novembre 2026

Objectif : faire découvrir les deux sites, https://velocemercato.fr/ et https://vmunivers.fr/.
Visuels originaux : `assets/social/veloce-team-{post,story}.jpg` et `veloce-team-short.mp4`
(personnage Véloce, logo VM, sans musique tierce), générés par `tools/veloce_team_visuels.py`.

## Publications (une seule fois chacune, accusés chiffrés)

| Compte | Format | Lien public |
|---|---|---|
| Facebook Véloce Mercato | photo | https://www.facebook.com/122106465861520366/posts/122107379217520366 |
| Instagram @veloce.mercato | photo | https://www.instagram.com/p/DfRIbbLDf_1/ |
| Instagram @veloce.mercato | story | 24 h, sans lien permanent |
| Facebook VMunivers.fr | photo | https://www.facebook.com/122098313661535169/posts/122100237297535169 |
| Instagram @vmunivers.fr | photo | https://www.instagram.com/p/DfRIfrGF2jm/ |
| Instagram @vmunivers.fr | story | 24 h, sans lien permanent |
| YouTube Veloce Mercato TV | Short | https://www.youtube.com/shorts/_3CM-P0wqJg (passé en public à la main par Heineguez) |

## Ce qui s'est passé

1. Essai (workflow `veloce-team-campagne.yml`, mode `essai`) : médias publics, Pages, comptes Instagram et chaîne vérifiés ; Short envoyé en privé.
2. Publication : 6/6 publications Meta réussies.
3. Short : passage en public refusé par YouTube (`ACCESS_TOKEN_SCOPE_INSUFFICIENT`, l'autorisation permet l'envoi, pas la modification). Aucune copie renvoyée ; passé en public dans YouTube Studio.
4. Correctif (PR #138) : désormais l'essai n'envoie rien sur YouTube et la publication envoie le Short directement en public.

## À savoir pour les prochaines campagnes

- Relancer `publier` ne republie jamais : chaque envoi est inscrit dans l'état chiffré avant l'appel.
- La chaîne envoie déjà ~7 vidéos par jour (6 JT + 1 Short) : risque de `uploadLimitExceeded` (vu le 1er novembre).
- Twitch n'est pas configuré (identifiants vides, `VM_AUTO_TWITCH` désactivé).
- Pour qu'un robot puisse passer une vidéo de privé à public, il faudrait reconnecter YouTube avec un droit de modification (décision du propriétaire).
