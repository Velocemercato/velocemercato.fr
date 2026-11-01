# ACTUALISATION — DIMANCHE 1er NOVEMBRE 2026, 08 h 01 PARIS

**CINQ publications réelles confirmées par les APIs Meta sur les 5 destinations autorisées.**
Elles correspondent à une série matinale de contenus différents, pas nécessairement
aux rubriques horaires exactes du programme de la journée.

| Réseau et marque | Heure réelle (Paris) | État vérifié | ID de publication | Lien confirmé |
|---|---|---|---|---|
| Facebook VeloceMercato | 07:52 | **PUBLIÉ** | `1384363904759072_122106610869520366` | https://www.facebook.com/122106465861520366/posts/122106610869520366 |
| Instagram VeloceMercato | 07:52 | **PUBLIÉ** | `17946519030377659` | https://www.instagram.com/p/DfMIdhHEiIp/ |
| Facebook RQ Pronos | 07:56 | **PUBLIÉ** | `112294796981981_1757944626331923` | https://www.facebook.com/1757379583055094/posts/1757944626331923 |
| Facebook VMunivers.fr | 07:59 | **PUBLIÉ** | `1349998758205153_122098581483535169` | https://www.facebook.com/122098313661535169/posts/122098581483535169 |
| Instagram VMunivers.fr | 07:59 | **PUBLIÉ** | `17915322627506871` | https://www.instagram.com/p/DfMJNbqoUYL/ |

Les publications sont attestées par les journaux des Actions suivants :
- Audit Meta lecture seule https://github.com/Velocemercato/velocemercato.fr/actions/runs/41282613224 (FB/IG Véloce)
- Coup d'envoi RQ https://github.com/Velocemercato/velocemercato.fr/actions/runs/41282788067 (1 Facebook)
- Lancement VM Univers https://github.com/Velocemercato/velocemercato.fr/actions/runs/41282928316 (FB et Instagram)

## Suivi des créneaux à venir (contrôle 08:01)

| Créneau prévu | Facebook Véloce | Instagram Véloce | Facebook VM Univers | Instagram VM Univers | Facebook RQ Pronos |
|---|---|---|---|---|---|
| 08h · Foot/Gaming | **NON PUBLIÉ** — créneau en cours | **NON PUBLIÉ** — créneau en cours | **NON PUBLIÉ** — destination non programmée | **NON PUBLIÉ** — non programmé | **NON PUBLIÉ** — horaire du robot à venir |
| 10h · VM Belfort | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — futur |
| 10h40 · Prono fictif 100 points | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur |
| 11h · JT Foot | NON PUBLIÉ — lien public à vérifier | NON PUBLIÉ — vidéo à vérifier | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — lien public à vérifier |
| 12h · JT Actus | NON PUBLIÉ — lien public à vérifier | NON PUBLIÉ — vidéo à vérifier | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — lien public à vérifier |
| 13h · Gaming | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur |
| 15h · VM Belfort | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur | NON PUBLIÉ — vidéo spécifique non produite | NON PUBLIÉ — futur |
| 18h · Foot | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur |
| 19h · Actus | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur |
| 20h · Gaming | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur |
| 21h · Projet VM | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — futur | NON PUBLIÉ — futur | NON PUBLIÉ — futur |
| 22h30 · Bilan de semaine | NON PUBLIÉ — vidéo 60 min non confirmée | NON PUBLIÉ — vidéo non confirmée | NON PUBLIÉ — non prévu | NON PUBLIÉ — non prévu | NON PUBLIÉ — vidéo 60 min non confirmée |

**Sécurité :** PR #86 fusionnée sur `main` ; tests hors ligne réussis,
contrôle ID exact de chaque Page. RQ Pronos n'est reliée à aucun Instagram.
Les archives et reçus AES-GCM de `broadcast-state` n'ont pas été réinitialisés.
Les deux workflows temporaires de lancement ont été rendus manuels après succès.
Un secours `workflow_run` lié aux robots d'information est ajouté à RQ Pronos,
sans changer les clés et avec la prévention des doublons.

**Pronostics :** les matchs de dimanche sont sourcés, et aucun pourcentage/score
n'a été déclaré certain. Bankroll fictive 100 points, aucune mise ni montante réelle.
Mention : « 18+ · Jouer comporte des risques : endettement, isolement, dépendance · Joueurs Info Service 09 74 75 13 13 ».

---

# RAPPORT DE SÉCURITÉ ET DE DIFFUSIONS — dimanche 1er novembre 2026
**Cliché au dimanche 1er novembre 2026 à 07 h 43 (heure Europe/Paris)**.
Pas un suivi continu, pas un message de publication. Les heures après ce contrôle restent à venir.

