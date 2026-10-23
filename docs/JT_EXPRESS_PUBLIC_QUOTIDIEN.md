# JT express et publication quotidienne

La demande du propriétaire est de raccourcir les vidéos et de les publier en
public chaque jour. Les cibles restent 8 h, 12 h et 20 h, heure de Paris. La
préparation commence 75 minutes plus tôt, avec un rattrapage à l’heure cible.
La file GitHub et le traitement YouTube empêchent de garantir la minute exacte.

## Programme court

Chaque rubrique Foot, Actus et Gaming sélectionne 4 à 6 sujets sourcés, avec
380 à 480 mots. La limite stricte est de 520 mots : un dépassement déclenche
une réécriture complète, une seule fois, avant la synthèse vocale. Un second
dépassement est refusé, sans couper les phrases ou accélérer artificiellement
la voix. Les visuels, les personnages et le rythme vocal existants sont conservés.

Les trois rubriques constituent un seul JT, d’environ 8 à 10 minutes. Le rendu
mesuré est refusé au-delà de 14 minutes pour cette version. Une chaîne dont le
droit aux vidéos longues n’est pas confirmé ne reçoit aucun programme dépassant
15 minutes. Les autres formats restent indépendants de cette édition courte.

La révision `court-v1` figure dans les métadonnées et l’identifiant du programme.
L’ancien programme de midi reste dans ses accusés : il n’est ni effacé ni présenté
comme un JT court. Les trois rubriques d’un montage doivent avoir la même révision.

## Publication publique

Sur instruction du propriétaire, un nouvel upload de JT demande `privacyStatus=public`
dès `videos.insert`. Les droits existants `youtube.upload` et `youtube.readonly`
suffisent à demander cette publication puis à vérifier son résultat. Le workflow
attend le traitement et contrôle la visibilité publique avant d’ajouter le lien
aux sites. Il peut attendre jusqu’à 45 minutes ; une erreur reste un échec explicite.
Le statut technique `uploaded` confirme le transfert d’un nouvel envoi public,
sans affirmer que son traitement est terminé. Seul `published`, accompagné d’un
lien confirmé par l’API, autorise l’annonce sur les sites.

Une vidéo envoyée auparavant en privé reste une vidéo différente. Sa modification
automatique demande `youtube.force-ssl` ou une autorisation équivalente. Le propriétaire
peut aussi changer sa visibilité dans YouTube Studio. Aucun autre exemplaire n’est
envoyé pour contourner un refus de visibilité. Une éventuelle restriction API de
YouTube aux uploads privés reste bloquante et n’est jamais annoncée comme un succès.

## Remplacement demandé pour le créneau courant

Le workflow `VM - Demande de JT express` lit `.github/demande-jt.json` uniquement
lorsque ce fichier change sur `main`. La demande doit dater de moins d’une heure,
viser le jour courant et l’un des créneaux connus. Il lance le workflow de
production avec `refaire=true`, une fois, pour produire les trois nouvelles
rubriques au lieu de réutiliser les longues éditions existantes.

Les lancements programmés gardent la protection contre les doublons.
`VM_AUTO_YOUTUBE=false` reste l’interrupteur général des envois.

## Environnement de lancement

Le premier lancement express du 23 octobre a été interrompu avant toute rédaction
par le délai d’installation APT (code 124). La production, la diffusion et leurs
tests utilisent désormais explicitement Ubuntu 24.04, au lieu de dépendre du
changement en cours de l’image `ubuntu-latest`. La sauvegarde des émissions n’est
pas lancée lorsque la production a été entièrement ignorée après un échec de préparation.

L’installateur partagé essaie d’abord l’installation ciblée de FFmpeg à partir
des index déjà présents. Si leur actualisation est nécessaire, il limite APT aux
sources Ubuntu officielles et au miroir principal, avec des délais réseau bornés.
La production et les deux suites de tests exécutent le même installateur.
