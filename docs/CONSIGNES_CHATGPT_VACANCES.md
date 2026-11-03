# Consignes pour ChatGPT — absence de Heineguez (4 au 17 novembre 2026)

Projet : https://github.com/Velocemercato/velocemercato.fr (site velocemercato.fr) et
https://github.com/Velocemercato/vmunivers (site vmunivers.fr). Heineguez est absent deux semaines.
Tout doit continuer à tourner **sans rien casser**. En cas de doute : ne rien publier, noter le problème.

## Ce qui tourne déjà tout seul (ne pas modifier)
- **JT vidéo** (La Pastille TV) sur YouTube, 6 par jour, et **Shorts du JT** à midi (sauf dimanche).
- **Facebook / Instagram automatiques** (`publier-meta.yml`) : actus et JT sur Véloce Mercato, VM Univers, RQ Pronos.
- **Campagne quotidienne VÉLOCE TEAM** (`campagne-quotidienne.yml`, 17 h 41 Paris) : publie le jour prévu dans
  `campagnes/calendrier.json` (Facebook + Instagram de Véloce Mercato et VM Univers ; Short YouTube le dimanche).
  Calendrier rempli jusqu'au **17 novembre**. Liens publics : `campagnes/journal.json`.
- **Séance Claude chaque lundi matin** : prépare la semaine suivante du calendrier (visuels + textes + tests).

## Ton rôle
1. **Chaque jour après 18 h** : ouvrir GitHub → Actions → « VM - Campagne quotidienne VÉLOCE TEAM ».
   Vert = publié (liens dans le résumé et `campagnes/journal.json`). Rouge = lire le « BILAN » de l'exécution.
2. **Si le lundi la semaine suivante n'a pas été ajoutée** (moins de 3 jours d'avance dans le calendrier) :
   ajouter 7 jours en suivant `campagnes/README.md`, générer les visuels avec
   `python tools/campagne_quotidienne.py --visuels --depuis AAAA-MM-JJ`, lancer
   `python -m pytest tests/test_campagne_quotidienne.py`, ouvrir une PR et la fusionner seulement si tout passe.
3. **TikTok** (pas automatique) : le kit est dans `campagnes/TIKTOK.md` (vidéo + texte de chaque jour).

## Règles absolues
- **Jamais** de doublon : ne jamais relancer à la main une publication déjà « PUBLIÉ » ; le robot l'ignore de toute façon.
- **Jamais** modifier les secrets, jetons, identifiants de Pages ou la clé `VM_DIFFUSION_STATE_KEY`.
- **Jamais** supprimer une publication, une vidéo ou un fichier existant.
- **Jamais** utiliser la page RQ Pronos (18+) pour la campagne VÉLOCE TEAM.
- **Jamais** de vidéo, musique ou image d'un tiers : uniquement les visuels VM (personnage Véloce, logo, illustrations VM).
- **Jamais** inventer un résultat : si une publication échoue, l'écrire tel quel.
- Garder l'identité visuelle : noir, rouge néon, or, vert ; ne pas refaire le décor des sites.

## Pannes connues et réponse
| Message dans le bilan | Cause | Que faire |
|---|---|---|
| `uploadLimitExceeded` | limite d'envois YouTube sur 24 h | rien : relancer le lendemain, sans doublon |
| `ACCESS_TOKEN_SCOPE_INSUFFICIENT` | l'autorisation YouTube ne permet pas de modifier une vidéo | ne pas toucher aux identifiants ; signaler à Heineguez |
| `Média public indisponible` | le site n'avait pas encore publié les visuels | relancer l'exécution 10 minutes plus tard |
| `Meta a refusé (… code 190 …)` | jeton Meta expiré | ne rien faire, signaler à Heineguez à son retour |
| `Aucun contenu prévu pour …` | calendrier vide ce jour-là | ajouter les jours (voir point 2) |

## Arrêt d'urgence
Dans `campagnes/calendrier.json`, mettre `"actif": false` : la campagne s'arrête dès le jour suivant,
sans toucher au reste.

Contexte et historique : `docs/AUDIT_CLAUDE_2026-11-02.md`, `docs/CAMPAGNE_VELOCE_TEAM_2026-11-03.md`.
