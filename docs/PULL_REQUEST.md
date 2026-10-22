Titre : Véloce Mercato — bannière intégrale, navigation et confidentialité

Le texte d’accueil pouvait couvrir l’illustration football, dont la hauteur imposée recadrait aussi le dessin sur ordinateur. Cette branche conserve les illustrations et leur identité football, affiche l’image entière et dispose le texte à côté sur ordinateur, puis dessous sur mobile. Les logos d’en-tête et de pied de page ramènent à l’accueil ; le pied de page reste contenu à 320 px.

Les liens de la navigation commune ouvrent directement `vmunivers.fr`. Les anciennes adresses du portail conservent un lien explicite vers ce domaine ; le générateur ne recrée plus une copie du portail sur le site football. Les styles Tailwind 3.4.17 de l’accueil sont précompilés et versionnés pour enlever sa dépendance au script CDN.

La page `stats.html` n’était pas privée, et les clés de comptage étaient publiques et communes à plusieurs sites. Le tableau et les appels d’audience sont retirés, y compris du générateur et des pages d’articles existantes. Les modifications répétées de ces pages concernent uniquement les liens communs et les compteurs d’audience ; les sondages et leurs votes restent en place. La proposition Plausible prépare une mesure séparée par domaine, non activée en l’absence de choix et de configuration du propriétaire.

Le service worker précache une icône existante, remplace les anciens caches de l’application, conserve ceux des autres applications et ne cache pas les données JSON. Les images originales, les fichiers de données éditoriales, les scores, les domaines et la bannière VM Détailing de juin 2027 sont conservés.

Validation : cinq tests passent, couvrant les ressources et domaines, les articles et le filtre Mercato, les logos, les thèmes, le cache et le mode hors connexion. Huit combinaisons d’affichage sont testées de 320 à 1440 px en clair et sombre avec Chromium. Les mobiles sont émulés et les services tiers bloqués ; le site public et l’API GitHub ne sont pas accessibles depuis cet environnement.

- [Diagnostic et limites](https://github.com/Velocemercato/velocemercato.fr/blob/codex/mercato-identite-confidentialite/docs/REVUE_IDENTITE.md)
- [Aperçus mobile et ordinateur](https://github.com/Velocemercato/velocemercato.fr/blob/codex/mercato-identite-confidentialite/docs/apercus/README.md)
- [Statistiques privées : activation à décider](https://github.com/Velocemercato/velocemercato.fr/blob/codex/mercato-identite-confidentialite/STATISTIQUES_PRIVEES.md)

Revue uniquement. Ne pas fusionner ou publier sans autorisation explicite du propriétaire.
