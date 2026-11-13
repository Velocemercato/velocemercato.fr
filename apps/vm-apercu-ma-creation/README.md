# Aperçu client Ma Création

Worker séparé ; aucune modification des projets Pages, des DNS, de VM Atelier ou des pages publiques existantes.

La maquette est chiffrée (AES-256-GCM) avant dépôt. Le dépôt public ne contient que le contenu chiffré et les condensats des capacités de consultation. Les liens de consultation et clés de déchiffrement ne doivent jamais être committés ni écrits dans les journaux.

Le lien contient une capacité aléatoire de 256 bits dans le fragment URL, absent des requêtes GET et des aperçus de messagerie. Seul le bouton Découvrir déclenche une requête POST authentifiée. Un Durable Object démarre alors, atomiquement, une fenêtre globale de 24 heures. Une réouverture ne la prolonge pas. Les accès suivants sont refusés en HTTP 410 à l’expiration. La page ouverte retire également l’aperçu à l’expiration.

Cette protection ne peut pas empêcher un visiteur autorisé de faire des captures ou de sauvegarder ce qu’il a déjà reçu. Elle contrôle les nouvelles consultations, pas les copies conservées.

Les accès de contrôle qualité et de test de sécurité sont indépendants du lien destiné à la cliente. Tester ces accès ne démarre pas sa fenêtre.

Tests : `node --test tests.mjs`. Déploiement : `npx --yes wrangler@4 deploy --config wrangler.toml`. Les secrets Cloudflare restent uniquement dans GitHub Actions.
