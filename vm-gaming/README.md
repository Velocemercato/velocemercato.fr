# VM GAMING

Le QG gaming du Groupe VM : trouver des coéquipiers et organiser des soirées sur Warzone, Battlefield REDSEC, EA SPORTS FC et, en préparation, GTA VI.

- Maquette d'origine : ChatGPT. Relecture, corrections et tests : Claude.
- Site statique (une page `index.html` + `data/events.json`), sans compte ni base de données.
- La partie compétition EA SPORTS FC reste sur Véloce Arena : https://velocemercato.fr/gaming.html

## Règles du projet

- Aucun faux joueur, faux événement ou faux compteur.
- `data/events.json` ne contient que des rendez-vous réellement annoncés :
  `[{"date":"2026-11-06T21:00:00+01:00","titre":"Soirée Warzone","jeu":"Call of Duty: Warzone"}]`
- Aucune donnée de joueur n'est enregistrée : les annonces sont copiées puis publiées par le joueur sur Discord.
- Pas de logos, captures ou vidéos officiels des jeux. Mention de non-affiliation en pied de page.
- Rien n'est publié sans validation de Romain.

## Organisation Discord proposée

Rôles : `Foot`, `Gaming`, `Les deux`, puis un rôle par jeu (`Warzone`, `REDSEC`, `FC`, `GTA VI`), `Modérateur`.

| Catégorie | Salons |
|---|---|
| 📢 Accueil | #bienvenue · #règles · #annonces · #rendez-vous-de-la-semaine |
| 🔎 Trouver des joueurs | #cherche-groupe (coller l'annonce du site) · #présente-toi |
| 🎯 Warzone | #warzone · 🔊 Warzone Duo · 🔊 Warzone Squad |
| 💥 Battlefield REDSEC | #redsec · 🔊 REDSEC Squad |
| ⚽ EA SPORTS FC | #fc · #véloce-arena · 🔊 FC Match 1 · 🔊 FC Match 2 |
| 🚗 GTA VI (préparation) | #gta-vi |
| 💬 Général | #général · #clips · 🔊 Détente |
| 🛡️ Modération | #signalements (privé, modérateurs) |

Règles du serveur : respect, aucune donnée personnelle (adresse, téléphone, identifiants), signalement aux modérateurs, âge minimum de Discord et des jeux.

## Plus tard, seulement si la communauté grandit

Connexion Discord, annuaire de groupes avec annonces qui expirent, calendrier géré en ligne, modération et politique de confidentialité adaptée. Cela demandera un vrai hébergement avec serveur : GitHub Pages ne suffit pas.
