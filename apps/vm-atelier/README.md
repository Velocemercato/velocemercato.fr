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
