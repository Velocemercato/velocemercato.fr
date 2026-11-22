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


## 8. Contrôle Metricool — instantané du 22 novembre 2026

Une lecture non destructive de Metricool a identifié une seule marque accessible, libellée `velocemercato`, avec fuseau `Europe/Paris`. Les connexions mélangent plusieurs univers : site web `vmunivers.fr`, Instagram et Threads `vmunivers.fr`, TikTok `velocemercato`, chaîne YouTube Véloce Mercato et Twitch. Cette configuration ne permet pas de considérer les statistiques agrégées comme un kit média fiable pour l'un ou l'autre site.

Aucune publication planifiée n'a été retournée pour cette marque entre le 22 et le 25 novembre 2026. Cela concerne le calendrier Metricool interrogé, pas nécessairement d'autres systèmes de publication.

Les métriques disponibles sont partielles et hétérogènes selon les réseaux. Elles ne doivent pas être additionnées entre plateformes ni présentées comme audience globale. Les valeurs brutes ne sont pas utilisées comme preuve d'audience commerciale.

**Action recommandée :** créer ou sélectionner des marques Metricool distinctes pour VM Univers et Véloce Mercato, rattacher chaque réseau au bon projet, vérifier les permissions, puis établir un tableau de bord séparé. Avant toute programmation, confirmer les contenus, les médias et le calendrier éditorial. Aucune publication n'a été créée ou envoyée pendant cet audit.


## 9. Contrôle approfondi des articles — dépôt consulté le 23 novembre 2026

- `articles.json` contient 50 brèves au moment du contrôle.
- Les dates `publishedAt` vont du 22 novembre 2026 à 05:12 UTC au 22 novembre 2026 à 22:04 UTC : le lot présent dans le dépôt est donc récent à cet instant.
- Répartition des sources dans ce lot : Foot Mercato 20, BBC Sport 13, Foot01 6, RMC Sport 5, Foot National 4, Foot Amateur 2.
- Huit pages d'articles ont été contrôlées par échantillonnage. Elles disposent d'un titre, d'une description, d'un canonical propre, d'un H1 et d'une attribution de source. Le volume extrait se situe autour de 277 à 332 mots selon la page.
- Aucun titre strictement identique n'a été détecté parmi les 50 articles. Deux articles autour du même match Inter–Atalanta ont toutefois des angles distincts (résultat du match et triplé de Pio Esposito) : cela mérite une vigilance éditoriale pour éviter les pages trop proches, sans suppression automatique.
- Les pages indiquent explicitement qu'une brève a été rédigée avec l'aide d'une IA à partir de la source citée. C'est une bonne pratique de transparence, mais la qualité et la valeur ajoutée doivent rester prioritaires.

### Diagnostic
La fraîcheur des 50 brèves est satisfaisante dans le dépôt consulté. Le risque principal n'est donc pas un manque de fréquence de publication : c'est de s'assurer que chaque brève apporte un angle propre, vérifiable et utile, et que le volume du sitemap (1 709 URL) reste proportionné à la qualité des pages réellement indexables.

### Vérification technique complémentaire
Le workflow reconstruit les pages d'articles et le sitemap après la collecte. La collecte conserve des identifiants basés sur l'URL source, élimine les URL déjà publiées et utilise une comparaison de titres pour limiter les sujets similaires. Cette protection existe déjà dans le code : ne pas réécrire une seconde déduplication sans tests ciblés.


## 10. Contrôle réel des publications Facebook / Instagram

Le code et les accusés publics confirment qu'une chaîne de publication Meta existe déjà : elle cible précisément trois Pages Facebook et deux comptes Instagram. Il ne faut donc pas repartir de zéro ni réinstaller un outil de programmation tiers.

### Comptes et créneaux déclarés dans le code
- Facebook Véloce Mercato : 08 h, 12 h, 20 h.
- Instagram @veloce.mercato : 12 h, 20 h.
- Facebook VM Actus & Pronos : 12 h, 20 h.
- Facebook VM Univers : 08 h, 12 h, 18 h.
- Instagram @vmunivers.fr : 18 h.

Le workflow `editorial-vm.yml` vérifie les confirmations, l'identité des comptes et les anti-doublons avant l'envoi. Le code refuse de publier si l'identité d'un compte ne correspond pas à la destination prévue.

