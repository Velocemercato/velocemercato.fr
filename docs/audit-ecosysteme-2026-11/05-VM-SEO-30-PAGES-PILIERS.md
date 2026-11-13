# 05 — Véloce Mercato : stratégie SEO et 30 pages piliers

> Volumes de recherche **non fournis** : à mesurer avec la Search Console (requêtes réelles) et un outil de mots-clés (Google Keyword Planner gratuit, Ubersuggest…). Les priorités ci-dessous reposent sur l’intention et la concurrence perçue. **[HYPOTHÈSE]** Elles sont à recalibrer au bout de 30 jours de données.

## 1. Intentions de recherche
| Intention | Exemples de requêtes | Format VM | Rythme |
|---|---|---|---|
| Info chaude | « transfert [joueur] », « blessure [joueur] » | Brève (Google News) | En continu |
| Navigation récurrente | « classement ligue 1 », « résultats foot ce soir » | Page pilier vivante | Mise à jour automatique |
| « Où regarder » | « [A] [B] chaîne », « match ce soir quelle chaîne » | Page programme TV + page match | Chaque jour |
| Locale | « [club de l’Est] actu », « résultats district » | Page club / foot amateur | Hebdomadaire |
| Evergreen | « hors-jeu règle », « mercato dates » | Guide « Comprendre » | Revue chaque saison |

## 2. Clusters et maillage
```
[Pilier] /mercato/ ── /mercato/officiels/ ── /mercato/[club]/ ── brèves mercato
[Pilier] /ligue-1/ ── /ligue-1/classement/ ── /ligue-1/calendrier/ ── /clubs/[club]/ ── /match/...
[Pilier] /ligue-des-champions/ ── /match/... ── /ou-regarder/ligue-des-champions/
[Pilier] /equipe-de-france/ ── /joueurs/[joueur]/
[Pilier] /foot-amateur/ ── /foot-amateur/[ligue]/ ── /clubs/[club-amateur]/
[Pilier] /ou-regarder/ ── /ou-regarder/[competition]/ ── /match/...
[Pilier] /comprendre/ ── guides evergreen
```
**Les règles de maillage :**
1. Chaque brève contient 1 lien vers sa page pilier (club ou compétition) et 1 bloc « À lire aussi » (3 liens du même cluster).
2. Chaque page pilier liste ses 10 derniers articles, en HTML statique.
3. Le fil d’Ariane est présent partout.
4. Pas plus de 3 liens sortants vers les sources par brève, la source primaire en premier.

## 3. Stratégies par type de page
- **Fraîcheur** :
  - brèves envoyées dans le sitemap News, avec une `lastmod` exacte ;
  - à chaque mise à jour d’un article, ajouter « Mis à jour le … » et une ligne « Ce qui a changé ».
- **Evergreen** :
  - 10 guides « Comprendre le foot » ;
  - relecture au début de chaque saison ;
  - liens depuis les brèves concernées (exemple : une brève sur un hors-jeu lie le guide du hors-jeu).
- **Pages match** :
  - générées depuis les données de scores (déjà présentes) pour la Ligue 1, la Ligue des champions, l’Équipe de France et les clubs de l’Est ;
  - **avant** le match : heure, lieu, chaîne, enjeux ;
  - **pendant** : score ;
  - **après** : résultat, buteurs (si la source est fiable) et liens ;
  - une seule URL par match, mise à jour (jamais 3 pages pour le même match).
- **Pages mercato** :
  - chaque info porte une étiquette (Rumeur, En discussion, Officiel) ;
  - les informations « officielles » ne sont confirmées que par un communiqué du club ou de la ligue.
- **Pages joueur** : **seulement** pour les joueurs qui ont au moins 5 articles VM (pas de pages vides). Contenu : fiche (poste, club, nationalité, à vérifier par source), derniers articles, historique mercato VM.
- **Pages club** : une présentation fixe (fondation, stade, palmarès sourcés) et des parties vivantes (derniers articles, prochains matchs, mercato).
- **Pages compétition** : classement, calendrier, actualités, diffuseurs.
- **Pages « où regarder »** : programme du jour et de la semaine, diffuseurs par compétition (**à vérifier chaque saison**, car les droits TV changent), FAQ.
- **FAQ** :
  - bloc FAQ sur les piliers (3 à 6 questions réelles) ;
  - le balisage `FAQPage` ne garantit plus d’affichage enrichi dans Google, mais il aide les lecteurs et les IA.
