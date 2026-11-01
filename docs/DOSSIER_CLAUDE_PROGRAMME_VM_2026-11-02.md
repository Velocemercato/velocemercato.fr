# DOSSIER POUR CLAUDE + CHATGPT — GROUPE VM
Date de rédaction : dimanche 1er novembre 2026, matin (Europe/Paris).
**Date du programme : lundi 2 novembre 2026.** Le samedi suivant est le **7 novembre 2026**. Ne pas appeler lundi « samedi ».

## Ordre de mission
Produire un programme éditorial soutenu **mais factuel** sur trois Pages Facebook :
- **VéloceMercato** : football, mercato, JT Foot, reportages ;
- **VMunivers.fr** : projets du groupe, sélection des meilleures publications, VM Belfort et VM Studio ;
- **RQ Pronos**, ID Facebook EXACT `112294796981981` : actualités mixtes, football, gaming, Belfort, agenda et analyses sportives fictives.
- Instagram **VéloceMercato** et **VMunivers.fr** uniquement si leur association Meta a déjà été vérifiée. **Aucun Instagram RQ Pronos.**
- Pages : https://velocemercato.fr/studio/reseaux.html et https://vmunivers.fr/studio/reseaux.html : kits de partage (pas des comptes qui publient).
- Ne pas envoyer le même texte identique partout ; adapter l'accroche, la source et le lien à chaque marque.

## Grille éditoriale demandée — heure de Paris
| Heure | Matière à préparer | Format / garde-fou |
|---|---|---|
| 07 h | Actu générale du jour | Brève vérifiée + lien ; diffusion si récente |
| 08 h | Football & gaming | 1–2 posts différents, liens sourcés |
| 10 h | VM Belfort + sélection sportive | Actualité locale ; analyse factuelle sans pari réel |
| 11 h | JT Foot | Vidéo seulement si le MP4 est **produit et accessible** ; sinon lien vers le dernier JT Foot publié |
| 12 h | JT Actus | Même règle vidéo |
| 13 h | Gaming | Brève vérifiée + JT s'il existe |
| 15 h | JT VM Belfort | **À produire** : le robot actuel ne garantit pas une émission locale dédiée ; sinon flash écrit, jamais inventer un MP4 |
| 18 h | Actu football | Brève vérifiée |
| 19 h | Actu du jour | Brève vérifiée |
| 20 h | Actu gaming | Brève vérifiée |
| 22 h 30 | Grande rétrospective de semaine/week-end | **Objectif : 1 h de vidéo** ; il faut assembler des segments dont les droits et la durée sont vérifiés. À défaut, partager les JT existants **sans écrire « une heure »** |

### Contraintes matérielles déjà constatées
- Le robot `VM Studio - La Pastille TV` produit déjà des JT Foot, Actus et Gaming. Ne pas multiplier les originaux sans vérifier le quota YouTube, la durée des rendus et l'hébergement.
- Le Kit Réseaux des JT a présenté des échecs par commit Git vide ; correction apportée dans `tools/reseaux_jt.py` le 1er novembre ; vérifier la prochaine exécution GitHub.
- Les workflows `publier-meta.yml` (Pages meta + meta_univers) et `pronos-publications.yml` (RQ Pronos) sont séparés. Ils ont un **registre chiffré de reçus** dans la branche `broadcast-state`. Ne jamais supprimer, réinitialiser ou copier ses jetons dans le dépôt.
- Ne pas prendre un workflow « vert » pour une publication : exiger `id` et `permalink_url` confirmés par Facebook/Instagram.
- À 07 h pile, GitHub Actions peut démarrer légèrement plus tard ; décaler la promesse « à 7 h » vers « créneau de 7 h ».
- Ne jamais supprimer les posts 2026 : le nettoyage des 11 anciens posts de 2024 RQ Pronos n'est **pas confirmé comme terminé**.

## Avant-match SOURCÉ du lundi 2 novembre
Données enregistrées dans `programmes/avant_match_2026-11-02.json`. Ne diffuser que les chiffres identifiables et encore exacts à l'heure du post.

**Lorient – Brest, lundi à 20 h 45 Paris, Ligue 1.**
- Sports Mole et Programme Foot annoncent l'affiche.
- OddAlerts rapporte, avant coup d'envoi, 2 victoires sur les 5 derniers matchs de Lorient, 1 sur 5 pour Brest (échantillon restreint, toutes compétitions).
- Sources : https://www.programmefoot.com/lundi-02-novembre-2026 ; https://www.oddalerts.com/livescores/brest-vs-lorient/8674-8143 ; https://www.sportsmole.co.uk/football/lorient/preview/lorient-vs-brest-prediction-team-news-lineups_607901.html

