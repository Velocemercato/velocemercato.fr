Titre : La Pastille et communication — partage fiable, rythme et créneaux Paris

Le partage pouvait perdre l’émission sélectionnée et les médias historiques étaient réattribués au dernier SHA. Le lecteur conserve l’épisode, propose les vitesses de lecture et fournit une page statique avec titre et affiche propres. Les futurs JT commencent après 0,8 seconde et utilisent une narration 12 % plus rapide, sans modifier la distribution des voix ; la musique est abaissée et le repli vocal robotique n’est plus publié. Les visuels originaux sont conservés.

La génération prévoit les trois rubriques matin/midi/soir en heure de Paris. Les spéciales exigent des matchs confirmés par les données disponibles. La production conserve le profil CDN existant ; les programmes HD longs restent des aperçus à assembler pour YouTube/Twitch, dont les intégrations ne sont pas encore réalisées. Les limites CDN et la stabilité des URL sont contrôlées.

Le workflow de communication prépare deux sélections distinctes d’articles, quiz et JT existants et peut les envoyer sur le salon Discord en réutilisant l’accès déjà configuré dans le robot de scores, avec priorité au secret GitHub. L’état est conservé sur une branche technique séparée ; un envoi incertain n’est pas réessayé aveuglément. Les autres réseaux reçoivent des exports à raccorder, sans publication simulée.

Validation : tests du site sur 320/390/768/1440 px, lecteur H.264 réel, rendu/décodage ffmpeg, assemblage des trois rubriques, horloge été/hiver, fraîcheur et publication Discord contrôlée avec réponses locales. Aucun test connecté YouTube/Twitch ou nouveau rendu vocal Piper n’est déclaré réalisé. Voir `docs/RESULTATS_PUBLICATION.txt`.

Branche intégrée : `codex/publication-validee`, après l’autorisation explicite du propriétaire de publier les éléments prêts. Les PR ne sont pas ouvertes automatiquement car le proxy bloque l’API GitHub ; le push Git reste disponible.