- **Vidéo** :
  - page `/pastille/` avec `VideoObject` ;
  - chaque Pastille est accompagnée d’un texte de 150 mots et de liens vers les articles cités.

## 4. Les 30 pages piliers

Légende des priorités :
- **P1** : jours 1 à 30 ;
- **P2** : jours 31 à 60 ;
- **P3** : jours 61 à 90.

---
### 1. `/mercato/` — **H1 : Mercato foot : rumeurs, officiels et bilans en direct**
- **Intention** : info + navigation · **Type** : pilier vivant · **MAJ** : continue (auto) · **Priorité** : P1
- **Mots-clés** : mercato, mercato foot | transferts, rumeurs mercato, mercato ligue 1, mercato officiel
- **Plan** :
  - H2 Les dernières infos mercato (H3 Officiel · H3 En discussion · H3 Rumeurs) ;
  - H2 Mercato par club (H3 Ligue 1 · H3 Clubs de l’Est) ;
  - H2 Dates du mercato ;
  - H2 Comment nous vérifions une info mercato ;
  - H2 FAQ.
- **Éléments** : filtres par étiquette, liste en HTML, encadré méthode, inscription newsletter.
- **Liens** : `/mercato/officiels/`, `/mercato/[club]/`, `/comprendre/mercato-comment-ca-marche/`, `/sources-et-corrections/`.

### 2. `/mercato/officiels/` — **H1 : Transferts officiels : tous les mouvements confirmés**
- Intention : vérification · Type : liste vivante · MAJ : continue · P1
- KW : transferts officiels | transfert confirmé, officialisation, signature
- Plan :
  - H2 Derniers transferts officiels (tableau : joueur, de, vers, type, source) ;
  - H2 Par club ;
  - H2 Prêts et fins de contrat ;
  - H2 FAQ.
- Éléments : lien vers le communiqué officiel du club, obligatoire. Liens : `/mercato/`, pages club.

### 3. `/mercato/dates/` — **H1 : Dates du mercato : ouverture et fermeture du marché des transferts**
- Intention : info evergreen · Type : guide · MAJ : 2 fois par an · P1
- KW : date mercato | fin mercato, ouverture mercato hiver, mercato estival
- Plan :
  - H2 Dates de la fenêtre en cours (à sourcer : LFP et fédérations) ;
  - H2 France, Angleterre, Espagne, Italie, Allemagne ;
  - H2 Les exceptions (jokers, joueurs libres) ;
  - H2 FAQ.
- Liens : `/mercato/`, `/comprendre/mercato-comment-ca-marche/`.

### 4. `/ligue-1/` — **H1 : Ligue 1 : actu, classement, résultats et calendrier**
- Intention : navigation · Type : pilier compétition · MAJ : auto + hebdo · P1
- KW : ligue 1 | actu ligue 1, résultats ligue 1, journée ligue 1
- Plan :
  - H2 À la une ;
  - H2 Résultats de la journée ;
  - H2 Classement (extrait) ;
  - H2 Prochains matchs et diffuseurs ;
  - H2 Mercato Ligue 1 ;
  - H2 Les clubs (grille).
- Liens : `/ligue-1/classement/`, `/ligue-1/calendrier/`, `/clubs/*`, `/ou-regarder/ligue-1/`.

### 5. `/ligue-1/classement/` — **H1 : Classement de Ligue 1**
- Intention : navigation · Type : données · MAJ : auto · P1
- KW : classement ligue 1 | classement L1, tableau ligue 1
- Plan : H2 Classement général ; H2 Forme récente ; H2 Ce que le classement signifie (qualifications européennes, relégation) ; H2 FAQ.
- Éléments : tableau HTML (pas une image), date et heure de mise à jour, source des données.

### 6. `/ligue-1/calendrier/` — **H1 : Calendrier de Ligue 1 : toutes les journées**
- Navigation · données · auto · P2
- KW : calendrier ligue 1 | programme ligue 1, prochaine journée
- Plan : H2 Prochaine journée ; H2 Journées par mois ; H2 Matchs reportés ; H2 Où regarder.

