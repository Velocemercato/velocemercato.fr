# Audit du parcours professionnel — 23 octobre 2026

Le visiteur doit comprendre ce que propose VM, voir des créations réelles, choisir un service et préparer une prise de contact. VM Univers reste le portail central ; Véloce Mercato garde sa présentation football.

L'examen part des versions `b2fddee` de VM Univers et `3ae86181` de Véloce Mercato. Les domaines publics sont filtrés par le proxy de cet environnement (403 sur le tunnel). La navigation et les captures sont réalisées avec Chromium sur les versions locales issues des dépôts publiés. Il s'agit de simulations de tailles d'écran, pas d'un essai sur un Samsung physique.

| Constat initial | Correction |
| --- | --- |
| L'accueil VM présente l'annuaire ; le visiteur professionnel ne voit pas immédiatement les offres. | Entrée professionnelle dans la navigation et l'accroche, trois accès par besoin, nouvelle page `/professionnels/`. |
| Les cartes de visite sont noyées dans une liste « logo & identité ». | Offre nommée « Cartes de visite & visuels », liste des supports et choix dédié dans la demande. |
| Les pages Web Studio et Services Web répètent les offres et mélangent création, outils et aide administrative. | Le Web Studio présente la création et ses formules. Services Web conserve les outils et l'aide et oriente vers la vitrine pour les prestations de communication. Les anciennes URL restent utilisables. |
| L'offre apparaît surtout au pied du média football. | Lien « Pro · sites & visuels » dans la navigation du Foot, d'Actus et de Gaming ; encart d'entrée existant réorienté vers le studio, sans ajouter de lecteur ou de fenêtre intrusive. |
| Certaines promesses manquent de cadre : réponse systématique en 48 h, modifications « incluses », parrainage d'éditions fixes. | Périmètre, suivi, délai et disponibilité à confirmer par écrit. Le statut d'ouverture prochaine déjà présent est conservé de façon cohérente. |
| La page publicité laisse entendre qu'une mesure d'audience est disponible sur demande. | L'absence d'activation des statistiques est explicite ; aucun nombre ni résultat commercial n'est annoncé. |
| La création d'un support et son impression peuvent se confondre. | Conception, fichiers livrés et impression distingués dans les offres et la FAQ. |
| Plusieurs catégories de l'annuaire contiennent des grilles imbriquées, réduisant la place des cartes. | Une grille par catégorie. Les six catégories et les 22 projets sont conservés. |

## Parcours livrés

- VM Univers : accueil → offres professionnelles → créations → demande personnalisée.
- Véloce Mercato : lien professionnel → Web Studio → formules web, cartes, identité et publicité.
- Publicité : choix d'un espace au tarif déjà affiché → service présélectionné → demande de disponibilité.
- Le flyer et les cartes de visite recto / verso VM Détailing existants sont présentés en exemple et peuvent être ouverts en grand.
- Les exemples de créations appartiennent au réseau VM. Les modèles garage, restaurant et club restent clairement des démonstrations.
- Les logos, photos, vidéos et créations existants restent en place. Les nouveaux aperçus sont des captures des sites, pas des témoignages ou des références clients inventés.

## Prix et disponibilité

Les prix web déjà publiés sont conservés : page unique dès 290 €, vitrine dès 590 €, site avec application installable dès 790 €, logo/visuels dès 90 €. Les cartes de visite sont sur devis. Les offres publicitaires existantes restent à 9,90 €, 29 €, 39 €, 49 € et 69 € par mois. Le détail, les droits d'usage, le suivi, les frais récurrents éventuels et l'impression sont à préciser par écrit.

Le studio annonçait déjà son ouverture prochaine : cette information n'a pas été remplacée par une annonce d'ouverture effective sans confirmation. La disponibilité des supports publicitaires, en particulier vidéo, est à confirmer avant réservation.

## Contact et confidentialité

Le contact professionnel est **vminvest.fr@gmail.com**. Le contact rédactionnel Foot, Actus et Gaming reste **velocemercato.fr@gmail.com**.

Le formulaire prépare un brouillon dans le navigateur. Il n'enregistre pas les champs dans le stockage local, ne les place pas dans l'URL et ne les transmet pas à un serveur. Le visiteur ouvre sa messagerie et appuie lui-même sur Envoyer. Une copie manuelle et l'adresse e-mail visible restent disponibles. Sans JavaScript, l'adresse et une aide de contact restent lisibles. Aucun e-mail réel n'a été envoyé et la réception de la boîte n'a pas été testée.

## Validation

- Six pages contrôlées à 320, 390, 768 et 1440 pixels : les deux accueils, la vitrine professionnelle, le Web Studio, Publicité et Services Web. Aucun débordement horizontal, image cassée ou erreur JavaScript dans ces contrôles.
- 317 liens et ressources contrôlés sur les pages modifiées, avec vérification des fragments internes et des destinations dans les deux dépôts.
- 25 tests automatisés validés, entre les deux dépôts : parcours professionnels, annuaire et régressions des sites.
- Tests des thèmes, de la recherche combinée, du maintien des 22 projets, des liens de marque et du cache hors connexion.
- Tests des choix d'offre, des brouillons et accents, de l'absence d'envoi implicite et de stockage local, de la copie de secours, de l'invalidation d'un ancien brouillon et des coordonnées accessibles sans JavaScript.
- Vérifications de l'affichage football en modes clair et sombre, de la conservation des proportions de sa bannière et du fonctionnement des filtres d'actualités.

Les captures et les résultats de navigation se trouvent dans `apercus-pro/`. Les résultats de déploiement GitHub Pages sont contrôlés séparément après les pushs. Un succès de déploiement ne constitue pas un essai direct sur les domaines publics depuis cet environnement.