## Sécurité — STOP
- L'ancien code `tools/publier_meta.py` sur `main` présente un retour implicite vers la première destination demandée. Ce n'est pas la route employée par les posts précédemment vérifiés, mais c'est ambigu et doit être corrigé.
- Correction sur la branche **`correctif-securite-meta-agenda-2026-11-01`** (pas fusionnée), avec validation des IDs `meta=1384363904759072`, `meta_univers=1349998758205153`, `meta_pronos=112294796981981`, refus de tout Instagram sur `meta_pronos`.
- Tests hors ligne sur cette branche : **21 tests verts**, lancement https://github.com/Velocemercato/velocemercato.fr/actions/runs/41281847646 .
- Aucune suppression, publication ni modification de `broadcast-state` due à cette tâche. Les automatisations historiques sur `main` n'ont pas été désactivées.

## Contrôle réel en lecture seule
Audit https://github.com/Velocemercato/velocemercato.fr/actions/runs/41281974056 : **0 URL confirmée ce dimanche au moment du contrôle** sur FB meta, IG meta, FB meta_univers, IG meta_univers, FB meta_pronos. Ce constat ne prouve pas l'absence de publications antérieures, ni futures.

## Tableau demandé par créneau et destination
**NP = NON PUBLIÉ** au moment du contrôle. *0 preuve* = aucun lien/ID identifié ; *à venir* = heure future ; *hors programme* = destination non prévue ; *vidéo à vérifier* = contenu vidéo public non confirmé.

| Créneau | Facebook Véloce | Instagram Véloce | Facebook VM Univers | Instagram VM Univers | Facebook RQ Pronos |
|---|---|---|---|---|---|
| 07h · Actus | NP·0 preuve | NP·0 preuve | NP·hors programme | NP·hors programme | NP·0 preuve |
| 08h · Foot/Gaming | NP·à venir | NP·à venir | NP·hors programme | NP·hors programme | NP·à venir |
| 10h · Belfort | NP·hors programme | NP·hors programme | NP·à venir | NP·à venir | NP·à venir |
| 10h40 · Analyse fictive | NP·hors programme | NP·hors programme | NP·hors programme | NP·hors programme | NP·à venir |
| 11h · JT Foot | NP·vidéo à vérifier | NP·vidéo à vérifier | NP·hors programme | NP·hors programme | NP·vidéo à vérifier |
| 12h · JT Actus | NP·vidéo à vérifier | NP·vidéo à vérifier | NP·hors programme | NP·hors programme | NP·vidéo à vérifier |
| 13h · Gaming | NP·à venir | NP·à venir | NP·hors programme | NP·hors programme | NP·à venir |
| 15h · Belfort | NP·hors programme | NP·hors programme | NP·à venir | NP·vidéo à vérifier | NP·à venir |
| 18h · Foot | NP·à venir | NP·à venir | NP·hors programme | NP·hors programme | NP·à venir |
| 19h · Actus | NP·à venir | NP·à venir | NP·hors programme | NP·hors programme | NP·à venir |
| 20h · Gaming | NP·à venir | NP·à venir | NP·hors programme | NP·hors programme | NP·à venir |
| 21h · Projets | NP·hors programme | NP·hors programme | NP·à venir | NP·à venir | NP·à venir |
| 22h30 · Bilan vidéo | NP·vidéo à vérifier | NP·vidéo à vérifier | NP·hors programme | NP·hors programme | NP·vidéo à vérifier |

RQ Pronos ne possède **aucun Instagram**. Aucune de ces cases ne doit être marquée « PUBLIÉ » sans ID et URL de la plateforme.

## Matchs officiels corrigés
- Strasbourg–Auxerre : 15h, LFP https://ligue1.com/fr/articles/l1_article_5805-
- Paris FC–Monaco : 17h15, LFP idem
- **Lyon–Angers : 17h15**, déplacement officiel LFP https://ligue1.com/fr/articles/l1_article_6010-j9-ol-angers-decale-au-dimanche-1er-novembre-ligue-1-2026-2027
- Liverpool–Arsenal : 17h30 à Paris (16h30 GMT), Liverpool FC https://lfcbeta.liverpoolfc.com/matches/mens-team/liverpool-v-arsenal-english-premier-league-20261101
- Marseille–Toulouse : 20h45, LFP idem
Fichier préparé sur branche (non publié) : `programmes/avant_match_2026-11-01.json`.
Simulation : 100 points fictifs, zéro argent réel ; ni montante ni probabilités fabriquées.
**18+ · Jouer comporte des risques : endettement, isolement, dépendance · Joueurs Info Service 09 74 75 13 13.**

## Reste à faire
Faire valider/fusionner le correctif de sécurité en `main` et vérifier les envois ultérieurs par URL confirmée (pas simplement un workflow vert). Ne jamais antidater ni rattraper les créneaux passés en rafale.