### 7. `/ligue-des-champions/` — **H1 : Ligue des champions : actu, résultats et clubs français**
- Navigation · pilier · auto + hebdo · P1
- KW : ligue des champions | LDC, résultats ligue des champions, clubs français LDC
- Plan :
  - H2 À la une ;
  - H2 Résultats et prochains matchs ;
  - H2 Le parcours des clubs français ;
  - H2 Classement de la phase de ligue ;
  - H2 Où regarder ;
  - H2 FAQ (format de la compétition).

### 8. `/equipe-de-france/` — **H1 : Équipe de France : actu des Bleus, liste, matchs**
- Navigation · pilier · hebdo · P1
- KW : équipe de france | bleus, liste deschamps / sélectionneur (vérifier le sélectionneur en poste), prochain match équipe de france
- Plan : H2 À la une ; H2 Dernière liste ; H2 Prochains matchs et diffuseurs ; H2 Résultats récents ; H2 Joueurs à suivre.

### 9. `/ou-regarder/` — **H1 : Quel match de foot ce soir à la télé ? Le programme**
- Intention : transactionnelle / pratique · Type : programme · MAJ : quotidienne (auto) · P1
- KW : match ce soir | programme foot tv, foot à la télé, quelle chaîne
- Plan :
  - H2 Ce soir ;
  - H2 Demain ;
  - H2 Ce week-end ;
  - H2 Diffuseurs par compétition (H3 Ligue 1 · H3 Ligue des champions · H3 Équipe de France) ;
  - H2 FAQ.
- Éléments : les diffuseurs **à vérifier chaque saison**. Pas de liens vers des sites de streaming illégaux.

### 10. `/ou-regarder/ligue-1/` — **H1 : Ligue 1 : quelle chaîne diffuse les matchs ?**
- Pratique · guide + programme · chaque journée · P1
- KW : ligue 1 chaîne | diffuseur ligue 1, abonnement ligue 1
- Plan : H2 Les diffuseurs de la saison (sourcés) ; H2 Le programme de la journée ; H2 Prix des abonnements (sourcés, datés) ; H2 FAQ.

### 11. `/ou-regarder/ligue-des-champions/` — **H1 : Ligue des champions : sur quelle chaîne regarder les matchs ?**
- Pratique · P2 · Plan identique à la page précédente.

### 12. `/resultats/` — **H1 : Résultats foot en direct : scores du jour**
- Navigation · données en direct · auto · P1
- KW : résultats foot | score en direct, résultats du jour
- Plan : H2 En direct ; H2 Terminés aujourd’hui ; H2 Par compétition ; H2 Alertes but (inscription).
- Éléments : bandeau existant, réglage des sports, « vérifié à HH:MM ».

### 13. `/foot-amateur/` — **H1 : Foot amateur : résultats, actus et clubs de l’Est**
- Locale · pilier · hebdo · P1
- KW : foot amateur | résultats foot amateur, district, régional 1
- Plan :
  - H2 À la une ;
  - H2 Par ligue (H3 Bourgogne-Franche-Comté · H3 Grand Est) ;
  - H2 Coupe de France : le parcours des amateurs ;
  - H2 Envoyer un résultat / une info (formulaire) ;
  - H2 Clubs partenaires.
- Éléments : appel aux clubs pour envoyer leurs résultats (contenu original), lien vers l’offre club.

### 14. `/foot-amateur/bourgogne-franche-comte/` — **H1 : Foot amateur en Bourgogne-Franche-Comté**
- Locale · hub régional · hebdo · P2
- KW : foot bourgogne franche comté | district doubs, district territoire de belfort, R1 BFC (noms à vérifier sur le site de la ligue)
- Plan : H2 Actus ; H2 Résultats par district ; H2 Clubs ; H2 Agenda.

### 15. `/foot-amateur/grand-est/` — **H1 : Foot amateur dans le Grand Est**
- Même modèle · P2

### 16. `/clubs/fc-sochaux-montbeliard/` — **H1 : FC Sochaux-Montbéliard : actu, mercato, résultats**
- Locale / navigation · page club · auto + hebdo · P1
- KW : fc sochaux | sochaux actu, mercato sochaux, sochaux résultat
- Plan :
  - H2 Dernières infos ;
  - H2 Prochain match et diffuseur ;
  - H2 Résultats récents ;
  - H2 Mercato ;
  - H2 Le club en bref (H3 Stade · H3 Palmarès, sourcé) ;
  - H2 FAQ.

