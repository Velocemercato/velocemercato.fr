# Reprise du JT de midi du 23 octobre 2026

La production des trois éditions de midi a réussi :
https://github.com/Velocemercato/velocemercato.fr/actions/runs/39938756164

L’envoi suivant a échoué avant tout appel YouTube, avec l’annotation :
« Le programme long nécessite les vrais originaux HD ; aucun ancien fichier comprimé substitué. »
https://github.com/Velocemercato/velocemercato.fr/actions/runs/39940005274

## Cause et correction

La copie directe des trois MP4 additionne des durées audio/vidéo arrondies différemment.
La fréquence moyenne du résultat n’est donc plus exactement `24/1`, même lorsque chaque
source est à 24 images/seconde. Reproduction réelle : trois clips HD de 2,317 s,
3,131 s et 1,929 s donnent `1087488/45349` après concaténation avec copie directe.

Le programme destiné à la diffusion vérifie maintenant chaque source HD avant
l’assemblage. Il reconstruit une chronologie régulière à la fréquence des originaux,
conserve la piste audio et prolonge la dernière image jusqu’à la fin du son.
Les originaux restent intacts ; un clip CDN à 12 images/seconde est refusé avant
cette opération. Le contrôle final de définition et de cadence reste actif.

L’encodeur des futures émissions utilise aussi un filtre `fps` explicite : `-r`
seul ne garantit pas que la dernière carte reste présente sur toute sa durée.
La durée vidéo de la conclusion est désormais testée, en plus de la durée audio.

## Reprise sans recréer les émissions

Le fichier `.github/reprise-diffusion.json` permet de demander explicitement une
reprise en le modifiant sur `main`. Seule cette modification déclenche la reprise ;
un changement de code seul ne relance pas une publication. La demande expire après
une heure. Les vérifications existantes continuent à imposer un lancement source
réussi sur `main`, ses propres originaux et une autorisation de production de moins
de trois heures. Les accusés chiffrés empêchent les doublons déjà confirmés.

Les options d’activation YouTube/Twitch, la vérification de chaîne, la visibilité
publique autorisée et la confirmation par la plateforme restent nécessaires.
Une génération réussie ne prouve pas une publication YouTube.

La première reprise du 23 octobre a terminé sans erreur, mais sans lien public
dans l’index. Le workflow des JT active désormais explicitement
`VM_YOUTUBE_PUBLIC=true`, conformément à la demande de publication automatique
du propriétaire. `VM_AUTO_YOUTUBE` reste l’interrupteur général ; la vérification
de chaîne et la confirmation du traitement et de la visibilité publique restent
obligatoires. Un accusé privé déjà enregistré est réutilisé sans nouvel envoi.
Le statut contrôlé et les liens effectivement publics apparaissent aussi dans
les annotations GitHub. Les diagnostics des vidéos de présentation ne montrent
plus de fragment d’identifiant secret.

Le raccordement OAuth demande désormais aussi `youtube.force-ssl`, droit accepté
par `videos.update`. Les deux anciens droits (`youtube.upload` et `youtube.readonly`)
permettent l’envoi privé mais pas cette modification de visibilité. Un jeton déjà
créé ne gagne pas de droit sans une nouvelle autorisation Google du propriétaire.

## Vérifications

- 24 tests de diffusion, dont l’assemblage réel de durées fractionnaires, le refus des sources CDN,
  l’absence de fragments secrets dans les diagnostics et le droit de publication dans le lien OAuth.
- 11 tests de production, dont la durée vidéo complète et les deux profils.
- Reprise locale de trois fichiers créés par l’ancien encodeur : cadence constante et décodage complet.
- Aucun test local ne contacte les comptes ni ne publie une vidéo.
