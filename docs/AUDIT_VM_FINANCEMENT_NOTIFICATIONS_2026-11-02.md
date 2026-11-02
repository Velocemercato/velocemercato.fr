# Audit VM — notifications, soutien, monétisation
Date : 2 novembre 2026

## Notifications
**Livré** : centre de préférences `/notifications/`, accessible depuis Véloce Mercato, VM Actus, VM Gaming, Pronos et VM MANGAS, avec cinq sujets distincts. Aucun choix coché au départ. Choix conservés dans localStorage (sur ce navigateur et ce domaine uniquement). Lorsqu'une page VM est ouverte, contrôle périodique toutes les trois minutes, et au retour dans l'onglet.

**Sources** : `/fil.json` (foot, actus, gaming), `/pronos/` (édition du jour), `/notifications/episodes.json` (nouveaux épisodes officiels ajoutés par l'équipe). Cette liste de mangas doit être mise à jour à chaque nouvel épisode.

**Limite** : aucun push à distance quand le navigateur est fermé. Pour cette fonction : créer un projet Web Push / VAPID, héberger le service d'envoi, enregistrer les subscriptions avec consentement, fournir désinscription, politique de confidentialité et suppression des données. Service workers seuls sur GitHub Pages ne suffisent pas. Les préférences du domaine vmunivers.fr sont indépendantes de celles de velocemercato.fr.

**Protection** : notification système demandée uniquement après clic. Aucune collecte de courriel, téléphone ou nom. Ne pas envoyer de contenus publicitaires ou de jeux d'argent via les alertes.

## Dons / soutien
Inspecté : `/soutenir.html`, `/liens.json` et `/transparence.json`.

- `soutien_media` : URL Stripe Payment Link de forme `https://buy.stripe.com/...` présente.
- `soutien_pro` et `soutien_gaming` : vides ; les boutons doivent rester désactivés.
- `transparence.json` : tableaux `contributions` et `depenses` actuellement vides. Ne pas publier « 0 € encaissé » comme preuve comptable, simplement « aucun reçu déclaré sur le site ».
- Le site remplace le bouton du média par le vrai lien Stripe si la configuration JSON se charge.
- **Non vérifié** : état actif du Payment Link, compte Stripe bénéficiaire, identité, KYC, virements, statut live/test, paiement finalisé, remboursement, frais Stripe. Impossible de confirmer sans accès au compte Stripe ou contrôle par son propriétaire.
- Ne jamais déclencher un paiement test sur le vrai compte pour vérification sans accord spécifique et possibilité de remboursement.
- Ne pas promettre de reçu fiscal. En France, contributions / financement participatif peuvent être fiscalisés selon la situation du bénéficiaire.
- La page promet une transparence régulière : mettre à jour les transactions **effectivement vérifiées**, jamais des montants approximatifs.

## Priorité revenus (sans chiffres d'audience inventés)
1. **Services VM Studio** : offres de création de sites + maintenance, plus faciles à convertir en revenus direct avec quelques clients réels. `/web-studio.html`.
2. **Publicité locale et espaces partenaires** : `/pub/` présente déjà fiches et encarts, avec grille indicative entre 9,90 et 69 €/mois pour les formats standards (à confirmer individuellement). Aucun emplacement ni audience garantis.
3. **Sponsoring des contenus originaux** : La Pastille, reportages, quiz originaux et articles de gaming. Mention publicitaire explicite et adéquation éditoriale. Pas de faux partenariat et pas de publicité intégrée aux épisodes des ayants droit.
4. **Soutien volontaire Stripe** : uniquement pour le lien média effectivement actif ; argent reçu et redistribué sous contrôle et traçabilité.
5. **Monétisation YouTube de vidéos originales** : vérifier les conditions du programme YouTube Studio et la propriété des contenus. Ne pas republier des épisodes de tiers.
6. **AdSense sur les pages originales** : candidature éventuelle après audit qualité et politique. Les pages dont la valeur consiste surtout à intégrer un épisode tiers ne doivent pas être le centre de ce modèle. Ne pas activer d'annonces sur pages pour enfants ou sur vidéo tierce sans validation des règles.
7. **Partenaires / investisseurs** : `/investisseurs.html` existe ; un dossier à chiffres mesurés, coûts, taux de conversion et plan juridique est indispensable avant toute démarche financière.

## Actions externes encore nécessaires
- Ouvrir Stripe Dashboard : confirmer compte de versement, lien et mode live, faire un essai sur environnement de test séparé si nécessaire.
- Relever visites et sources du trafic à partir des outils analytics auxquels vous avez accès (sans promettre un chiffre impossible à justifier).
- Réaliser kit partenaires **daté** : lignes éditoriales, statistiques réelles, format, durée, tarifs proposés, politique pub + contact.
- Vérifier mentions légales, politique de confidentialité, publicités identifiées et statut fiscal de l'activité.
- Pour web push hors navigation : choisir l'opérateur de diffusion et finaliser les contrats/données.