### 17. `/clubs/rc-strasbourg/` — **H1 : RC Strasbourg Alsace : actu, mercato, résultats** · même modèle · P1
### 18. `/clubs/fc-metz/` — **H1 : FC Metz : actu, mercato, résultats** · P2
### 19. `/clubs/as-nancy-lorraine/` — **H1 : AS Nancy Lorraine : actu, mercato, résultats** · P2
### 20. `/clubs/dijon-fco/` — **H1 : Dijon FCO : actu, mercato, résultats** · P2
### 21. `/clubs/psg/` — **H1 : PSG : actu, mercato, résultats** · forte concurrence, mais trafic fort · P2
### 22. `/clubs/om/` — **H1 : OM : actu, mercato, résultats** · P2
### 23. `/clubs/ol/` — **H1 : OL : actu, mercato, résultats** · P3

### 24. `/coupe-de-france/` — **H1 : Coupe de France : tirage, résultats et petits poucets**
- Navigation / locale · pilier · par tour · P2
- KW : coupe de france | tirage coupe de france, résultats coupe de france
- Plan : H2 Prochain tour (date, tirage) ; H2 Résultats ; H2 Les clubs amateurs de l’Est encore en lice ; H2 Où regarder.

### 25. `/comprendre/mercato-comment-ca-marche/` — **H1 : Comment fonctionne le mercato ? Le guide simple**
- Evergreen · guide · par saison · P1
- KW : comment marche le mercato | indemnité de transfert, clause libératoire, prêt avec option d’achat
- Plan : H2 Les fenêtres de transfert ; H2 Transfert, prêt, fin de contrat ; H2 Clauses ; H2 Qui négocie ; H2 Lexique ; H2 FAQ.

### 26. `/comprendre/regle-du-hors-jeu/` — **H1 : La règle du hors-jeu expliquée simplement**
- Evergreen · guide illustré · par saison · P2
- KW : hors-jeu règle | hors jeu explication, VAR hors-jeu
- Plan : H2 La règle (texte de l’IFAB, sourcé) ; H2 Exemples en schémas ; H2 Les exceptions ; H2 La VAR ; H2 FAQ.

### 27. `/comprendre/fair-play-financier/` — **H1 : Le fair-play financier et la DNCG, c’est quoi ?** · Evergreen · P3

### 28. `/pastille/` — **H1 : La Pastille TV : le JT foot en 2 minutes**
- Navigation / vidéo · hub vidéo · quotidienne · P1
- KW : jt foot | résumé actu foot vidéo
- Plan : H2 La Pastille du jour ; H2 Archives ; H2 Comment elle est faite (mention IA) ; H2 Devenir sponsor.
- Éléments : `VideoObject`, transcription, mention « générée avec IA ».

### 29. `/jeunes-talents/` (Pépite FC) — **H1 : Jeunes talents : les pépites du foot à suivre**
- Info / découverte · liste + articles · mensuelle · P3
- KW : jeunes talents foot | pépites ligue 1, wonderkid

### 30. `/ballon-dor/` — **H1 : Ballon d’Or : favoris, votes et palmarès**
- Événement + evergreen · pilier saisonnier · avant et après la cérémonie · P2
- KW : ballon d’or | favoris ballon d’or, palmarès ballon d’or
- Plan : H2 L’édition en cours (données vérifiées uniquement) ; H2 Palmarès ; H2 Comment fonctionne le vote ; H2 FAQ.

---
## 5. Ordre de création conseillé
1. **P1** :
   - Mercato, Officiels, Dates ;
   - Ligue 1, Classement ;
   - Ligue des champions ;
   - Équipe de France ;
   - Où regarder (×2) ;
   - Résultats ;
   - Foot amateur ;
   - Sochaux, Strasbourg ;
   - « Comment fonctionne le mercato » ;
   - Pastille.
2. **P2** : Calendrier, Où regarder LDC, les 2 hubs régionaux, Metz, Nancy, Dijon, PSG, OM, Coupe de France, Hors-jeu, Ballon d’Or.
3. **P3** : OL, fair-play financier, jeunes talents.

**Les règles de qualité :**
- Aucune page pilier ne se publie vide.
- Au moins 300 mots de contenu propre + des données + 5 liens internes.
- Toute donnée factuelle (palmarès, stade, diffuseur) a une source et une date.
