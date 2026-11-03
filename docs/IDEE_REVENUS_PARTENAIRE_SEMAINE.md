# Idée revenus n°1 : le « Partenaire de la semaine VÉLOCE TEAM »

Proposition de Claude, 3 novembre 2026, à relire et améliorer par ChatGPT et Heineguez. **Rien n'est en vente ni publié.**

## Le constat (chiffres réels connus)

- Les offres existent déjà : `/pub/` (9,90 à 69 €/mois), VM Studio (sites 290 à 1 490 € + gérance dès 29 €/mois),
  VM Pro Local (fiche 150 € TTC), dons Stripe (`/soutenir.html`). **Aucune vente enregistrée** (`transparence.json` vide).
- Audience encore petite : chaîne YouTube « Veloce Mercato TV » 1 abonné, 1,7 k vues sur 28 jours (capture du 3 novembre).
  Nombres d'abonnés Facebook/Instagram non relevés dans le dépôt : **à vérifier avant de vendre**.
- Conséquence : la publicité au clic (AdSense) ou la monétisation YouTube rapporteraient presque rien pour l'instant
  (YouTube exige notamment 1 000 abonnés pour son programme partenaire). **L'argent viendra d'abord des commerces locaux**,
  pas des vues. Les followers servent de vitrine et de preuve.
- Atout unique : un robot publie déjà **chaque jour, tout seul**, une affiche + une story + un Reel sur 2 Pages Facebook
  et 2 comptes Instagram, avec des visuels propres. Ajouter un client ne coûte presque rien.

## L'idée

Chaque semaine, **un jour de la campagne est réservé à un commerce, artisan, club ou association de la région**
(Haute-Saône, Belfort, Doubs, Vosges) : « Le partenaire de la semaine VÉLOCE TEAM ».

Le client reçoit, en une seule fois :
1. une affiche + une story + un Reel animé à ses couleurs, au style VM, publiés sur **Véloce Mercato et VM Univers**
   (Facebook + Instagram, 4 comptes), avec la mention **« Partenariat »** ;
2. sa fiche dans **VM Services / VM Pro Local** pendant 1 mois ;
3. les fichiers (affiche, story, vidéo) **pour ses propres réseaux** : c'est ce qu'il valorise le plus.

### Prix de lancement (à valider)
| Formule | Contenu | Prix |
|---|---|---|
| Découverte | 1 jour partenaire + fichiers | **49 €** |
| Mois local | 4 jours (1/semaine) + fiche VM Pro Local | **149 €/mois** |
| Club amateur | « Le club de la semaine » payé par un sponsor du club, le club relaie | **49 €** (payé par le sponsor) |

Les **deux premiers partenaires sont offerts** en échange d'un avis et d'une autorisation de citer leur nom :
c'est la preuve dont on a besoin pour vendre aux suivants.

### Pourquoi ça peut marcher
- Le commerçant achète **du contenu prêt + de la visibilité locale**, pas des « vues » (qu'on ne peut pas garantir).
- Les clubs amateurs et leurs sponsors partagent les publications → **nouveaux followers** pour VM.
- Chaque partenaire satisfait est un prospect pour **VM Studio** (site à 290 €+, gérance 29 €/mois) : c'est là
  que se trouve le vrai chiffre d'affaires.

## Ce qu'il faut construire (petit, sur l'existant)
1. Dans `campagnes/calendrier.json`, un champ `"partenaire"` (nom, logo fourni par le client, lien) et la mention
   **Partenariat** imprimée sur l'affiche et dans le texte ; un test qui l'exige pour tout jour partenaire.
2. Une page `/partenaire/` (ou une section de `/pub/`) : exemple d'affiche, prix, formulaire qui prépare un e-mail
   (comme VM Pro Local), sans paiement sur le site.
3. Le paiement : un **lien de paiement Stripe** créé par Heineguez lui-même dans son compte (Claude/ChatGPT n'y touchent pas).

## Règles (non négociables)
- **Publicité toujours identifiée** (« Partenariat » / « Publicité ») sur l'image et le texte (loi pour la confiance dans
  l'économie numérique) ; sur Instagram/Facebook, utiliser l'outil de contenu de marque de Meta quand il s'applique.
- **Jamais** de jeux d'argent, d'alcool sans mention légale, de CBD présenté comme médicament, ni de publicité sur les pages
  mangas destinées aux enfants. **Jamais** la page RQ Pronos pour ces partenariats.
- Aucune audience, vue ou résultat promis ; seulement des publications livrées et leurs liens.
- Facturation par la structure de Heineguez (micro-entreprise jusqu'à sa fin prévue, puis la future société) :
  à confirmer par lui avant la première vente.

## Démarrage proposé (au retour de Heineguez)
1. Relever les vrais chiffres (abonnés Facebook/Instagram, portée des 2 dernières semaines de campagne) : ils iront dans l'argumentaire.
2. Construire le champ « partenaire » + la page (1 PR, tests).
3. Choisir 10 commerces via VM Services (garages, coiffeurs, snacks, clubs) ; 2 offerts, 8 contactés avec l'exemple.
4. Bilan après 4 semaines : nombre de partenaires, euros encaissés **vérifiés**, nouveaux followers.

## Autres pistes, plus tard
- Sponsoring nommé d'une rubrique (« La Pastille foot présentée par… »), avec mention claire.
- Boutique Véloce Team en impression à la demande (t-shirts au logo et au personnage Véloce), sans stock.
- Club de soutien à 2 €/mois via Stripe.
- Monétisation YouTube et AdSense : seulement quand l'audience aura grandi, et uniquement sur des contenus 100 % VM.
