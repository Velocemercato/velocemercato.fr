# Accueils simplifiés — repères pour la relecture de Claude

## Véloce Mercato

L'accueil donne la priorité aux actualités foot, à une seule Pastille, aux réseaux et au lien vers VM Univers. Les routes Actus et Gaming restent immédiatement accessibles. Les filtres sont placés avec les articles ; quatre brèves s'affichent initialement sur téléphone, six sur ordinateur, puis le visiteur peut charger la suite ou ouvrir les archives.

Les scores, l'agenda, les vidéos de buts, les quiz, la presse, Arena et les coulisses restent accessibles dans « Matchs, scores et plus de foot ». Les anciens liens `/#videos`, `/#agenda`, `/#live` et `/#pastille` ouvrent ce volet automatiquement. Les scripts des vidéos officielles, de l'agenda et de la presse attendent son ouverture. Le partage est dans la section réseaux et ne recouvre plus les articles.

Le lecteur de la Pastille reste relié aux publications réelles. Sur l'accueil foot, une diffusion YouTube doit concerner le foot seul ; le programme groupé ne double plus le lecteur du JT foot. Sans lien public correspondant, le dernier extrait disponible reste affiché. Les scripts de production, les horaires et les autorisations YouTube n'ont pas été changés.

Fichiers : `assets/home-clarity.css`, `assets/home-navigation.js`, `index.html` et option de filtrage dans `assets/broadcast-feed.js`.

## VM Univers

L'accueil commence par une présentation courte, la recherche et un sélecteur de thème. Les six catégories sont repliées au départ ; une recherche ou un thème ouvre les résultats. Les 28 liens de projets restent identiques, avec deux projets à venir. Le logo, les visuels et la mention « Disponible courant juin 2027 » du detailing sont conservés. Le studio professionnel reste accessible directement ; les coulisses et le contact sont plus bas.

Les paramètres `q` et `theme`, les liens partagés, les deux modes de cartes et la navigation sans redirection de domaine sont préservés. Les réseaux du portail restent Facebook, Instagram et TikTok de Véloce Mercato, clairement identifiés en attendant les comptes VM Univers.

Fichiers : `assets/portal-clarity.css`, `assets/portal.js`, `index.html`.

## Validation

Navigation vérifiée en navigateur sur téléphone et ordinateur : lecture d'article, catégories et pagination, sélection et recherche combinées, remise à zéro, liens partagés, ouverture des rubriques secondaires, lecteur YouTube, QR de partage et accès professionnels. L'affichage a également été contrôlé à 320, 390, 768 et 1440 pixels. Les visuels existants restent utilisés.

Les captures locales à 390 pixels mesurent un accueil par défaut d'environ 3 200 pixels de hauteur pour Véloce (contre 8 500) et 2 500 pour VM (contre 8 000). Ces mesures décrivent le rangement du contenu, pas des statistiques d'audience ni une mesure de vitesse réseau. Les premiers titres d'articles sont accessibles dans le premier écran testé.

Les nouveaux fichiers CSS et les scripts modifiés ont des URL versionnées pour éviter qu'un ancien cache conserve les anciens contrôles. Aucun compteur de visiteurs public ni chiffre d'audience n'a été ajouté.
