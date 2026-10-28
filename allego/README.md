# Allego — prototype « Scanne avant d’acheter. »

Application web mobile pour vérifier un article d’occasion avant un achat entre particuliers.
Parcours complets : **AirPods**, **téléphone**, **baskets**. Les autres catégories (tablettes et ordinateurs,
consoles et électronique, vêtements, sacs de luxe, montres et bijoux, vélos et trottinettes, outils et autres objets)
existent dans la structure, avec des contrôles génériques et la liste honnête de ce qui manque.

## Lancer

Trois fichiers statiques, sans compilation ni serveur applicatif :

```bash
cd velocemercato.fr
python3 -m http.server 8000
# puis ouvrir http://localhost:8000/allego/
```

- Pour la **caméra sur un téléphone**, il faut une page servie en HTTPS (ou `localhost`). Une fois en ligne :
  `https://velocemercato.fr/allego/`.
- La lecture du texte (OCR) télécharge Tesseract.js depuis `cdn.jsdelivr.net` la première fois. Les images, elles,
  ne sont jamais envoyées.
- La page est en `noindex` : c’est un prototype.

## Parcours

1. Photographier (caméra, plusieurs photos), importer des images ou saisir une référence.
2. Confirmer la catégorie (proposée automatiquement), indiquer ce que montre chaque photo
   (produit, boîte, réglages, facture, annonce), puis corriger les caractères. Les caractères souvent confondus
   (0/O, 1/I, 5/S, 8/B…) sont surlignés.
3. Premiers indices : modèle identifié, tableau de comparaison entre les sources, lien vers la vérification officielle.
4. Checklist à remplir devant le vendeur ; les résultats se mettent à jour.

Trois résultats séparés, chacun avec ses constats, sa source, ses limites et ce qui reste à vérifier :

| Résultat | Statuts possibles |
|---|---|
| 1. Authenticité (cohérence du produit + indices de contrefaçon) | Indices cohérents · Anomalies détectées · Preuves insuffisantes |
| 2. Provenance | Document présenté et cohérent (non vérifié auprès de l’émetteur) · Document incohérent · Document non rapproché · Aucun document |
| 3. Signalement de vol | **Statut de vol non vérifiable** (toujours, faute de source autorisée connectée) |

Règle « Indices cohérents » : aucune anomalie, au moins un identifiant identique sur deux sources,
et au moins deux contrôles forts réussis devant le vendeur. C’est une règle explicite, pas un score :
aucun pourcentage n’est calculé.

## État réel des fonctions

### Opérationnel
- Caméra arrière, plusieurs photos, import d’images.
- Codes-barres : en direct via `BarcodeDetector` (Chrome Android…), sinon sur photo via ZXing (chargé à la demande).
- OCR sur l’appareil via Tesseract.js (chargé à la demande). Si le chargement échoue, saisie manuelle.
- Clé de contrôle des IMEI (Luhn) et des codes GS1 (EAN/UPC) ; conversion O→0, I→1… dans les champs numériques.
- Identification des AirPods par numéro A… (table locale `categories.js`, relevée d’après la page Apple
  « Identifier vos AirPods » ; **à revérifier**, AirPods Pro 3 non couverts).
- Repérage du modèle de téléphone (iPhone, Galaxy, Pixel) et de la marque de baskets dans le texte.
- Détection des écarts entre produit, boîte, réglages, annonce et facture (série, IMEI, référence, taille,
  capacité, génération), avec explication non accusatrice, action suivante et formulation pour le vendeur.
- Checklists : facture, correspondance des références, ouverture, jumelage, association à un ancien compte, etc.
- Aucune conservation : ni serveur, ni `localStorage`, ni cookies. Photos en mémoire (object URLs), effacées par
  « Tout effacer » ou à la fermeture de l’onglet.

### Laissé à l’utilisateur (rien n’est simulé)
- **Vérification officielle Apple** : bouton vers `checkcoverage.apple.com` et copie des numéros ; l’utilisateur
  indique ce que la page affiche (modèle correspondant, autre modèle, numéro invalide, **produit remplacé**, autre).
  Allego explique alors chaque cas : par exemple, « produit remplacé » ne prouve ni une contrefaçon ni un vol
  (échange en garantie, numéro de boîte, recopie, erreur de lecture).

### Nécessite une API ou un partenariat
- Interrogation automatique d’Apple ou d’autres fabricants (série, garantie, verrouillage d’activation).
- Identification d’un téléphone par l’IMEI : base TAC de la GSMA (sous licence).
- IMEI déclarés volés : GSMA Device Check ou opérateurs (accès professionnel).
- Vélos : fichier national des cycles identifiés, uniquement via un opérateur de marquage agréé.
- Fichiers de police ou d’assureurs : aucun accès public.
- Fiche produit à partir d’un code-barres : GS1 ou fournisseur commercial.
- Vérification d’une facture : partenariat avec les enseignes.
- Production : héberger Tesseract.js, ses données de langue et ZXing sur le site (aujourd’hui via jsDelivr).

### Nécessite un expert
- Baskets de valeur, sacs de luxe, montres, bijoux : Allego oriente vers une expertise, sans conclure.

### Données de démonstration
Trois scénarios **fictifs** (AirPods, téléphone, baskets), signalés par un bandeau jaune « DÉMONSTRATION » sur
chaque écran et dans le résumé copié. Numéros de série inventés (préfixe `DEM`) ; l’IMEI de démonstration est un
exemple public valide en format, sans lien avec un vrai appareil. Le scénario AirPods reproduit le cas
« numéro d’un produit remplacé ».

## Ajouter une catégorie
Ajouter un objet dans `categories.js` : `sources`, `fields` (avec leur `kind` : `serial`, `imei`, `gtin`, `size`…),
`keywords` pour la détection, `family()` pour l’identification du modèle, `checklist`, `official`, `unavailable`,
`expert`. Le moteur `app.js` est générique.

## Garde-fous de formulation
- Jamais « authentique » ni « non volé ». Un numéro valide peut être copié ; un code-barres identifie une référence.
- Sans registre accessible et fiable : « Statut de vol non vérifiable ».
- Un compte encore associé ne prouve pas un vol : il est présenté comme un point à régler avant de payer.
