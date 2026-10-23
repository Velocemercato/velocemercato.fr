# Visuels intégrés des démonstrations VM

Les visuels sont créés et intégrés directement dans les modèles : les 74 demandés, puis les 19 compléments de la nouvelle démo caviste. Aucun téléchargement manuel n’est nécessaire pour les afficher. Le registre `demos/img/catalogue.json` fait correspondre les noms demandés aux chemins utilisés dans les sites.

Voir [la note de reprise pour Claude](CLAUDE_REPRISE_DEMOS_IMAGES.md) pour les fichiers, le rangement et les vérifications. Les descriptions ci-dessous restent le brief de référence pour les prochains visuels. Les emplacements de vidéos, portraits d’équipe et avant/après non fournis restent identifiés comme exemples à compléter avec les contenus du futur client.

## Style commun (à coller avant chaque description)

> Photo réaliste de qualité professionnelle, lumière naturelle chaleureuse, couleurs vives, cadrage publicitaire, aucun texte, aucun logo de marque existante, aucune personne célèbre. Petite touche d'univers manga : légers traits de vitesse ou reflets dynamiques discrets en arrière-plan.

Formats :
- **Héros** (grande image en haut) : portrait 4:5, 1200 × 1500 px.
- **Cartes** (prestations, produits, équipe) : paysage 16:10, 1200 × 750 px.
- **Galerie** : carré 1:1, 1200 × 1200 px.
- **Affiches de vidéos** (`video-poster`) : paysage 16:9, 1600 × 900 px.

## Priorité 1 : une image héros par page (7 images)

| Fichier | Description |
|---|---|
| `demos/img/coiffeur/hero.webp` | Intérieur d'un salon de coiffure barber moderne, fauteuils noirs, néons jaunes, un coiffeur fait un dégradé à un client. |
| `demos/img/beaute/hero.webp` | Cabine d'institut de beauté zen, tons rose poudré et blanc, fleurs de cerisier, table de massage avec serviettes roulées. |
| `demos/img/restaurant/hero.webp` | Salle de bistrot français chaleureuse le soir, tables en bois dressées, assiette de viande et frites maison au premier plan. |
| `demos/img/snack/hero.webp` | Tacos XXL gratiné coupé en deux, fromage qui coule, frites, sur un comptoir de snack avec néons orange. |
| `demos/img/artisan/hero.webp` | Équipe du bâtiment en tenue de sécurité sur un chantier de rénovation de maison, échafaudage, lumière de fin de journée. |
| `demos/img/drive/hero.webp` | Employée souriante qui charge des sacs de courses dans le coffre d'une voiture au point de retrait d'une épicerie, cagettes de fruits. |
| `demos/img/cbd/hero.webp` | Boutique CBD moderne et lumineuse, étagères en bois clair avec flacons ambrés et bocaux, plantes vertes, ambiance calme et sérieuse (aucune fumée, aucune personne qui consomme). |
| `demos/img/caviste/hero.webp` | Cave à vin de quartier chaleureuse, murs de bouteilles en bois, comptoir de dégustation, lumière dorée, aucune personne en train de boire. |
| `demos/img/investir/hero.webp` | Illustration style manga dynamique : un jeune entrepreneur devant un mur d'écrans de téléphone montrant des sites de commerces, éclairs jaunes et bleus, ambiance énergique. |

## Priorité 2 : galeries (5 images par site, carrées)

| Fichier | Description |
|---|---|
| `coiffeur/galerie-1` à `-5` | 1 dégradé américain vu de profil · 2 taille de barbe au rasoir · 3 balayage blond sur cheveux longs · 4 carré plongeant · 5 couleur vive rose ou bleue. |
| `beaute/galerie-1` à `-5` | 1 cabine de massage tamisée · 2 ongles nail art pastel · 3 soin du visage avec masque · 4 rehaussement de cils en gros plan · 5 accueil de l'institut avec plantes. |
| `restaurant/galerie-1` à `-5` | 1 pièce de bœuf tranchée · 2 dos de cabillaud au beurre blanc · 3 moelleux au chocolat coulant · 4 terrasse en été · 5 chef qui dresse une assiette. |
| `snack/galerie-1` à `-5` | 1 tacos gratiné · 2 kebab en galette · 3 pizza qui sort du four à bois · 4 smash burger double cheddar · 5 cornet de frites maison. |

Les fichiers vont dans `demos/img/<site>/galerie-N.webp`.

## Priorité 3 : cartes (prestations, produits, équipe)

