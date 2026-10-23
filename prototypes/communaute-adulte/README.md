# À Part — maquette de communauté adulte

Identité provisoire. Prototype indépendant, sans lien dans la navigation du portail VM. Le dossier n'est pas un service de rencontres ouvert au public ; la PR reste en brouillon pour relecture.

## Parcours réalisés

- Entrée de démonstration « 18 ans ou plus », explicitement distinguée d'une vérification de majorité.
- Six profils fictifs, majeurs, sans photos ni adresses réelles.
- Recherche par ville ou intérêt ; filtres combinables : couple/femme/homme, reçoit chez soi/se déplace/hôtel, soirée/week-end/vacances.
- Détail de profil avec préférences ; aucune adresse précise ni disponibilité en direct.
- Trois salons de test : lounge, présentations, idées de sorties.
- Conversation privée distincte pour chaque profil, messages rédigés par le visiteur, aucun faux interlocuteur ni réponse automatique.
- Pseudo de test, blocage/déblocage, signalement avec motif, réinitialisation de la démo.
- Tous les contenus saisis sont ajoutés par nœuds texte. Aucun `innerHTML` utilisé pour les afficher.

## Données et limites

Aucun backend, appel réseau applicatif, stockage local, cookie, compte ou paiement. Les messages, pseudos, blocages et signalements restent en mémoire et sont perdus au rechargement. Aucun modérateur ne reçoit les signalements. Les préférences ne constituent pas un consentement à une rencontre.

Le nom, les initiales, les âges, les villes et les biographies des cartes sont des exemples inventés, indiqués comme tels. L'affichage ne permet ni de contacter un membre réel ni de réserver un hôtel.

## Ouvrir et vérifier avec Claude

Servir ce dossier comme fichiers statiques dans l'environnement de développement habituel ; ouvrir `index.html` via HTTP. Les modules ne sont pas destinés à être ouverts directement avec `file://`.

1. Sur ordinateur et mobile, vérifier la mise en page, le clavier et la fermeture des fenêtres de profil.
2. Accepter l'entrée de démo, filtrer « couple / reçoit chez soi / vacances », puis vérifier les filtres combinés et « Tout voir ».
3. Ouvrir un profil, essayer un message privé, puis vérifier que les autres conversations et salons restent distincts.
4. Bloquer le profil : sa carte doit disparaître et son envoi privé être désactivé. Débloquer dans « Respect & sécurité ».
5. Enregistrer un signalement de test, vérifier qu'il est marqué « non transmis », puis réinitialiser et recharger.
6. Essayer un texte contenant des balises : il doit apparaître littéralement, sans exécution.

## Vérifications effectuées

- Avant et après modification : `python -m unittest discover -s tests -p 'test_pastille_schedule.py' -v` : 3 tests passent.
- `node --test tests/test_adult_demo.mjs` : 7 tests passent sur les filtres, messages distincts, blocage, signalement, limites et remise à zéro de l'état.
- `node --check` des deux modules : succès.
- HTML : identifiants uniques, correspondance des labels, présence des fichiers locaux et références DOM vérifiés.
- `git diff --check` : succès.
- Vérification visuelle et exécution dans un vrai navigateur non effectuées : superviseur `sites-previewd` indisponible dans cet environnement. Ces contrôles restent nécessaires avant validation.

## Reprise technique avant un service réel

Valider le nom et un domaine séparé. Définir l'inscription, l'authentification, la vérification de majorité adaptée au périmètre, les droits d'accès et l'effacement des données. Remplacer l'état en mémoire par un backend protégeant les conversations ; faire appliquer les blocages et autorisations côté serveur. Prévoir consentement et contrôles de confidentialité, signalements effectivement reçus, modération et limites d'envoi avant l'ouverture. Aucun de ces services serveur n'est revendiqué par ce prototype.
