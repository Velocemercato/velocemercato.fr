# Audit technique du réseau VM — 23 octobre 2026

Les vérifications portent sur le code des dépôts et sur des serveurs HTTP locaux dans Chromium. Les requêtes vers les services tiers sont bloquées ou remplacées par des réponses contrôlées pour les essais de panne et de lecture. L’accès direct aux domaines est filtré par l’environnement : ce document ne certifie pas le DNS, les services externes, une mesure de rapidité en 4G ou un test physique sur Android.

## Corrections apportées

- Gaming et sources Actus : retrait des débordements constatés à 320 pixels, sans masquer le contenu.
- Champs de recherche et de CV : libellés accessibles.
- QR de partage : bibliothèque MIT locale, provenance et licence conservées ; aucun générateur distant requis. Menu : sauvegarde avant les sorties de fonction, PNG de 880 pixels, téléchargement désactivé si le contenu est trop long, liens partagés et retour à l’éditeur fonctionnels.
- Radio : affiches locales quand elles existent, absence de lecture automatique, liste et audio en erreur signalés, reprise du chargement possible.
- Météo : valeurs absentes affichées comme absentes, délai de réponse borné, nouvelle tentative, réponses tardives ignorées pour conserver la dernière sélection. Les contributions restent centralisées sur le domaine média, conformément à la modification parallèle.
- Produits locaux, Sport et Pépite : distinguer une panne d’une liste réellement vide et permettre une nouvelle tentative. Accord parental demandé pour les catégories U11, U13, U15 et U17 ; ceci ne remplace pas la vérification des autorisations avant publication.
- Contacts des outils VM : adresse VM Univers ; la rédaction et le football conservent leur adresse distincte.
- Nouvelle page /vente/ : création parallèle conservée ; exemples cliquables, contact professionnel et retour VM Univers, distinction entre créations internes et références clients, suivi défini au devis. Le site vitrine conserve son prix public existant dès 590 € ; aucun nouveau prix n’est fixé.
- Cache des deux domaines : nouvelle version, bibliothèque QR ajoutée aux ressources locales. Les caches d’autres applications sont préservés.
- Papiers Sans Galère : retrait des appels au compteur public commun ; retour direct VM Univers ; QR local ; activation du service worker limitée au nettoyage des caches de sa propre application.

## Résultats vérifiés

- Deux dépôts principaux : 414 pages HTML et 10 230 références internes contrôlées, aucune destination de fichier ou ancre manquante, aucun identifiant dupliqué relevé par le contrôle.
- Pages d’entrée : 117 navigations à 320, 390 et 1 440 pixels, sans erreur JavaScript observée, requête locale en 404, image cassée, champ visible sans libellé, bouton visible sans nom ou débordement horizontal.
- Papiers Sans Galère : les trois pages à ces trois largeurs, soit neuf contrôles d’affichage supplémentaires ; partage local fonctionnel et aucun appel au compteur public ; 51 références internes de fichiers contrôlées sans destination absente.
- VM Univers : 21 tests exécutés, 19 réussis et deux tests propres au Menu QR ignorés, car cet outil est sur le domaine média.
- Véloce Mercato : 35 tests ciblés réussis (site 5, professionnels 6, QR 3, résilience météo 3, services 5, Pépite 4, radio 2, lecteur vidéo 7).
- Papiers Sans Galère : deux tests réussis, dont isolation du cache et rechargement hors connexion.

Les identifiants et données utilisés pour les tests de formulaires sont fictifs. Aucun e-mail, inscription, vote, message social, vidéo ou donnée personnelle réelle n’est envoyé par les tests. La lecture H.264 utilise un média de contrôle ; elle ne mesure pas le débit d’un CDN public.

## Limites et suites utiles

Les corrections portent sur les défauts observés, pas sur une certification générale. Les liens vers des services externes, comptes YouTube/Twitch, statistiques privées, performances réseau réelles, droits sur les médias, mentions professionnelles et contrats commerciaux nécessitent leurs propres preuves ou configurations. Les pages de démonstration et anciens alias noindex ne constituent pas des références clients.

Les statistiques privées ne sont pas activées par cette modification. Aucun chiffre d’audience ou de rentabilité n’est créé. GitHub Pages est statique : un mot de passe écrit en JavaScript ne protégerait pas un tableau de bord public. Choisir un fournisseur avec tableau de bord dans le compte du propriétaire et configurer séparément les deux domaines.

GitHub Pages et les API tierces ont des conditions d’usage : vérifier notamment les usages commerciaux prévus avant de vendre une prestation d’hébergement ou une intégration météo. Aucune migration de domaine n’est entreprise.

## Reproduire et comparer

Installer les dépendances de tests du dépôt et disposer de Chromium. Les essais de lecteur vidéo nécessitent aussi ffmpeg. Les fichiers de contrôle sont dans `tests/`. Sur les deux dépôts principaux, `VM_TEST_ARTIFACTS` permet de choisir le répertoire des captures.

- VM Univers : `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v`.
- Véloce Mercato : lancer les modules `test_site`, `test_professional`, `test_local_qr`, `test_weather_resilience`, `test_services`, `test_pepite`, `test_radio` et `test_pastille_browser` avec unittest discover. Ne pas déclencher les workflows de publication pour tester un formulaire.
- Papiers Sans Galère : `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

Branche de travail : `codex/audit-sites-23oct` dans les trois dépôts. Les changements publiés en parallèle ont été intégrés avec Git, sans écraser leur historique. Les liens de comparaison GitHub rendent la branche consultable ; ils ne constituent pas à eux seuls une pull request créée.

## Aperçus locaux

- [Aperçu velocemercato.fr-accueil-390](audit-23oct2026/velocemercato.fr-accueil-390.png)
- [Aperçu velocemercato.fr-web-studio.html-1440](audit-23oct2026/velocemercato.fr-web-studio.html-1440.png)
