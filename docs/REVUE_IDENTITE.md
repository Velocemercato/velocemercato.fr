# Véloce Mercato : diagnostic et corrections à examiner

## Constats

- Le domaine déclaré et le lien canonique correspondent déjà à `velocemercato.fr`.
- Sur ordinateur, le texte d’accueil était posé sur l’illustration football et la hauteur imposée pouvait la recadrer. Une seconde bannière avait aussi une hauteur maximale avec `object-fit: cover`.
- Le logo d’en-tête renvoyait vers `#top`, situé dans le contenu après la bannière. Les liens « Tous les sites VM » conduisaient vers une copie du portail sur `/vm/`, parfois via une redirection intermédiaire `/groupe.html`.
- Le tableau `stats.html` n’était pas privé : tout visiteur connaissant l’URL pouvait le lire, et le service de compteurs permettait de consulter les clés sans connexion. Les mêmes clés mélangeaient plusieurs sites. Les échecs de lecture étaient affichés comme des zéros.
- Le précache du service worker contenait une icône inexistante ; l’erreur était ignorée. La suppression des caches n’était pas limitée aux caches de cette application.

## Corrections de la branche

- Illustration football conservée, entière et sans déformation : texte à côté sur ordinateur, dessous sur mobile. La seconde bannière est également affichée avec ses proportions d’origine.
- Logo football cliquable vers `/`, logo du pied de page cliquable et ajustement du pied de page pour les écrans de 320 px.
- Liens du portail dirigés vers `https://vmunivers.fr/`, dans les pages existantes et le générateur `vmbar.py`. Les anciennes URL `/vm/` et `/groupe.html` proposent un lien explicite vers VM Univers, sans déplacement automatique. La copie source du portail est retirée pour éviter sa régénération.
- Les raccourcis du manifeste football restent sur le domaine football ; le portail externe reste accessible par la navigation du site. L’ancienne application installée depuis ce domaine ouvre une page de passage explicite : elle ne peut pas être transférée silencieusement vers un autre domaine.
- Styles utilitaires de l’accueil précompilés avec la même version Tailwind 3.4.17 et la même configuration typographique, pour ne plus dépendre du script CDN à chaque ouverture. Les autres pages conservent leurs styles existants.
- Compteurs d’audience publics retirés de toutes les pages et de leur générateur, tableau public retiré. Le changement répété dans les pages d’articles ne touche que la navigation commune et les appels d’audience. Les sondages, leurs compteurs de votes, les articles et leurs données sont conservés.
- Cache `vm-app-v4` limité aux ressources du même domaine : icône valide, remplacement des anciens caches de l’application, conservation des caches étrangers, absence de cache des JSON et erreurs hors connexion explicites.
- La bannière VM Détailing « Ouverture prévue courant juin 2027 » est conservée.

## Validation locale

Prérequis de test : Python 3.12, Chromium et `python3 -m pip install -r tests/requirements.txt`.

Commande : `python3 tests/test_site.py`. Le navigateur peut être choisi avec `VM_CHROMIUM_EXECUTABLE` ; les captures sont écrites dans le dossier choisi par `VM_TEST_ARTIFACTS`, ou `/tmp/vm-site-tests` par défaut.

Les tests vérifient les domaines déclarés, les liens internes, les images, le manifeste, le chargement réel des articles JSON, les huit combinaisons de largeur (320, 390, 768 et 1440 px) et de thème clair/sombre, les proportions de l’illustration et l’absence de texte superposé, de débordement ou d’erreur JavaScript. Ils couvrent l’ouverture d’un article, sa fermeture, le filtre Mercato, le logo d’accueil et le thème. Ils vérifient aussi le service worker, sa migration, la protection des autres caches, l’absence de cache des JSON, le repli hors connexion et la suppression des appels d’audience dans les pages et le générateur.

Les essais mobiles sont des émulations Chromium. Les services tiers sont bloqués : les votes, Discord, polices Google, flux externes et autres intégrations ne sont pas déclarés validés en ligne. Les captures montrent les polices système de repli si nécessaire. Aucune donnée de fréquentation n’est inventée.

## Recompiler les styles de l’accueil

Depuis la racine du dépôt, avec Node.js et npm :

```sh
npm exec --yes --package=tailwindcss@3.4.17 -- tailwindcss --config tools/home-tailwind.config.cjs --input tools/home-tailwind.css --output assets/home-utilities.css --minify
```

Le CSS généré est versionné : GitHub Pages n’a pas besoin d’exécuter npm. Relancer cette commande si des classes utilitaires sont ajoutées ou modifiées dans l’accueil.

## Contrôles et décisions restants

Les accès HTTPS à `api.github.com`, `vmunivers.fr` et `velocemercato.fr` sont bloqués par le proxy ; la résolution DNS locale n’est pas disponible. Le contrôle du site public et des paramètres de publication GitHub Pages reste donc à faire. Aucun DNS ou `CNAME` n’est modifié.

La proposition de statistiques privées est dans [STATISTIQUES_PRIVEES.md](../STATISTIQUES_PRIVEES.md). Aucun compte payant n’est créé et aucune collecte Plausible n’est activée. Son activation nécessitera le choix du propriétaire, les extraits officiels des deux sites, une information de confidentialité adaptée et une nouvelle validation.

Examiner les captures dans `docs/apercus/` et la pull request. Aucune fusion ou mise en production n’est autorisée par la préparation de cette branche.
