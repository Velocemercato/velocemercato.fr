# Audit international — Véloce Mercato
Date : 22 novembre 2026  
Périmètre : dépôt GitHub `Velocemercato/velocemercato.fr`, branche de travail `audit-international-2026-11-22`.  
Statut : audit statique du dépôt. Ce document ne certifie pas l'état du site en production.

## 1. Synthèse exécutive

Le projet dispose déjà d'une base riche : accueil avec métadonnées SEO et Open Graph, rubriques Foot / Multisport / Actus / Gaming / Mangas, articles, sitemap, workflows éditoriaux, La Pastille TV, VM Studio et préparation de contenus sociaux.

Le principal frein n'est pas l'absence d'idées ou de pages : c'est la **fiabilité opérationnelle vérifiée**, la **qualité éditoriale et l'indexation des nombreuses URL**, puis la transformation de la production automatisée en diffusion réellement publiée et mesurée.

## 2. Éléments confirmés dans le dépôt

- L'accueil déclare un canonical vers `https://velocemercato.fr/`, une description, Open Graph, une carte Twitter large et des alternates FR/EN.
- `robots.txt` autorise l'exploration générale et exclut les brouillons, démos et anciennes pages de statistiques publiques.
- `sitemap.xml` contient **1 709 URL** au moment de l'audit. Les dates observées vont du 15 octobre au 22 novembre 2026.
- Le sitemap contient de nombreuses URL d'articles de forme `/a/rss-v2-....html`. Leur valeur éditoriale, leur canonicalisation, leur indexabilité et leur éventuelle redondance doivent être contrôlées avant d'en accroître le nombre.
- Le workflow `actualites.yml` est planifié toutes les 20 minutes. Il dépend notamment du secret `ANTHROPIC_API_KEY`. Les étapes agenda, vidéos, fil express, actualité régionale et foot amateur sont facultatives et configurées en `continue-on-error`.
- Le workflow `reseaux.yml` prépare des formats verticaux et des textes pour les JT. Il ne prouve pas à lui seul une publication automatique sur Instagram, TikTok ou Facebook.
- La documentation de communication décrit des exports de contenus et un envoi Discord conditionné par un webhook. Elle précise que les autorisations YouTube/Twitch restent à connecter et qu'aucun upload réel n'a été confirmé dans l'environnement d'audit.
- VM Studio possède un Worker Cloudflare, des tests dédiés et un workflow de déploiement. Le déploiement nécessite des secrets GitHub Cloudflare appropriés. La documentation prévoit une clé Stripe de test et un verrou explicite avant l'activation d'une clé réelle.

## 3. Risques et points à vérifier

### Priorité critique — disponibilité et déploiements
1. Consulter les dernières exécutions GitHub Actions de chaque workflow : succès, échecs, durée, fréquence réelle, erreurs de quota et secrets absents.
2. Vérifier le domaine, les redirections HTTP/HTTPS, DNS, certificat, Cloudflare Pages et le Worker VM Studio depuis le tableau de bord réel.
3. Vérifier les parcours de commande du studio : demande, réception dans l'administration, suivi, email, paiement test, retour de paiement et idempotence.
4. Vérifier qu'une panne d'une étape facultative n'est pas confondue avec un JT ou une actualité publiée avec succès.

### Priorité haute — SEO et indexation
1. Examiner un échantillon représentatif des URL `/a/rss-v2-*.html` et des articles rédigés : contenu unique, attribution, sources, canonical, date, liens internes, absence de texte vide ou généré uniquement depuis un titre.
2. Séparer les pages utiles à l'indexation des archives techniques, brouillons, pages de recherche et doublons. Ne pas supprimer en masse les URL historiques sans analyse des redirections et du trafic.
3. Vérifier les pages anglaises : traduction réelle, cohérence des balises hreflang réciproques, canonical propre à chaque langue et navigation utilisable.
4. Vérifier les données structurées Article, Organization, Breadcrumb et VideoObject là où elles sont pertinentes, sans inventer de notes, d'auteurs ou de dates.
5. Vérifier la cohérence des liens internes entre Foot, Multisport, Actus, Gaming et Mangas. La rubrique Multisport doit rester distincte du contenu football.

### Priorité haute — publication et croissance
1. Distinguer clairement : contenu généré, contenu préparé, contenu programmé, contenu envoyé et contenu effectivement visible sur le compte social.
2. Connecter les comptes via les autorisations officielles, puis effectuer des essais privés ou en brouillon avant toute publication automatique.
3. Conserver une validation humaine pour les actualités sensibles, les partenariats, les contenus sponsorisés et les publications pouvant engager la marque.
4. Mettre en place un rapport hebdomadaire : articles publiés, erreurs, sources, vidéos prêtes/publiées, liens sociaux, visites par domaine et conversions.

## 4. Opportunités commerciales

- Construire une page annonceurs/partenaires avec formats, emplacements, exemples, contact et formulaire de brief.
- Préparer un kit média basé uniquement sur des statistiques réellement mesurées et datées.
- Développer des offres distinctes : sponsoring d'une rubrique, partenaire d'une émission, vidéo sponsorisée, test produit transparent, affiliation déclarée.
- Ajouter des appels à l'action cohérents dans les articles et émissions, sans transformer les pages éditoriales en panneaux publicitaires.
- Pour VM Studio, préparer un parcours commercial mesurable : demande reçue, qualification, devis, validation, paiement, livraison, avis client.

Aucun chiffre d'audience, partenariat, accord de marque ou résultat commercial n'est présumé dans cet audit.

## 5. Plan d'action recommandé

| Ordre | Action | Condition de validation |
|---|---|---|
| P0 | Audit des dernières exécutions Actions | Statuts et logs consultés, causes des échecs identifiées |
| P0 | Contrôle Cloudflare et domaines | HTTPS, redirections, Pages et Worker vérifiés |
| P0 | Test complet VM Studio en mode test | Demande, suivi, email et paiement test vérifiés |
| P1 | Audit qualité du sitemap et des articles | Échantillon contrôlé, doublons classés, aucun retrait massif |
| P1 | Vérification des pages EN et hreflang | Canonicals et liens linguistiques réciproques |
| P1 | Audit Multisport indépendant du Foot | Rubriques et flux éditoriaux séparés |
| P2 | Connexion publication sociale | Essais privés réussis, preuve de publication conservée |
| P2 | Kit média et page partenaires | Chiffres vérifiables, offres et mentions transparentes |

## 6. Limites de cet audit

- Le dépôt GitHub a été consulté ; cela ne prouve pas que la même révision est actuellement déployée sur le domaine.
- L'accès direct au site public et au DNS n'a pas pu être validé depuis cet environnement.
- Les exécutions récentes des workflows, les secrets, les comptes Cloudflare, Stripe, YouTube, Twitch, Meta, TikTok et les statistiques privées ne sont pas réputés accessibles sur la seule base du code.
- Aucun secret, DNS, paiement réel, compte social ou réglage de production n'a été modifié.
- Aucune publication publique n'a été déclenchée.

## 7. Décision de sécurité

Cette branche ne contient que le présent rapport. Elle n'altère pas `main` et ne déclenche pas de déploiement du site. Toute correction de code sera proposée dans une branche distincte, testée, puis soumise à validation avant fusion.
