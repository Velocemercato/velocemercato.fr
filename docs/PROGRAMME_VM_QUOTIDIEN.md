# Groupe VM — grille quotidienne récurrente
**À partir du dimanche 1er novembre 2026, tous les jours sans date de fin.** Heure : Europe/Paris (hiver/été).  
**Programme éditorial ≠ confirmation de publication.** GitHub Actions peut retarder ou manquer un lancement.

## Source canonique et kits
- Grille JSON commune : [`programmes/grille_vm_quotidienne.json`](../programmes/grille_vm_quotidienne.json).
- Kit réseaux des JT : https://velocemercato.fr/studio/reseaux.html — affiche désormais la grille du jour et l'âge des dernières vidéos préparées ; nouvelle entrée après production du JT.
- Programme VM Univers : https://velocemercato.fr/studio/programme-vmunivers.html — à 10 h et 15 h, les flashs locaux exigent des sources et ne sont pas des textes prêts à poster ; à 21 h, projet en rotation.
- La page https://vmunivers.fr/studio/reseaux.html est une destination distincte. Sa présence et sa synchronisation ne sont pas démontrées par les modifications du présent dépôt.

## Programme identique chaque jour
| Paris | Rubrique | Robots existants et preuve exigée |
|---|---|---|
| 07:00 | Actus générales | Meta Véloce / RQ : article récent sourcé |
| 08:00 | Football et gaming | Meta Véloce : football ; RQ : foot ; gaming aussi à 13 h |
| 10:00 | VM Belfort | Meta Univers / RQ : source locale datée et différente |
| 10:40 | Agenda RQ Pronos | Données sportives officielles du jour si disponibles, ou aucune publication |
| 11:00 | JT Foot | Partage du JT YouTube réellement publié uniquement |
| 12:00 | JT Actus | Idem ; pas de vidéo inventée |
| 13:00 | Gaming | Article récent vérifié ; extrait vidéo si réellement disponible |
| 15:00 | VM Belfort (second flash) | Autre information locale datée ; pas de faux JT |
| 18:00 | Football | Brève récente différente |
| 19:00 | Actualités | Brève récente différente |
| 20:00 | Gaming | Brève récente différente |
| 21:00 | Projet VM Univers | Projet réel en rotation ; RQ Pronos peut relayer un projet |
| 22:30 | Bilan du jour | Dernier JT public récent si disponible ; pas de vidéo « 60 minutes » fictive |

Le contenu **change chaque jour**, mais la structure reste la même. Tous les créneaux sont conditionnels : si les sources manquent, le robot affiche « non publié » au lieu de remplir avec des données inventées. **Aucun rattrapage massif des heures manquées.**

## Connexions et sécurité inchangées
- Facebook Véloce : `meta` = `1384363904759072`.
- Facebook VM Univers : `meta_univers` = `1349998758205153`.
- Facebook RQ Pronos : `meta_pronos` = `112294796981981` (aucun Instagram RQ).
- Instagram : seulement les comptes déjà liés à `meta` et `meta_univers`, si média valable.
- Les accusés et jetons sont dans `broadcast-state`, chiffrés ; ne pas initialiser ni effacer cette branche. Vérification et reçus de Meta après envoi. Ni changement d'identifiants ni suppression de posts.
- RQ Pronos : toujours 100 points fictifs, sans argent réel, sans montante, sans certitude inventée. `18+ · Jouer comporte des risques : endettement, isolement, dépendance · Joueurs Info Service 09 74 75 13 13`.
- Les vidéos JT YouTube sont soumises au pipeline existant et à ses quotas. **Le kit est un outil de préparation/partage, pas une preuve de mise en ligne Meta ou TikTok.**

## Où contrôler les résultats
- GitHub Actions `VM - Facebook et Instagram automatiques` : `.github/workflows/publier-meta.yml`.
- GitHub Actions `VM - RQ Pronos publications (apres test confirme)` : `.github/workflows/pronos-publications.yml`.
- GitHub Actions `VM Studio - La Pastille TV` : `.github/workflows/emissions.yml`.
- GitHub Actions `VM - Kit réseaux des JT` : `.github/workflows/reseaux.yml` (après production + contrôles quotidiens).
- GitHub Actions `VM - Releve quotidien des liens Meta (LECTURE SEULE)` : contrôle public sans POST, maintenant à la date du jour.
- Tests `tests/test_grille_quotidienne.py` sans réseau ni publications.

### Attention au 2 novembre et après
Les matches du 1er novembre ne doivent pas être réutilisés le 2. Le script RQ consulte le fichier officiel **du jour courant** `programmes/avant_match_AAAA-MM-JJ.json` s'il existe avec sources vérifiées, puis le prono daté existant si valable. Sans fixture officielle : **pas de faux agenda ni pourcentage**. La production automatique de nouveaux calendriers officiels chaque jour et la vidéo bilan de 60 minutes ne sont pas garanties par cette modification.

**Terminé techniquement** signifie grille, scripts, kits et tests sur `main`, mais **publié confirmé** n'est déclaré que pour les posts accompagnés de leurs identifiants et liens publics vérifiés.
