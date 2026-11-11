# VM Prono — étape 1 (mode test)
En ligne : https://vm-prono.velocemercato87.workers.dev (non référencé). Espace Romain : `/admin`.

- Conseils **publics** et **VIP** saisis et validés par Romain : rien n'est généré automatiquement.
- **Invitations VIP à usage unique**, valables 14 jours. Seul le condensat SHA-256 est stocké, et la consommation est atomique (Durable Object SQLite).
- **Un seul appareil actif par membre.** « Nouveau téléphone » génère une nouvelle invitation, et l'ancienne session tombe à l'activation. La révocation est immédiate.
- **Sécurité :**
  - cookies `HttpOnly`, `Secure`, `SameSite=Strict` ;
  - contrôle d'origine sur chaque POST (CSRF) ;
  - 10 tentatives d'activation par IP et par heure ;
  - en-têtes CSP, `nosniff` et `DENY` ;
  - aucun contenu VIP sans session.
- **Administration :** secret `ADMIN_TOKEN`, défini par Romain dans Cloudflare (Workers → vm-prono → Paramètres → Variables et secrets). Il n'est jamais dans ce dépôt.

## Vérifié en local (wrangler dev) le 11/11/2026
Admin protégé, mauvais code refusé, POST d'une autre origine refusé, public sans contenu VIP, VIP refusé sans session, **8 activations simultanées d'un même code → 1 seule réussie**, code réutilisé refusé, nouveau téléphone (l'ancien appareil perd l'accès), révocation immédiate, limitation des tentatives (429).

## Étapes suivantes
- Notifications (OneSignal) : un nouveau conseil prévient les abonnés ; le push VIP dit seulement « nouveau conseil disponible ».
- Rapprochement avec un match suivi (scores en direct) et cartes visuelles VM.
- Adresse personnalisée (prono.velocemercato.fr), puis lien depuis le pouf du bureau, une fois validé.

Déploiement : `CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=… npx wrangler deploy` depuis ce dossier.
