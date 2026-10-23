# La Pastille : échec du JT Actus du 23 octobre 2026

## Cause constatée

Le run [39911456375](https://github.com/Velocemercato/velocemercato.fr/actions/runs/39911456375), lancé le 23 octobre à 06:26 UTC, s’est terminé en échec après 38 minutes et 18 secondes pour le job. Le fichier `studio/emission-log.txt`, enregistré par le commit `67dfc720` à 07:04 UTC, indique :

- Foot : émission du matin publiée.
- Actus : fichier `actus-edition-20261023-0857.mp4` refusé, car il dépasse la limite jsDelivr de 20 000 000 octets.
- Gaming : émission du matin publiée.

Le message GitHub « All jobs have failed » concerne l’unique job du workflow ; il ne signifie pas que les deux sites ou toutes les vidéos sont indisponibles. Le run suivant, terminé en quinze secondes, correspond à une plage sans production : il ne prouve pas qu’un nouvel Actus a été produit.

## Corrections

1. Pour le profil CDN de plans fixes, les images clés complètes ne sont plus répétées toutes les deux secondes : l’intervalle maximal devient dix secondes. La définition 1280 × 720, la cadence de 12 images par seconde, le CRF, les réglages audio et le démarrage progressif restent identiques. Les changements de scène restent gérés par l’encodeur. Le profil HD est inchangé. Un saut dans la vidéo peut nécessiter de décoder davantage de secondes depuis la précédente image clé.
2. Une limite de transport devient une exception distincte. Elle ne se confond pas avec un fichier absent, une panne d’écriture, de synthèse vocale ou d’envoi Git.
3. Si un rendu terminé dépasse encore la capacité CDN, le MP4, le poster, l’audio, les métadonnées et le script sont conservés dans `studio/tmp/a-heberger/`. Le workflow les enregistre dans l’artefact `pastille-a-heberger`, disponible deux jours. L’artefact est créé avant le nettoyage du dépôt par le workflow.
4. L’émission en attente n’est ni déclarée publiée, ni ajoutée aux listes et pages publiques. Les émissions déjà publiées restent inchangées. Le résumé GitHub distingue publication, attente d’hébergement, aperçu, absence de nouvelle émission et panne réelle.
5. Quand la diffusion longue est effectivement configurée et autorisée, les originaux HD et leurs métadonnées restent disponibles pour le programme complet, même si un fichier CDN est trop volumineux. La limite CDN ne bloque plus à elle seule cette voie. Les contrôles existants de fraîcheur, de lot complet et d’autorisation demeurent requis.
6. Les pannes réelles font toujours échouer le traitement. Une attente d’hébergement est signalée explicitement par un avertissement ; elle ne devient pas une publication fictive. Une production sautée par le calendrier est désormais expliquée dans le résumé du workflow.

## Validation

- Onze tests existants de production passés : calendrier Paris, garde-fous, voix sans repli silencieux, vraie vidéo H.264/AAC, deux profils, synchronisation, démarrage progressif, assemblage et pages de partage.
- Cinq tests de reprise passés : vidéo trop grosse conservée sans envoi Git, fichier public inchangé, originaux HD conservés, absence de connexion sans faux original HD, confirmation de publication avant marquage public, et bilan différencié des résultats. Une panne d’envoi reste une erreur.
- Vingt et un tests de diffusion passés avec comptes et envois simulés. Aucun compte social réel n’est contacté par ces essais.
- Comparaison réelle de huit minutes, avec quatre plans du décor Actus et un audio de contrôle : 22 574 308 octets avant, 8 165 826 octets après, soit environ 63,8 % de moins. Le même exemple dépasse la limite avant la correction et passe après. Les deux fichiers ont été entièrement décodés par ffmpeg, à 1280 × 720 et 12 images par seconde, avec la même durée de 480 secondes.

Cette comparaison est une mesure sur une vidéo de contrôle, pas sur le JT Actus perdu du runner. Le gain dépend des images, des changements de scène et de la durée ; il ne garantit pas que tous les programmes longs tiendront sous 20 Mo. Le repli vers un hébergement adapté reste nécessaire au-delà de la capacité.

Un workflow de tests Pastille sans publication est ajouté pour vérifier automatiquement la production et la reprise lors des prochains changements.

## Vérification après déploiement

Le correctif s’applique aux prochaines productions. Le fichier Actus du run en échec n’a pas été récupéré ou republié par ces tests. Les tests de comptes simulés ne certifient pas la connexion réelle des comptes YouTube ou Twitch. Un run de tests réussi ou une exécution sans production ne doit pas être présenté comme un JT diffusé.

Si un nouvel avertissement de capacité apparaît : ouvrir l’exécution de production, consulter son résumé et récupérer l’artefact `pastille-a-heberger` pendant ses deux jours de conservation. Il contient le rendu prêt à héberger ; la vidéo ne doit être annoncée disponible sur une plateforme qu’après confirmation de son envoi.
