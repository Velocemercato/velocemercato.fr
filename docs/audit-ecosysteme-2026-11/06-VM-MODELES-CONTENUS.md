# 06 — Véloce Mercato : les 14 modèles de contenus

Les exemples utilisent des **noms fictifs** (FC Exemple, Joueur X) : aucun fait réel n’est inventé.

## Règles communes à tous les modèles
- **Title** : 50 à 60 caractères, le mot-clé au début, « – Véloce Mercato » à la fin.
- **Meta description** : 140 à 155 caractères, le fait principal plus ce que le lecteur va apprendre.
- **H1** unique, identique ou très proche du title.
- **Chapô** (1 à 2 phrases) qui répond tout de suite : qui, quoi, quand.
- **Signature** : auteur (lien vers `/redaction/[auteur]/`) + « Publié le JJ/MM/AAAA à HH:MM » + « Mis à jour le… » si besoin.
- **Étiquette de statut** pour le mercato : 🟢 Officiel · 🟡 En discussion · ⚪ Rumeur.
- **Bloc source** : « Source : [Média / communiqué] (lien) ». La source primaire passe en premier.
- **Mention IA** si l’IA a été utilisée : « Rédigé avec l’aide d’un outil d’IA à partir des sources citées, vérifié par la rédaction. »
- **Image** : uniquement des visuels VM, libres de droits ou sous licence. Alt descriptif. Une image de partage spécifique à chaque article.
- **Maillage** : 1 lien vers la page pilier, 1 bloc « À lire aussi » (3 liens), 1 appel vers la newsletter ou les alertes.
- **Données structurées** : `NewsArticle` (headline, datePublished, dateModified, author `Person`, publisher, image) + `BreadcrumbList`.

---

## 1. Article d’actualité football
**Structure**
- H1 : [Sujet] : [fait principal]
- Chapô
- H2 Ce qu’il faut savoir (3 puces)
- H2 Le contexte
- H2 Ce que ça change pour [club / compétition]
- H2 La suite (prochaine échéance)
- Bloc source · À lire aussi · Newsletter

**Obligatoire** : chapô, source, contexte, date, auteur. **Facultatif** : citation (avec source), tweet officiel intégré, mini-stats.

**SEO** : le mot-clé dans le H1, le chapô et un H2. 300 à 600 mots. **Sources** : au moins 1 source fiable ; 2 si l’info est sensible (blessure, conflit). **MAJ** : ajouter « Mis à jour : … » en tête et ne pas changer l’URL. **Maillage** : page club et page compétition.

**Exemple**
> **H1 : FC Exemple : Joueur X forfait pour le prochain match**
> *Le FC Exemple a annoncé ce mardi que Joueur X ne participera pas à la rencontre de samedi, selon le communiqué officiel du club.*
> **Ce qu’il faut savoir**
> • L’absence est confirmée par le club.
> • La durée d’indisponibilité n’est pas précisée.
> • Le prochain match a lieu samedi.
> **Le contexte** — Joueur X a disputé [nombre à vérifier] matchs cette saison…
> **Source : communiqué du FC Exemple (lien).**

## 2. Article mercato (rumeur ou en discussion)
**Structure**
- H1 : [Club] : [Joueur] [verbe prudent : « pisté », « proche de »]
- Étiquette ⚪ / 🟡
- Chapô avec « selon [média] »
- H2 Ce que l’on sait
- H2 Ce qui n’est pas confirmé
- H2 Le profil du joueur
- H2 Ce que ça changerait pour [club]
- H2 Notre avis : probabilité (faible / moyenne / forte), avec sa justification

**Règles** :
- jamais « officiel » sans communiqué ;
- toujours nommer le média d’origine ;
- pas de montant sans source ;
- conditionnel obligatoire.

**Schema** : `NewsArticle`.

**Exemple**
> **H1 : FC Exemple : Joueur Y dans le viseur pour cet hiver** · ⚪ Rumeur
> *Selon [Média], le FC Exemple s’intéresse à Joueur Y. Aucune des deux parties n’a confirmé.*
> **Ce qui n’est pas confirmé** : le montant, l’accord du joueur, le calendrier.

## 3. Transfert officiel
**Structure**
- H1 : Officiel : [Joueur] rejoint [Club]
- 🟢 Officiel
- Chapô
- Encadré **fiche transfert** (joueur, de, vers, type, durée, montant « non communiqué » si absent, source officielle)
- H2 Pourquoi ce transfert
- H2 Son profil
- H2 L’historique de ce dossier sur VM (liens vers les rumeurs précédentes)

**Règle** : lien vers le communiqué officiel **obligatoire**. Mettre à jour les anciennes rumeurs VM avec « ✅ Confirmé le … » et un lien vers l’officiel. **Maillage** : `/mercato/officiels/`, la page club, la page joueur si elle existe.

## 4. Page match
**URL** : `/match/AAAA-MM-JJ-equipe-a-equipe-b/` (une seule URL par match).

**Structure**
- H1 : [A] – [B] : heure, chaîne, compos et score
- H2 Infos pratiques (date, heure, stade, compétition, **diffuseur**)
- H2 Les enjeux
- H2 Forme des équipes (5 derniers résultats)
- H2 Compositions probables (si la source est fiable, sinon le bloc est retiré)
- H2 Score en direct
- H2 Résumé et buteurs (après le match)
- H2 FAQ (« à quelle heure ? », « sur quelle chaîne ? »)

