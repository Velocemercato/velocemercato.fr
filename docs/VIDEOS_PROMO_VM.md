# Vidéos promo originales VM — proposition (issue #144)

**Statut : proposition à relire.** Ces vidéos ne sont **pas publiées** et ne figurent pas dans
`campagnes/calendrier.json`. Rien n'a été modifié dans les publications, JT, Shorts, automatisations,
ni dans la campagne VÉLOCE TEAM de 17 h 41.

## 1. Audit des vidéos et ressources existantes (3 novembre 2026)

| Ressource | Format | Son | Origine (d'après le dépôt) |
|---|---|---|---|
| `media/promos/*.mp4` (9 vidéos : foot, actus, gaming, studio) | 20 s, 9:16 et 16:9 | **muet** (−91 dB) | générées par l'outil `creer_promos.py` ; la note `docs/PLAN_PUBLICITE_VM.md` prévoyait une « musique originale », absente des fichiers actuels |
| `assets/social/veloce-team-short.mp4` | 12 s, 9:16 | muet | `tools/veloce_team_visuels.py` (affiche fixe + zoom) |
| `assets/social/campagne/*-reel.mp4` | 10 s, 9:16 | muet | `tools/campagne_quotidienne.py` (affiche fixe + zoom) |
| `mangas/assets/vm-mangas-short.mp4` | 11 s, 9:16 | pas de piste son | campagne VM MANGAS |
| `img/reportages/alexia-depagne/reportage-voix.mp4` | 2 min 41, 9:16 | **voix** | reportage VM avec voix de synthèse |
| Illustrations `img/vm-art/*`, `img/banniere-foot.webp`, `vm-gaming/img/*`, `img/avatar-veloce.webp`, logo | images | — | créations VM (illustrations générées pour VM) ; aucune trace de média tiers |

Limite : le dépôt ne contient pas les fichiers sources ni les licences des outils de génération d'images ;
l'origine est déduite des scripts et des notes. Aucune musique ni vidéo tierce n'a été trouvée dans les vidéos auditées.

## 2. Nouvelles vidéos proposées (`assets/social/promo/`)

Générées par `python tools/vm_videos_promo.py`, aperçus dans `docs/apercus/videos-promo/`.

| Fichier | Accroche | Appel à l'action |
|---|---|---|
| `veloce-team-intro.mp4` | Deux univers, une passion | Rejoins la team |
| `vm-mangas-teaser.mp4` | Notre enfance en dessins animés | Regarde sur VM |
| `foot-amateur.mp4` | Ton club, ta région | Trouve ton club |
| `question-team.mp4` | Team foot ou team univers ? | Réponds en commentaire |
| `veloce-arena.mp4` | Véloce Arena entre potes | Rejoins l'Arena |

Animation en 5 temps sur 15 s (1080×1920, 30 i/s, H.264) : logo couronné → titre → illustration VM ou personnage
Véloce → 3 points → bouton qui pulse. Traits de vitesse façon manga, cadre néon rouge, noir / rouge / or / vert.
Piste son **muette** (aucune musique tierce).

## 3. Contraintes des plateformes respectées

- **9:16, 1080×1920, 15 s** : accepté par les Reels Facebook/Instagram, les Shorts YouTube et TikTok.
- **Zones sûres** : tout le texte reste entre 260 et ~1 600 px de haut et entre 90 et 930 px de large
  (pas sous les boutons de droite ni sous la légende du bas), vérifié par un test à chaque étape de l'animation.
- **Son** : les plateformes favorisent les vidéos avec du son. Ajouter un son **dans l'application** depuis la
  bibliothèque de musique commerciale (comptes de marque) plutôt qu'une musique dans le fichier.
- **TikTok de plus d'une minute** : ces vidéos font 15 s. Aucune promesse d'éligibilité à la rémunération TikTok
  (programme réservé à certains comptes et vidéos de plus d'une minute, selon des critères décidés par TikTok).

## 4. Comment les utiliser ensuite (à décider par Heineguez)

1. **TikTok (manuel)** : les programmer dans TikTok Studio comme le kit `campagnes/TIKTOK.md`.
2. **Campagne quotidienne** : pour qu'un jour du calendrier utilise une de ces vidéos à la place du zoom sur l'affiche,
   il faudra une petite évolution (champ `"video"` optionnel dans un jour, testé) — à faire dans une PR séparée,
   seulement après accord, et uniquement pour des jours pas encore publiés.
3. **Coordination** : ne pas modifier le calendrier pendant la séance Claude du lundi ; vérifier qu'aucune PR ne
   touche `campagnes/calendrier.json` avant d'y ajouter quoi que ce soit (voir `docs/CONSIGNES_CHATGPT_VACANCES.md`).

## Tests

`python -m pytest tests/test_videos_promo.py -q` : format, durée, piste muette, sources VM uniquement,
zones sûres à 7 instants de l'animation, absence du calendrier.
