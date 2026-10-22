# Audience privée : proposition pour les deux sites

## Constat et correction

Les anciens scripts envoyaient les visites de plusieurs sites dans les mêmes clés `vm-stats-*` chez un service de compteurs publics. Une visite était comptée par onglet, pas par personne. La page `stats.html` de Véloce Mercato était lisible sans connexion : `noindex` ne constitue pas une protection. Une erreur réseau y devenait un zéro, ce qui pouvait laisser croire à une absence de visiteurs.

Ces appels d’audience sont retirés des deux dépôts, y compris des générateurs. Le tableau public est retiré. Les sondages football restent indépendants de la mesure d’audience. Les compteurs historiques hébergés chez le tiers restent publics et mélangés avec d’autres sites : ils ne deviennent pas privés par cette modification et ne doivent pas être importés comme fréquentation fiable de chacun de ces deux domaines.

## Solution recommandée : Plausible

Deux sites distincts dans un compte personnel Plausible : `vmunivers.fr` et `velocemercato.fr`. Les tableaux de bord sont privés et accessibles après connexion au compte. Ne pas activer la visibilité publique, créer de lien de partage, ni intégrer un tableau dans les pages GitHub Pages.

- Visiteurs uniques estimés, visites et pages vues pour chaque domaine, sans les additionner entre sites.
- Périodes aujourd’hui, semaine civile depuis lundi, mois civil et périodes personnalisées ; fuseau Europe/Paris pour les deux sites.
- Courbes d’évolution et comparaison avec la période précédente ; vérifier les dates affichées, notamment si un raccourci utilise une période glissante plutôt qu’une période civile.
- Mesure sans cookies, sans identifiant persistant entre sites. Pas de suivi publicitaire ni de collecte des formulaires. Désactiver les mesures optionnelles inutiles et ne pas envoyer de propriétés personnelles.
- Compatible avec les pages HTML statiques de GitHub Pages : un script public de collecte, aucun secret et aucune API de lecture des statistiques dans le navigateur.

Plausible Cloud est un service payant après sa période d’essai. Aucun compte ni abonnement n’a été créé. Alternative gratuite : Cloudflare Web Analytics, avec deux sites et un tableau de bord dans le compte Cloudflare ; ses métriques de visites ne doivent pas être présentées comme un décompte exact de personnes uniques.

## Activation après choix du propriétaire

La collecte Plausible n’est pas activée dans ces branches. Aucune clé ni URL de script personnalisée n’est inventée. Le propriétaire doit d’abord créer ou utiliser son compte et ajouter les deux domaines séparément.

1. Choisir Plausible ou l’alternative, puis créer les deux entrées de site. Garder la visibilité privée et sécuriser le compte avec les protections proposées.
2. Dans les réglages de chaque site Plausible, récupérer son extrait officiel dans **General → Tracking → Site installation**. Il s’agit d’un extrait public de collecte, pas d’un mot de passe : ne jamais transmettre de clé API de lecture ni de code de connexion.
3. Préparer une modification dédiée qui insère l’extrait exact dans le `<head>` des pages du domaine correspondant et dans leurs générateurs. Limiter l’exécution aux noms d’hôte de production attendus ; les aperçus locaux et de branches ne doivent pas être comptés.
4. Mettre à jour l’information de confidentialité des deux sites : prestataire, finalité, données effectivement traitées, durées et contact. La qualification d’une éventuelle exemption de consentement dépend de la configuration et des règles applicables ; l’absence de cookies ne suffit pas à elle seule.
5. Après autorisation de fusion et publication, utiliser la vérification d’installation du prestataire. Effectuer une visite de contrôle sur chaque site, confirmer son attribution au bon domaine et vérifier qu’un visiteur déconnecté ne peut pas ouvrir les tableaux de bord.
6. Confirmer l’absence de cookies de mesure, de stockage d’identifiants et d’envoi du contenu des formulaires. Vérifier les courbes et les périodes dans le fuseau choisi. Exclure ses propres visites si souhaité, selon la procédure officielle.

La mesure démarre à l’activation effective, sans reconstitution de chiffres antérieurs. Les bloqueurs de suivi, les navigateurs et les méthodes de déduplication limitent la précision : « visiteurs uniques » est une estimation, pas un registre de personnes. Une même personne peut être décomptée à nouveau un autre jour : respecter la définition du prestataire pour les cumuls hebdomadaires et mensuels. Une panne ou une donnée absente doit être affichée comme indisponible, jamais transformée en un chiffre d’audience.

## Documentation officielle consultée

- https://plausible.io/docs/plausible-script
- https://plausible.io/docs/visibility
- https://plausible.io/docs/your-plausible-experience
- https://developers.cloudflare.com/web-analytics/

Cette proposition ne modifie aucun réglage de compte, DNS, facturation ou production.
