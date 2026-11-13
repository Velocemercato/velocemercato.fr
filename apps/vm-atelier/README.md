# VM Studio (mode test)

Deux outils dans un seul Worker Cloudflare, sans serveur à gérer :

| Adresse | Pour qui | Ce que ça fait |
|---|---|---|
| `/studio` | le client | Il compose son site (nom, photo, couleurs, formule, options). **Le prix monte en direct**, il voit l'aperçu, puis envoie sa demande (panier). Rien n'est payé : Romain valide puis envoie un lien de paiement Stripe. |
| `/admin` | Romain | Liste des commandes, projets, éditeur par blocs (titre + photo, texte, image, galerie, produits, bouton, contact). |
| `/salon/<lien>` | le client, en face de Romain | **Mode salon** : le téléphone du client affiche le site pendant que Romain le construit (mise à jour en 1 à 2 s). |
| `/voir` | le client | Consultation avec **code à usage unique** : le code ne marche qu'une fois ; fermer ou recharger la page met fin à l'accès. |

## Tarifs
Dans `src/prix.js`. Le serveur recalcule toujours le total (un prix modifié dans le navigateur est ignoré).

## Mise en ligne (après accord de Romain)
1. `npm ci && npx wrangler deploy`
2. Cloudflare → Workers & Pages → **vm-atelier** → Paramètres → Variables et secrets : ajouter le secret **ADMIN_TOKEN** (code de l'atelier).
3. Facultatif : remplir `CONTACT_EMAIL` et `CONTACT_TEL` dans `wrangler.toml` (affichés sur le studio).

## Sécurité
Codes à usage unique : seul le condensat SHA-256 est stocké, consommation atomique (8 essais simultanés → 1 seul succès), 10 essais par heure et par IP. Liens salon : jeton aléatoire de 24 caractères, révocable. Textes insérés sans HTML, liens limités à https / mailto / tel. Requêtes d'écriture refusées si elles viennent d'un autre site.

## Limites honnêtes
Une capture d'écran reste toujours possible. Les créations IA (logo, voix, vidéo, musique, 3D) sont vendues comme options mais réalisées à part pour l'instant.

## Lot 1 — Assistant IA, formats print et retours client (13/11/2026)

- **Assistant IA** (`src/ia.js`) : Romain écrit une consigne (« photo à gauche, titre plus grand »). L'IA (Claude, SDK officiel `@anthropic-ai/sdk`, sortie JSON validée par Zod) renvoie une **proposition** : elle s'affiche dans l'aperçu de Romain seulement, puis **Appliquer** / **Refuser** / **↶ Annuler**. Les photos ne sont jamais envoyées à l'IA (repères IMG_1…). Plafond d'appels par jour (`IA_MAX_JOUR`, 40 par défaut), journal sans secret, pas de relance automatique.
- **Réglages Cloudflare** (saisis par Romain) : secret `ANTHROPIC_API_KEY` (obligatoire), variables facultatives `ANTHROPIC_MODEL` (défaut `claude-opus-5-5`) et `IA_MAX_JOUR`. Sans clé : « IA à connecter », aucune réussite simulée.
- **Formats** : site, carte de visite 85×55 mm (recto/verso), flyer A5, affiche A3, post carré, story 9:16. Le bloc « 📄 Nouvelle page / verso » sépare les pages. Bouton **🖨 Imprimer / PDF** au bon format.
- **Retours client en direct** : sur son lien « salon », le client touche un élément et écrit sa demande. Romain la reçoit dans l'atelier en 3 s maximum et peut l'envoyer à l'IA en un clic.
- **Version** : un enregistrement fait sur une version périmée est refusé (409 `projet_modifie`).

Tests : `node tests/ia.test.mjs` (21 cas, Claude et Gemini, réponses d'Anthropic simulées, aucun appel payant) et `node tests/lot1.test.cjs` (13 vérifications navigateur, Romain + client simultanés, avec une fausse IA locale via `ANTHROPIC_BASE_URL`).

### Mise à jour du 13/11 (suite)
- **Deux fournisseurs d'IA** : Claude (`ANTHROPIC_API_KEY`) ou **Gemini, offre gratuite de Google AI Studio** (`GEMINI_API_KEY`, modèle `GEMINI_MODEL`, défaut `gemini-flash-latest`). `IA_FOURNISSEUR=claude|gemini` force le choix ; sinon Claude s'il est configuré, puis Gemini.
- **Liens clients sur le domaine VM vérifié uniquement** : `https://atelier.velocemercato.fr` (salon, code unique). L'adresse technique `*.workers.dev` redirige en 301 vers ce domaine.
- **Option payante pour le client** : « Retouches en direct avec l'assistant IA (30 jours) », 29 €, pour que le coût de l'IA soit couvert par le client.

## Lot 3 — Paiement Stripe (mode test)
- Atelier → Commandes → **💳 Créer le lien de paiement** : session Stripe Checkout créée côté serveur avec les lignes et prix du devis enregistré (centimes entiers ; aucun montant venant du navigateur).
- Le client voit **« 💳 Payer X € »** sur son lien de suivi ; après paiement, la page `/paiement/retour` **interroge Stripe** (payment_status `paid`) avant de passer la commande en « payée » (idempotent). Visiter la page sans payer ne valide rien.
- Secret Cloudflare : `STRIPE_SECRET_KEY` (clé **de test** `sk_test_…` ou restreinte `rk_test_…`). Une clé réelle est **refusée** tant que la variable `STRIPE_REEL=oui` n'est pas ajoutée après l'accord écrit de Romain.
- Tests : `tests/paiement.test.mjs` (10) et `tests/lot3.test.cjs` (9, faux Stripe local via `STRIPE_BASE_URL`).

## Lot 2 — Lien client (« 🔑 Créer le lien client »)

Depuis l'atelier, bouton **🔑 Créer le lien client** :
- **Version** : *figée* (le client voit l'instantané du moment) ou *en cours* (il voit les modifications en direct).
- **Ouvertures** : *1 seule* (le code est consommé par le premier appareil, un 2ᵉ navigateur est refusé) ou *plusieurs*.
- **Durée de session** : 15 min, 1 h ou 24 h ; **validité** du code : 1, 7 ou 30 jours.
- Copier le lien / le code / le message tout prêt, ou 📤 Partager (téléphone).
- Liste des codes avec état (actif, utilisé, expiré, révoqué) et bouton **Révoquer** (ferme aussi les sessions ouvertes).

Côté client (`/voir`) : session conservée au rechargement, compte à rebours, bouton « Fermer l'aperçu ».
Les robots d'aperçu (HEAD/GET sans saisie) ne consomment pas le code ; anti-force brute sur les échecs seulement ;
ouverture atomique (8 tentatives simultanées → 1 seule acceptée).

Tests : `tests/lot2.test.cjs` (12 vérifications).

## Visuels seuls + vérification avant envoi + page de présentation

- `/` est la **page de présentation** publique (indexée, `robots.txt` + `sitemap.xml`), avec exemples rendus en direct.
- `/studio` : le client choisit **Site, Carte de visite (recto-verso ou relief), Flyer A5, Affiche A3, Publication carrée, Story**
  (`/studio?p=carte` ouvre directement le bon produit). L'aperçu au bon format se met à jour en direct et reste collé
  en haut de l'écran sur téléphone (⤢ Agrandir).
- « 👀 Vérifier avant d'envoyer » ouvre le récapitulatif (visuel + prix exact) ; rien ne part sans « ✅ C'est bon, j'envoie ».
- Prix des visuels dans `src/prix.js` (`PRIX.produits`) ; options possibles : logo, retouches IA. Le serveur recalcule le
  total et impose le format du produit.
- Tests : `tests/visuels.test.cjs` (21 vérifications, dont 24 affichages 320/390/768/1300 px sans débordement).