**Schema** : `SportsEvent` (name, startDate, location, homeTeam, awayTeam, eventStatus). **MAJ** : J-2 (création), J (score), J+1 (résumé). **Interdit** : liens de streaming illégaux et cotes.

**Exemple (avant le match)**
> **H1 : FC Exemple – AS Modèle : heure, chaîne et enjeux**
> *Le FC Exemple reçoit l’AS Modèle samedi à [heure à vérifier], en [compétition]. Match diffusé sur [diffuseur à vérifier].*

## 5. Page club
**Structure**
- H1 : [Club] : actu, mercato, résultats
- H2 Dernières infos (10, automatiques)
- H2 Prochain match et diffuseur
- H2 Résultats récents
- H2 Mercato du club (officiels / rumeurs)
- H2 Le club en bref (stade, fondation, palmarès : tout est sourcé et daté)
- H2 FAQ

**Schema** : `SportsTeam` + `BreadcrumbList`. **MAJ** : automatique pour les listes, la partie fixe une fois par saison.

## 6. Page joueur
**À créer** seulement à partir de 5 articles VM sur le joueur.

**Structure**
- H1 : [Joueur] : actu, mercato et parcours
- Encadré fiche (poste, club actuel, nationalité, date de naissance : sourcés)
- H2 Dernières infos
- H2 Mercato : historique VM
- H2 Parcours
- H2 FAQ

**Schema** : `Person` (name, affiliation). Ne jamais publier de vie privée.

## 7. Page compétition
**Structure**
- H1 : [Compétition] : actu, classement, résultats
- H2 À la une
- H2 Classement
- H2 Résultats et calendrier
- H2 Où regarder
- H2 Format de la compétition (evergreen)
- H2 FAQ

**Schema** : `SportsEvent` pour les matchs listés, `BreadcrumbList`.

## 8. Page « Où regarder le match »
**Structure**
- H1 : [A] – [B] : sur quelle chaîne et à quelle heure ?
- Réponse en 1 phrase dès le chapô
- H2 Chaîne et horaire
- H2 Regarder sur mobile ou ordinateur (offres légales du diffuseur)
- H2 Les autres matchs du jour
- H2 FAQ

**Règles** :
- diffuseur **vérifié** auprès du diffuseur ou de la ligue ;
- date de vérification affichée ;
- jamais de lien illégal.

## 9. Page FAQ (thématique)
**Structure**
- H1 : [Sujet] : les questions les plus posées
- H2 par question (phrase entière) ; réponse de 40 à 80 mots, puis lien vers la page détaillée

**Schema** : `FAQPage`. **Sources** : règlements officiels (IFAB, FIFA, LFP).

## 10. Article vidéo / La Pastille TV
**Structure**
- H1 : La Pastille du [date] : [3 sujets]
- Vidéo avec image de prévisualisation, chargée au clic
- Mention « 🎙️ Vidéo réalisée avec des outils d’IA (voix et montage) à partir des articles cités »
- H2 Les sujets du jour (1 paragraphe et 1 lien par sujet)
- H2 Transcription (sous-titres `.vtt`)
- Encadré **sponsor** : « La Pastille est présentée par [Sponsor] (partenariat) », si sponsorisée

**Schema** : `VideoObject` (name, description, thumbnailUrl, uploadDate, duration, contentUrl).

## 11. Brève d’actualité
**Structure**
- H1 court
- 2 à 4 phrases
- 1 puce « Ce que ça change »
- Source
- Lien vers la page pilier

**Règle anti-contenu fin** : une brève doit apporter au moins 1 élément de plus que la source (contexte, conséquence ou lien utile). Sinon, la regrouper dans un article « L’essentiel du jour ».

## 12. Dossier de fond
**Structure**
- H1 : [Question ou angle fort]
- Chapô
- Sommaire
- H2 ×4 à 6 (une partie par idée)
- H2 Nos sources
- H2 Ce qu’il faut retenir

1 200 à 2 500 mots, des données sourcées, des graphiques créés par VM. **E-E-A-T** : la méthode est expliquée et l’auteur signe. **Exemple d’angles** : « Les centres de formation de l’Est : qui fait jouer ses jeunes ? », « Foot amateur : combien coûte une saison pour un club de district ? » (avec des données à collecter).

## 13. Article partenaire sponsorisé
**Structure**
- Bandeau en haut : **« CONTENU SPONSORISÉ — Article réalisé en partenariat avec [Marque] »**
- H1
- Chapô
- H2 ×3
- Encadré « À propos de [Marque] »
- Liens en `rel="sponsored"`

**Règles** :
- pas de faux avis ;
- pas de produit interdit aux mineurs ;
- pas d’opérateur de paris sans agrément ANJ ;
- l’étiquette reste visible sur les réseaux (« #partenariat » ou outil « Partenariat rémunéré »).

**Schema** : `Article` (pas `NewsArticle`).

## 14. Page de correction ou mise à jour
**Dans l’article corrigé**, juste sous le chapô :
> **Correctif du [date] :** une version précédente indiquait [erreur]. Il fallait lire [correction]. Merci à [lecteur, s’il est d’accord] pour le signalement.

**Sur `/sources-et-corrections/`**, dans le tableau « Corrections récentes » : date · article (lien) · nature de la correction.

**Règles** : ne jamais supprimer un article erroné sans explication ; mettre à jour `dateModified`.
