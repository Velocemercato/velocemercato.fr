Titre : Automatiser les programmes longs YouTube et Twitch après connexion des comptes

Les longs JT HD ne peuvent pas être diffusés par le CDN des petits clips. Cette branche conserve des originaux 720p/24 fps depuis les mêmes images et voix, assemble les trois rubriques fraîches et transmet les programmes autorisés au workflow de diffusion. Elle implémente le raccordement OAuth, un upload YouTube reprenable avec confirmation publique après traitement, et la diffusion Twitch d’un programme enregistré sans interrompre un direct existant. Titres, descriptions, chapitres et liens proviennent des métadonnées des JT.

Les jetons et accusés sont chiffrés hors du site. Les comptes doivent être autorisés une fois avec l’outil local ; sans comptes et clé configurés, aucun rendu HD supplémentaire ni envoi externe ne se déclenche. Les quatre pages d’actualité affichent seulement les liens publics confirmés. Les contraintes Google de vidéos longues et d’autorisations API restent à vérifier sur le compte réel ; les replays Twitch dépendent des réglages de la chaîne.

Validation : tests des sessions, reprises, OAuth local PKCE, chiffrement, restrictions de compte, gardes Twitch, assemblage/décodage ffmpeg et cartes navigateur, ainsi que régressions des sites. Les API de publication sont testées avec des réponses de contrôle ; aucun compte YouTube/Twitch n’est disponible et aucun envoi réel n’est déclaré effectué. Voir `YOUTUBE_TWITCH_TESTS.txt` et `YOUTUBE_TWITCH_CONNEXION.md`.

La publication de l’intégration est autorisée par la demande du propriétaire ; les comptes restent à connecter. La création de PR par API est bloquée par le proxy, la branche de revue reste disponible.
