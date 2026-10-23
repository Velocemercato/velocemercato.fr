# Dix créneaux de JT courts, heure de Paris

| Rubrique | Créneaux quotidiens |
|---|---|
| VM Actus | 07 h, 13 h, 19 h |
| Véloce Mercato Foot | 08 h, 12 h, 20 h, 23 h |
| VM Gaming | 00 h, 10 h, 18 h |

Chaque édition est une vidéo indépendante : original HD pour YouTube, version légère dans la rubrique correspondante de velocemercato.fr. Les identifiants contiennent la rubrique, la date et l'heure du créneau ; les accusés chiffrés empêchent un deuxième envoi de la même édition. L'ancien JT groupé reste consultable.

Le robot vérifie les créneaux à :07, :27 et :47. Il produit seulement les créneaux échus depuis moins de 90 minutes qui n'ont pas encore leur rendu. GitHub Actions, la rédaction, le rendu et le traitement YouTube peuvent retarder la disponibilité : la grille indique l'heure de coupure des nouvelles, pas une garantie de diffusion à la minute. Europe/Paris gère automatiquement l'heure d'été et d'hiver, y compris le JT Gaming de minuit. Les anciens programmes longs restent disponibles en lancement manuel ; ils ne s'ajoutent plus automatiquement aux dix créneaux.

## Sources et durées

Les nouvelles brèves enregistrent leur date de création `createdAt`, en conservant la date originale `publishedAt`. La sélection utilise cette date de création (ou, pour les anciens articles sans ce champ, la date source), strictement après le précédent créneau de la même rubrique et jusqu'au créneau courant inclus. Exemple : Foot 12 h utilise la période 8 h–12 h ; Gaming 0 h utilise 18 h la veille–0 h. La production enregistre les bornes et les références sélectionnées. Une brève découverte tardivement entre donc dans le créneau de son ajout, sans être oubliée à cause de l’ancienneté de sa source. La date originale reste fournie au rédacteur pour ne pas présenter un fait ancien comme nouveau. Il n'y a plus de recours aux 24 dernières heures pour remplir un créneau séparé.

Jusqu'à huit articles sont proposés à la rédaction pour sélectionner les sujets importants. Objectif : environ trois minutes, moins si les nouvelles sont rares. Sans nouvelle exploitable, pas de bulletin artificiel. Une vidéo dépassant cinq minutes est refusée avant l'envoi, sans coupe de phrase. Aucun test de jeu n'est présenté comme notre essai personnel : le média auteur est cité. Les images de match et les vidéos tierces ne sont pas téléchargées ni réutilisées.

## Publication et reprise

YouTube reçoit une demande publique autorisée par le propriétaire ; le site n'affiche son lien qu'après confirmation de la visibilité publique par l'API. Un échec ou une limite du fournisseur conserve les accusés existants. Ne pas supprimer `broadcast-state`, réinitialiser la clé ou régénérer une vidéo pour contourner une restriction. Le quota et les limites de mise en ligne réels dépendent du projet Google et de la chaîne ; aucun quota disponible n'est inventé ici. Les vidéos YouTube peuvent rester bloquées si le fournisseur refuse l'envoi ; le succès des tests de code ne constitue pas une preuve de publication.

Pour reprendre une diffusion, relancer le workflow de diffusion avec le numéro du lancement de production réussi (artefact conservé deux jours). Pour produire explicitement une édition séparée, sélectionner un univers, `format=edition`, `edition_at=DATE_THEURE:00:00+OFFSET` correspondant à la grille et au maximum trois heures dans le passé, `publish=true`. Laisser `refaire=false` pour éviter une génération payante inutile.

## Diffuseurs officiels

`/ou-regarder.html` référence les sites officiels FIFA+, UEFA.tv, FFF TV, France.tv, CANAL+, beIN SPORTS et DAZN, ainsi que les vidéos d'éditeurs de jeux. Cette sélection n'attribue pas une chaîne à une affiche sans confirmation : les droits, le programme et le territoire doivent être vérifiés chez le diffuseur. Les liens de réseaux sociaux/Telegram ne prouvent aucune autorisation. Aucun annuaire IPTV pirate, téléchargement de match ou contournement géographique n'est ajouté.

Les accès directs aux diffuseurs sont filtrés depuis l'environnement de travail ; leur disponibilité régionale et les offres de chaque match ne sont donc pas certifiées par notre audit local.

## Installation vidéo

Le premier lancement séparé `39954095941` a échoué avant rédaction sur les miroirs APT HTTP (délai 124). L’installation est limitée aux sources Ubuntu signées, en HTTPS pour les archives et les mises à jour de sécurité, sans dépôt tiers. Les outils déjà présents sont réutilisés.
