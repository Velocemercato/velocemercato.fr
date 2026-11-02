# VM Multisport — le site se transforme selon le sport

## Première version
- `/multisport/?sport=nba` : basket NBA ; `?sport=nfl` : NFL ; `?sport=f1`, `?sport=motogp`, `?sport=tennis`, `?sport=rugby`, `?sport=cyclisme`.
- Le Football historique reste sur la page d'accueil `/` ; un sélecteur y donne accès aux autres univers et rappelle le sport enregistré.
- Tous les sports utilisent le même site `velocemercato.fr` et le même moteur. Thème, titres, lien calendrier/résultats, vidéos et choix d'alertes changent à chaque clic sans rechargement de la sous-page.
- Sport préféré conservé dans `localStorage` sur cet appareil (aucune inscription ni suivi côté serveur).
- `/multisport/actualites.json` est alimenté par `tools/multisport_flux.py` : titres Google News RSS, attribution à l'éditeur, liens, publication datée, fenêtre maximale 7 jours. Pas de réécriture fictive des brèves ou réhébergement des textes. Le robot s'exécute plusieurs fois par jour ; disponibilité variable.
- **Résultats/programmes** : liens vers les sources officielles. NBA : widget scores TV Sports, NFL/F1/MotoGP : widget programme TV Sports (chargé seulement sur clic, pas présenté comme résultats). Les autres sports proposent les résultats officiels via liens.
- **Vidéos** : liens vers chaînes officielles. La Pastille multisport doit être créée éditorialement sport par sport, non simulée. Ne jamais diffuser des extraits de matchs sans droits.
- Notifications : mêmes préférences que le Centre d'alertes VM, avec 7 nouvelles catégories. Pour l'instant elles ne s'affichent que pendant qu'une page VM est ouverte. Le push hors site demande un service serveur et l'accord du visiteur.

## Rubriques éditoriales par sport
La page propose désormais **À la une**, **France**, **Europe**, **International** et un tour d'horizon en trois colonnes. Ces rubriques fonctionnent avec tous les sports, avec des intitulés personnalisés (NBA : Français/Européens ; F1 : pilotes français et Grands Prix européens ; rugby : Top 14/XV de France, etc.).

La catégorisation est volontairement prudente : seuls des mots et noms explicites présents dans le titre de presse donnent les étiquettes `france` et `europe`. Un événement aux États-Unis concernant un Français peut être classé dans « France » pour le suivi des sportifs français ; il ne s'agit pas de prétendre que le match se déroule en France. Le fil « International » est le panorama global du sport sélectionné. Les titres sans signal géographique restent dans « À la une » et « International ».

Si la rubrique est vide, elle l'annonce clairement au lieu de fabriquer une information. Chaque onglet peut être partagé par URL (`?sport=nba&rubrique=france`). Les titres récents restent limités à sept jours, affichés avec la date et la source, et ouvrent le lien de l'éditeur.

## Points d'amélioration
1. Acheter ou négocier un flux score/licence par sport si besoin d'affichage de résultats en direct dans l'interface sans widget tiers.
2. Ajouter un générateur **original** de La Pastille basket, NFL, F1, MotoGP, avec validation éditoriale des informations et respect des droits vidéo, puis publier seulement des éditions vraiment créées.
3. Renforcer la personnalisation des compétitions, équipes favorites, calendrier et classements avec un compte optionnel ; ne pas collecter de préférences sans consentement.
4. Tester la fiabilité des titres RSS (dédoublonnage, pertinence, faux titres d'autres sports) avant d'en faire une automatisation commerciale.
5. Les termes « live », « score en direct » et « JT disponible » ne doivent être affichés que si une source le confirme.

Conserver le dossier `/sport/` existant : il correspond aux randonnées et entraînements, différent de la rubrique d'information multisport.