**Newcastle – Everton, lundi à 21 h Paris, Premier League.**
- Selon PitchLabStats, les 5 derniers matchs de championnat recensés : Newcastle 2 V, 0 N, 3 D ; Everton 1 V, 2 N, 2 D.
- Sources : https://www.skysports.com/football-scores-fixtures/2026-11-02 ; https://pitchlabstats.com/match/2026-11-02-newcastle-everton ; https://www.sportsmole.co.uk/football/newcastle-united/preview/newcastle-vs-everton-prediction-team-news-lineups_608131.html

**Autres affiches annoncées :** Reims – Sochaux à 20 h 45 (intérêt local Belfort/Montbéliard), Atalanta – Parme à 20 h 45, Sassuolo – Fiorentina à 18 h 30, Benfica – Alverca à 21 h 15.
Programme : https://www.programmefoot.com/lundi-02-novembre-2026
Ces horaires peuvent évoluer ; revérifier juste avant publication.

### Analyse sportive fictive (pas d'incitation aux mises)
- Donner d'abord **match, heure, source, séries de résultats, domicile/extérieur, absents confirmés, tendances xG** si disponibles et clairement datées.
- Si Claude/ChatGPT utilise un algorithme, exiger le type de modèle (ex. Elo / Poisson / classification), fenêtre de données, fréquence de recalibration, vérification hors échantillon. **Ne pas inventer de probabilités 1/N/2**, ni de « 90 % sûr », ni de pourcentage sans calcul traçable. Les cotes ne sont pas des probabilités réelles sans correction de marge.
- « Combiné du jour » : à traiter comme **scénario pédagogique 100 % fictif** si au moins deux événements indépendants et vérifiables sont disponibles ; mettre en évidence que **chaque sélection supplémentaire fait baisser la probabilité conjointe**. Pas de montante, aucun montant à miser ou bookmaker.
- Suivi fictif : bankroll de départ **100 points virtuels**, historique daté des analyses publiées (résultats, nuls, erreurs, calibration), **aucune transaction**.
- Obligation en pied de tout pronostic : « Jouer comporte des risques, 18+, Joueurs Info Service 09 74 75 13 13 ».
- En cas d'absences, de données périmées ou de sources contradictoires : **pas de pronostic chiffré**. Publier seulement l'agenda sourcé ou attendre.

## Concrètement, ce que Claude doit faire
1. Avant chaque créneau, lire les JSON actuels `articles.json`, `actus/news.json`, `vm-gaming/news.json`, `belfort/actus.json`, `studio/diffusions.json`, `studio/reseaux.json`, `prono.json`. Identifier les publications déjà envoyées à l'aide des accusés chiffrés.
2. Produire seulement des textes originaux, datés, vérifiables, adaptés aux trois Pages. Pour un post vidéo, confirmer le MP4 ou le lien public YouTube avant de le présenter comme publié.
3. Préparer une **émission de 60 minutes** de bilan de semaine à partir de segments réellement produits, si un montage techniquement et légalement fiable est possible. Sinon marquer `non_prêt` et ne pas publier une promesse trompeuse.
4. Vérifier les autorisations et le suivi des posts avec Meta Graph, journaliser **l'identifiant et le lien public** après chaque envoi ; refuser tout doublon.
5. Laisser le propriétaire valider le nouveau contenu sportif avant diffusion lorsqu'il implique une interprétation contestable ou des pourcentages non calibrés ; l'accord donné concerne la simulation, pas des paris d'argent réel.
6. Corriger les échecs de `VM - Kit réseaux des JT` sans casser les nouvelles pages ; contrôler `vmunivers.fr/studio/reseaux.html`.
7. Dresser un bilan par créneau : `prévu / prêt / publié-confirmé / indisponible`. **Ne jamais annoncer que tout est publié sur toutes les Pages sans les liens.**

## Copie-coller pour Claude
> Tu es le responsable technique et éditorial de VM Univers, Véloce Mercato et RQ Pronos. Exécute uniquement les étapes que les données vérifiées et les connexions actuelles permettent. Respecte la grille ci-dessus, en heure Europe/Paris, pour le lundi 2 novembre 2026. Les nouvelles vidéos doivent exister avant publication. Tous les pronostics et combinés sont des simulations sans argent et sans montante. Vérifie les statistiques et leurs sources ; n'invente jamais de probabilités. Évite absolument les doublons, ne touche pas aux publications de 2026, et fournis à la fin de chaque action le lien Facebook/Instagram/YouTube confirmé ou un statut explicite « non publié ».