### Derniers permaliens présents dans le journal public consulté
- Facebook Véloce Mercato : publication confirmée le 22 novembre 2026 vers 20 h, heure de Paris.
- Facebook VM Actus & Pronos : publication confirmée le 22 novembre vers 20 h.
- Instagram @veloce.mercato : publication confirmée le 22 novembre vers 20 h.
- Facebook VM Univers : publication confirmée le 22 novembre vers 17 h 31.
- Instagram @vmunivers.fr : dernier permalien journalisé le 11 novembre 2026 vers 4 h 25.

**Point prioritaire :** le compte Instagram VM Univers paraît en retard de diffusion par rapport aux quatre autres. Il faut diagnostiquer la connexion, les créneaux, le quota et le journal d'accusés avant de tenter un nouvel envoi.

Le workflow séparé `tiktok-metricool.yml` est uniquement déclenchable manuellement et son mode déclaré est `essai`. Il ne fait pas partie du périmètre retenu de trois Pages Facebook et deux comptes Instagram. Aucun usage de Metricool n'est nécessaire pour le plan des cinq comptes.

## 11. Incident de déploiement Cloudflare — preuve par les logs GitHub Actions

Le run GitHub Actions `45079938522` du 22 novembre 2026, workflow `Publier Véloce Mercato sur Cloudflare`, a échoué à l'étape de publication :
- la préparation du site a terminé et a annoncé 1 857 pages préparées ;
- Wrangler a reconnu un Account API Token et le compte Cloudflare associé ;
- l'appel au projet Pages `velocemercato` a échoué avec `Authentication error [code: 10000]` ;
- le contrôle du domaine a été ignoré après cet échec.

Le diagnostic le plus probable est un jeton dont les permissions ou le périmètre de compte ne permettent pas le déploiement Pages. La documentation Cloudflare demande le droit **Account → Cloudflare Pages → Edit** (ou `Pages Write` dans la nomenclature API) pour créer un déploiement. Sources officielles : https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/ et https://developers.cloudflare.com/pages/configuration/api/.

**Correction à faire côté Cloudflare/GitHub :** créer ou corriger un jeton dédié avec Cloudflare Pages Edit sur le compte qui héberge le projet, puis remplacer le secret GitHub `CLOUDFLARE_API_TOKEN` sans jamais le communiquer dans une conversation. Vérifier que `CLOUDFLARE_ACCOUNT_ID` désigne le même compte. Rejouer ensuite le déploiement et contrôler `version.txt` et le domaine. Ne pas modifier DNS pour résoudre un problème de permission API.

Les exécutions du workflow Pages de VM Univers du 22 novembre ont, elles, terminé avec succès dans les runs consultés. Cela confirme le pipeline GitHub de VM Univers, pas nécessairement toutes les routes du site en production.


## 12. VM Studio — dernier déploiement vérifié

Le run GitHub Actions `45073604943` du 22 novembre 2026 pour `Déployer VM Studio sur Cloudflare` est terminé avec succès.
- Les tests Node.js de création, IA, paiement, transmission et suivi ont réussi : 7 tests recensés dans le journal.
- Le contrôle de `https://atelier.velocemercato.fr/api/config` et le contrôle CORS de suivi ont été exécutés.
- Wrangler a confirmé le déploiement de la version `vm-atelier` à 100 %.

C'est un bon signal opérationnel pour VM Studio. Cela ne remplace pas un test utilisateur complet du formulaire de création, de la réception d'une demande réelle ni un paiement réel. Le paiement testé dans le pipeline est en mode test.


## 13. VM Multisport — contrôle du flux et séparation du Foot

Le flux `multisport/actualites.json` consulté le 23 novembre contient 54 articles répartis dans 11 disciplines :
- NBA : 9
- NFL : 2
- F1 : 11
- MotoGP : 11
- Tennis : 5
- Rugby : 7
- NHL : 2
- MMA : 1
- Ski : 6
- Cyclisme : 0
- MLB : 0

Aucun contenu Foot n'est présent dans ces catégories. Les articles observés comportent une source et une URL, avec des dates récentes au 22 novembre. Le workflow de mise à jour des liens multisport a terminé avec succès le 22 novembre.

**Conclusion :** la séparation Foot / Multisport est visible dans les données du dépôt et fonctionne dans le flux consulté. Les disciplines sans article ne doivent pas être remplies artificiellement : il faut attendre une actualité valable ou améliorer la couverture des sources.
