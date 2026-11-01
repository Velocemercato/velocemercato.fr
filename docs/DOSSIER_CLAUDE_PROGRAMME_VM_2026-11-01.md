# GROUPE VM — PRIORITÉ DIMANCHE 1er NOVEMBRE 2026 (heure de Paris)

## DIRECTIVE POUR CLAUDE
L'utilisateur a corrigé : il veut **DIMANCHE 1er NOVEMBRE**, pas lundi. Ne pas poster le dossier de lundi sur les créneaux du dimanche. Lundi 2 reste préparé séparément dans `docs/DOSSIER_CLAUDE_PROGRAMME_VM_2026-11-02.md`.

## CONTRÔLE DE SÉCURITÉ AVANT DIFFUSION — BLOCAGE VOLONTAIRE

**État de cette branche : préparation seulement, aucune nouvelle publication déclenchée.**
- Détection dans `tools/publier_meta.py` d'un ancien `return available[next(iter(requested.values()))]` : la connexion publiait pourtant via identifiants sauvegardés, mais ce retour implicite était ambigu.
- Correction de ce retour sur `correctif-securite-meta-agenda-2026-11-01` ; contrôle additionnel des IDs exacts : `meta = 1384363904759072`, `meta_univers = 1349998758205153`, `meta_pronos = 112294796981981`.
- Tout Instagram sur `meta_pronos` bloque désormais la diffusion (Facebook seul), y compris dans le contrôleur de diffusion principal. Les workflow automatiques historiques sur `main` **ne sont pas modifiés par ce correctif**.
- Attendre le succès des tests de la branche, puis validation et intégration contrôlée avant de relancer une nouvelle campagne. Ne pas contourner ce verrou via un autre workflow.

### Réseaux et marques
- Facebook VeloceMercato = `meta`, football / actualités ;
- Facebook VMunivers.fr = `meta_univers`, projets et communication VM ;
- Facebook RQ Pronos = `meta_pronos`, Page ID **112294796981981**, agenda et football + diverses actualités ;
- Instagram VeloceMercato et VMunivers.fr = comptes existants et reliés. **Pas de compte Instagram RQ Pronos.**
- Kit JT : https://velocemercato.fr/studio/reseaux.html
- Kit univers : https://vmunivers.fr/studio/reseaux.html
- Ne jamais copier le même message sur les trois Pages, ni annoncer de publication sans accusé Facebook/Instagram confirmé.

### Programmation du DIMANCHE — grille souhaitée
| Paris | Sujet | Livraison responsable |
|---|---|---|
| 07h | Actualités générales du matin | Post sourcé, ne pas antédater si créneau passé |
| 08h | Foot et gaming | Deux brèves différentes et vérifiées |
| 10h | VM Belfort | Flash local sourcé ; pas de faux JT vidéo |
| 10h40 | RQ Pronos : matchs de dimanche + simulation | Publier agenda officiel du jour sans pourcentages inventés |
| 11h | JT Foot | Seulement s'il existe un MP4 / lien YouTube réellement public |
| 12h | JT Actus | Même précaution |
| 13h | Gaming | Infos récentes, lien vers VM Gaming |
| 15h | VM Belfort | Deuxième flash local ; vidéo uniquement si réellement produite |
| 18h | Football | Brève sourcée |
| 19h | Actualités | Brève sourcée |
| 20h | Gaming | Brève sourcée |
| 21h | Projet VM Univers | Promotion d'un projet réel |
| 22h30 | Magazine de la semaine et du week-end | L'objectif **60 minutes de vidéo** n'est pas produit/confirmé. Ne jamais titrer « 1 h » sans MP4 d'une heure ; partager des JT existants seulement. |

### Matchs à vérifier et expliquer
Le fichier `programmes/avant_match_2026-11-01.json` contient l'agenda et des liens sources :
1. Strasbourg–Auxerre, 15h Paris (Ligue 1, LFP).
2. Paris FC–Monaco, 17h15 (Ligue 1, LFP).
3. **Lyon–Angers, 17h15** (Ligue 1, match décalé du samedi au dimanche par la LFP le 27/10/2026).
4. Liverpool–Arsenal, 17h30 Paris (16h30 GMT, calendrier officiel Liverpool FC).
5. Marseille–Toulouse, 20h45 (Ligue 1, LFP).

**Liens officiels** :
- https://ligue1.com/fr/articles/l1_article_5805- (calendrier L1, hors modification OL)
- https://ligue1.com/fr/articles/l1_article_6010-j9-ol-angers-decale-au-dimanche-1er-novembre-ligue-1-2026-2027 (correction OL–Angers, 17h15)
- https://lfcbeta.liverpoolfc.com/matches/mens-team/liverpool-v-arsenal-english-premier-league-20261101 (16h30 GMT)
- https://fplchallenge.premierleague.com/en/fixtures/9 (calendrier Premier League)

Ne pas transformer un horaire vérifié en probabilité ou score garanti. Vérifier les compositions, blessures et forme des équipes avant tout chiffrage ; un modèle Elo/Poisson doit fournir ses données et sa calibration avant publication. On peut afficher **100 points fictifs de bankroll** et expliquer qu'un combiné augmente les risques, mais **aucune mise réelle, aucune montante**. Mention obligatoire : « 18+ · Jouer comporte des risques : endettement, isolement, dépendance · Joueurs Info Service 09 74 75 13 13 ».

### Livrables et méthode technique
- Scripts actuels : `tools/pronos_programme.py`, `tools/pronos_facebook.py`, `tools/publier_meta.py`, `pastille_schedule.py`, `tools/reseaux_jt.py`.
- Source JT réellement publiée : `studio/diffusions.json` ; prêter attention au `status=published` et au lien vidéo public.
- Sources de news : `articles.json`, `actus/news.json`, `vm-gaming/news.json`, `belfort/actus.json`.
- Robots GitHub : `.github/workflows/pronos-publications.yml`, `.github/workflows/publier-meta.yml`, `.github/workflows/emissions.yml`, `.github/workflows/reseaux.yml`.
- Les accusés sont chiffrés sur branche `broadcast-state`, ne pas la réinitialiser. Vérifier URL/ID après chaque envoi ; les tests hors ligne ne constituent pas un post réel.
- Le kit de JT a eu des erreurs liées aux commits Git vides ; une correction a été apportée à `tools/reseaux_jt.py` ; surveiller les exécutions après modification.

### TEXTE À COPIER À CLAUDE
> PRIORITÉ ABSOLUE AU DIMANCHE 1er NOVEMBRE 2026. Applique le programme du dossier `docs/DOSSIER_CLAUDE_PROGRAMME_VM_2026-11-01.md` et les 5 affiches officielles du fichier `programmes/avant_match_2026-11-01.json`. Contrôle les sources, la date des matchs, les nouvelles vidéos et le statut de chaque destination. Mets en forme différemment les posts pour VeloceMercato, VMunivers.fr et RQ Pronos, plus les deux Instagram connectés. Ne publie aucune fausse vidéo, aucune cote ou probabilité inventée, et aucune montante ; bankroll de 100 points uniquement fictifs. Utilise seulement la signature éditoriale « VM », sans prénom ni ville personnelle. Après chaque publication, rapporte le lien confirmé par Facebook/Instagram. Pour les créneaux manqués, ne fais pas de rafale de posts rétroactifs.
