# Audit des parcours VM — 22 novembre 2026

## Portée vérifiée

38 URL internes liées depuis les deux accueils : 29 sur Véloce Mercato, 9 sur VM Univers. Toutes ont répondu HTTP 200 pendant le contrôle. Aucune duplication d’identifiant HTML ni image sans attribut alt dans ces pages. Ces contrôles ne prouvent pas le fonctionnement des services tiers, de chaque article historique, des paiements ou des notifications hors navigateur.

Le contrôle automatique signale six ancres absentes du HTML initial de l’accueil Véloce. Le lien Foot a été testé dans le navigateur : il ouvre effectivement le volet de 20 actualités via JavaScript. Il ne faut donc pas traiter ce signal HTML comme une panne confirmée. Les autres anciennes ancres restent à examiner avant suppression.

## Corrections livrées dans le code

- Parcours public de création unifié : les boutons de VM Studio et VM Univers conduisent vers /creer/.
- Modèles artisan, restaurant et portfolio, personnalisables sans service distant.
- Bouton principal et lien modifiables, navigation de maquette, textes de section jusqu’à 1 600 caractères.
- Navigation mobile Modifier / Voir l’aperçu / Envoyer.
- Branchement du créateur public au service de composition, avec traitement explicite de ses erreurs et protection contre l’écrasement d’une retouche faite pendant une génération.
- Styles manga et relief ajoutés au schéma de création. Il s’agit de directions graphiques, pas d’un générateur d’applications métier ou de scènes 3D.
- Aperçu de l’atelier rafraîchi pendant les retouches manuelles ; brouillon local de l’atelier restaurable.
- VM Univers : liens directs vers les trois identifiants Facebook issus du registre de publication, retrait de liens répétés et du suivi Metricool sur l’accueil, suppression d’un compteur de projets figé et d’une promesse de prix en direct sur la maquette.

## Vérifications réalisées

- Tests Node de création, fournisseur, transmission et paiement exécutés avec succès en CI pour la révision 28d3b41f535578ccbfb58cd272053d3c5d2e98ad.
- Dans le navigateur public : chargement du modèle artisan, modification du nom et conservation après rechargement.
- Recherche « studio » sur VM Univers : les deux parcours correspondants sont trouvés.
- Volet Foot : ouverture et chargement d’actualités récentes confirmés.
- Alertes : page et liste de nouveautés chargées, sans activer d’abonnement de test.

## Blocages et limites restant à lever

1. **Déploiement du Worker VM Atelier bloqué.** Run GitHub 45068296084, job 137349300604 : Cloudflare refuse l’accès au service vm-atelier (« No access to the specified service »). Les tests ont réussi, la publication du Worker a échoué. Les corrections serveur sont enregistrées mais ne sont pas actives. La prérequête publique OPTIONS /api/studio/proposer renvoie encore 403. Corriger les accès Cloudflare existants pour le compte et le service concernés, puis relancer le déploiement. Ne pas déplacer les clients ou remplacer le stockage pour contourner ce problème.
2. **Paiement encore en mode test**, confirmé par /api/config. Aucun encaissement réel n’a été testé ou activé.
3. **Notifications hors navigateur non certifiées.** La page indique qu’elle fonctionne avec une page ouverte. Tester l’inscription, la réception et la désinscription sur appareils réels avant toute promesse de push permanent.
4. **Transmission finale réelle à contrôler** après publication serveur : réception dans l’administration, reprise des photos, du bouton et du lien, puis suivi client. Les tests actuels utilisent un stockage simulé ; aucune fausse commande de production n’a été créée pendant l’audit.
5. **Audit complet des archives et performance terrain à poursuivre.** Le périmètre de ce contrôle est celui des parcours d’accueil. Il ne couvre pas tous les articles historiques, toutes les tailles d’écran et tous les appareils.

## Critères de fermeture

Le projet commercial est prêt lorsque le Worker corrigé est publié, un brief réel produit une maquette, une retouche conserve les éléments existants, le projet et ses photos arrivent dans l’administration, le lien de suivi fonctionne, et le paiement choisi est vérifié. La notoriété internationale et les revenus ne sont pas des critères qu’un déploiement peut garantir.
