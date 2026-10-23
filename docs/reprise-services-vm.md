# VM Services — reprise du 24 octobre 2026

## Livré pour relecture

- `/services/` : recherche par ville, trois catégories CBD, cavistes/commerces d'alcool, taxis/VTC.
- Accès par `/services/?categorie=cbd`, `?categorie=caviste` et `?categorie=taxi` depuis `/pro/`.
- Les recherches vont vers Google Maps ; les horaires et disponibilités doivent être confirmés directement auprès du professionnel. Le choix « ouvert maintenant » ajoute une demande à la recherche externe, sans garantie de filtrage ou d'exhaustivité.
- Aucun faux établissement, faux avis ou horaire inventé. Les fiches VM ne sont pas encore alimentées. L'inscription renvoie au formulaire existant de VM Pro Local, qui prépare un e-mail.
- Aucun paiement, commande, réservation, compte ou chat ajouté. Tarifs et portail football inchangés.

## Reprise

1. Relire cette PR avec Claude, terminer la vérification visuelle et les tests navigateur, puis fusionner après validation.
2. Vérifier les premières adresses auprès des professionnels (nom, catégorie, adresse, téléphone public, lien officiel, horaires et date de contrôle) avant de créer leurs fiches. Ne pas recopier massivement les données de Google Maps.
3. Prévoir une source de données et un calcul d'ouverture avec fuseau horaire, jours fériés, fermetures exceptionnelles et horaires de nuit avant d'afficher un statut VM « ouvert maintenant ».
4. Garder l'alcool limité aux professionnels pour cette première version. Étudier séparément tout projet de vente, livraison ou mise en relation entre particuliers.
5. Décider du domaine et du périmètre de la communauté adulte séparée ; voir `projet-communaute-adulte.md`.
6. Reprendre le comparatif matériel/setup avec la liste exacte des composants, le budget et le pays de livraison. Aucun achat ni recherche de prix n'est inclus dans cette PR.

## Validation

Avant modification : `python -m unittest discover -s tests -p 'test_pastille_schedule.py' -v` : 3 tests passent.

Après modification : même suite, 3 tests passent ; `node --test tests/test_local_services.mjs` : 5 tests passent. Vérification des recherches par catégorie, encodage d'entrées, catégories invalides et absence de promesse de disponibilité des taxis. `git diff --check` passe.

Suite navigateur existante : tentative de `python -m unittest discover -s tests -p 'test_services.py' -v` bloquée à l'import par `ModuleNotFoundError: No module named 'playwright'`. Aucun résultat navigateur automatisé n'est revendiqué.

Prévisualisation visuelle : le superviseur `sites-preview` n'a pas pu démarrer (`sites-previewd mailbox is unavailable`). Relecture visuelle sur ordinateur et téléphone encore à effectuer ; PR à conserver en brouillon jusque-là.

Contrôle complémentaire : `test_diffusion.py` donne 31 succès sur 32. Le test `test_promos_upload_private_two_per_run_without_duplicates` échoue car les vidéos `media/promos/*.mp4` ne sont pas présentes dans ce checkout partiel ; la file est donc vide. Les modules de diffusion n'ont pas été modifiés.