**Coiffeur** (`demos/img/coiffeur/`)
- `svc-coupe-homme` coupe homme aux ciseaux · `svc-degrade` dégradé tondeuse · `svc-barbe` barbe et serviette chaude · `svc-enfant` enfant souriant au salon · `svc-coupe-femme` coupe femme · `svc-brushing` brushing volume · `svc-couleur` application de couleur au pinceau · `svc-balayage` balayage effet soleil · `svc-soin` soin profond au bac.
- Équipe (personnes fictives, de face, souriantes) : `equipe-ryo` barber barbu tatoué · `equipe-lina` coloriste aux cheveux colorés · `equipe-sam` coiffeur visagiste.

**Institut** (`demos/img/beaute/`)
- `svc-massage` massage du dos à l'huile · `svc-pierres` pierres chaudes sur le dos · `svc-dos` massage express · `svc-visage` soin éclat · `svc-cils` cils recourbés · `svc-sourcils` sourcils restructurés · `svc-semi` vernis semi-permanent · `svc-nailart` nail art · `svc-jambes` épilation des jambes à la cire (pudique) · `svc-maillot` pot de cire et spatule (sans corps).
- `carte-cadeau` carte cadeau rose avec ruban · `duo` deux tables de massage côte à côte · `abonnement` coffret de soins élégant.

**Snack** (`demos/img/snack/`), photo du produit sur fond sombre :
- `tacos`, `kebab`, `burger`, `chicken` (burger poulet pané), `pizza-margherita`, `pizza-orientale`, `pizza-turbo` (crème, poulet, cheddar), `frites`, `tenders`, `canette` (canette sans marque), `tiramisu`.

**Restaurant** (`demos/img/restaurant/`)
- `plat-du-jour` blanquette de veau dans une assiette creuse, vue de dessus.

**Artisan** (`demos/img/artisan/`)
- Métiers : `metier-renovation` salle de bain en travaux · `metier-maconnerie` mur de parpaings en construction · `metier-toiture` couvreur sur un toit · `metier-industrie` dalle béton dans un entrepôt.
- Avant / après (même angle de vue sur les deux images) : `sdb-avant` / `sdb-apres` salle de bain vieillotte puis moderne · `facade-avant` / `facade-apres` façade grise abîmée puis ravalée · `atelier-avant` / `atelier-apres` atelier industriel vide et sale puis rénové.

**Boutique CBD** (`demos/img/cbd/`), produit seul sur fond clair, sans marque, sans fumée, sans feuille de cannabis stylisée :
- `huile-5`, `huile-10`, `huile-20` (flacons pipette ambrés de tailles différentes), `infusion` (sachet kraft et tasse), `fleur-lemon` et `fleur-berry` (fleurs séchées dans un bocal en verre), `baume`, `creme`, `sels`, `coffret`, `boite`.
- Galerie `galerie-1` à `-5` : espace boutique, rayon des huiles, rayon des infusions, analyse de laboratoire sur une tablette, conseiller qui renseigne un client.

**Caviste** (`demos/img/caviste/`), bouteille seule sur fond clair, étiquette vierge, sans marque :
- `rouge-cdr`, `rouge-bourgogne`, `blanc-riesling`, `blanc-jura`, `rose-provence`, `cremant`, `biere-blonde`, `biere-ipa`, `whisky`, `rhum`, `sans-alcool-rouge`, `sans-alcool-biere`, `coffret`.
- Galerie `galerie-1` à `-5` : rayons de vins, bières artisanales, spiritueux, coffrets cadeaux, caviste qui conseille.
- Règle : pas de personne en train de boire, pas de scène festive (loi Évin).

**Drive** (`demos/img/drive/`), produit seul sur fond blanc, sans marque visible :
- `pommes`, `carottes`, `bananes`, `salade`, `lait`, `oeufs`, `comte`, `yaourts`, `baguette`, `croissants`, `poulet`, `steaks`, `pates`, `riz`, `cafe`, `eau`, `jus`, `papier`, `lessive`.

## Vidéos (facultatif)

Chaque page prévoit une vidéo de présentation (`video.mp4`, son affiche `video-poster.webp`) et 3 vidéos courtes verticales (`reel-1.mp4` à `reel-3.mp4`). ChatGPT ne fait que des images. Pour les vidéos, trois solutions :

1. Les **filmer chez un vrai client** (c'est le pack photo/vidéo que tu vends).
2. Les générer avec un outil vidéo (Sora, par exemple) à partir des mêmes descriptions.
3. Ne rien faire : la démo affiche « Vidéo à venir » proprement.

Pour les affiches `video-poster.webp`, demande à ChatGPT la même scène que la vidéo, au format 16:9.

## Règles importantes

- **Ne jamais** utiliser de vraies photos d'un commerce ou d'une personne sans leur accord.
- Pas de logo ni de marque existante (Coca-Cola, McDonald's…) sur les produits.
- Les démos restent marquées « site de démonstration, entreprise fictive ».
