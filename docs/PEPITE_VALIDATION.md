# Pépite FC : valider une fiche joueur

Les fiches arrivent par e-mail sur `velocemercato.fr@gmail.com`. Rien n’est publié sans validation.

## Avant de publier
1. Vérifier que le joueur est mineur ou majeur : si mineur, l’accord écrit du représentant légal doit être présent. Sans accord, ne pas publier.
2. Ne jamais publier nom de famille, adresse, téléphone, e-mail ni photo d’identité. Seuls prénom, catégorie, poste, ville, club et liens vidéo sont affichés.
3. Vérifier chaque lien : seuls YouTube, Vimeo et Google Drive sont acceptés par le site.
4. Refuser les fiches fausses, injurieuses ou demandant de l’argent aux familles.

## Publier une fiche
Ajouter un objet dans `pepite/dossiers.json` :

```json
[
  {"prenom": "Léo", "nom": "Martin", "categorie": "U15", "poste": "Milieu", "ville": "Belfort", "club": "", "scolaire": "3e", "videos": "https://youtu.be/abc123 https://vimeo.com/42"}
]
```

Le champ `nom` n’est pas affiché : il sert seulement à retrouver la fiche. Les champs `videos` acceptent plusieurs liens séparés par un espace.

## Demandes pro
Les demandes de recruteurs et agents arrivent aussi par e-mail. Vérifier l’accréditation d’agent ou la licence avant toute mise en relation.
