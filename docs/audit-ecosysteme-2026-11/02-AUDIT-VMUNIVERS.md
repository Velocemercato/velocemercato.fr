# 02 — Audit détaillé de vmunivers.fr

## A. Positionnement commercial

### Positionnement actuel
[FAIT] Ce qui a été relevé :
- **Titre de l’accueil** : « VM Univers — projets, création de sites & communication ».
- **H1** : « Un seul univers, toutes nos passions ».
- **Contenu de l’accueil** : environ 28 cartes d’applications et de projets (VM Studio, VM Auto, VM Prono, VM Région, médias, annuaire…) et un filtre par catégorie (Tout, Pro, Local, Médias). Une bannière de consentement Metricool, ce qui est conforme.
- **L’offre B2B** se trouve sur `/professionnels/` :
  - « Votre activité. Votre image. Notre prochain projet. » ;
  - 3 axes (site, identité et supports, publicité VM) ;
  - packs de 290 à 1 490 € ;
  - démos ;
  - créations ;
  - formulaire de projet branché sur VM Studio.
- **Sitemap** : 6 adresses (accueil, découvrir, téléchargements, professionnels, connect, météo).

**Diagnostic :** l’accueil parle *de VM* (« nos passions »), pas *du client*. Un artisan qui arrive de Google voit un portail de loisirs (prono, auto, médias), pas un prestataire. L’offre existe et elle est bonne, mais elle se trouve à 1 clic et sous une page qui la dessert.

### Cible idéale
**Les TPE locales sans site ou avec un site daté, qui ont besoin d’être trouvées et contactées sur téléphone**, dans un rayon d’environ 50 km autour de la base de VM Univers ([À COMPLÉTER] : Belfort / Montbéliard ?), et partout en France à distance.

Ordre de priorité, du plus au moins prioritaire :
1. Métiers de la réservation : coiffeur, beauté, restaurant, snack, garage.
2. Artisans du bâtiment.
3. Clubs et associations sportives (lien naturel avec le foot).
4. Indépendants et créateurs.

### 3 personas

| Persona | Profil | Douleur | Déclencheur | Ce qu’il achète |
|---|---|---|---|---|
| **Karim, snack / pizzeria** | 30-45 ans, gérant, tout passe par le téléphone | Commandes au téléphone, commissions des plateformes, pas de site | « Je paie des commissions », « les clients ne trouvent pas mes horaires » | Site Business avec commande en ligne + carte QR + fiche Google |
| **Léa, coiffeuse / esthéticienne** | 25-40 ans, indépendante ou petit salon, très Instagram | Rendez-vous par message, oublis, pas de vitrine pro | « Je passe mes soirées à répondre aux DM » | Site avec agenda + rappels SMS + identité (logo, carte) |
| **Patrick, président de club amateur** | 45-65 ans, bénévole | Infos éparpillées, recherche de sponsors, inscriptions papier | Début de saison, recherche de partenaires | Site club + flyers + kit sponsors (et lien avec Véloce Mercato pour la visibilité) |

### Promesse claire
> **« Votre site et votre image pro, à prix fixe. Vous voyez le résultat en direct avant de payer. »**

Sous-promesse : *« Pensé pour le téléphone, prêt à être trouvé sur Google, sans abonnement obligatoire. »*

### Positionnement différenciant
1. **Le direct** : l’atelier en ligne montre le site, la carte ou le flyer qui se construisent, avec le prix affiché. Les agences envoient des maquettes PDF.
2. **Des prix fixes et écrits** : 4 packs, des options à prix affiché, 50/50, et rien de caché.
3. **Des démos métier à tester** : 11 démos (coiffeur, snack, garage…) où l’on réserve et commande comme un vrai client.
4. **La culture locale et sportive** : clubs, commerces de quartier, visibilité possible sur le média Véloce Mercato (offre séparée).

### Accroche proposée
**« VM Univers — le studio qui vous montre avant de vous facturer. »**

Variante plus locale : **« Votre commerce, en ligne et en vrai. »**

### Positionnement à éviter
- « Agence digitale 360° », « solutions innovantes », « transformation digitale » : générique, et pas crédible pour une petite structure.
- « Un seul univers, toutes nos passions » en page d’accueil : ça parle de VM, pas du client.
- Mélanger le studio avec les pronostics, l’auto ou les médias dans le même parcours.
- Promettre des résultats (« +200 % de clients ») sans preuves.

### Hiérarchie des services
1. **Site internet** (cœur, 70 % de l’effort commercial).
2. **Identité visuelle et supports imprimés** (logo, carte, flyer : ventes rapides, porte d’entrée).
3. **Visibilité locale** (fiche Google, kit réseaux, animation, publicité sur le réseau VM).

---

## B. Architecture du site recommandée

```
vmunivers.fr/
├── /                                Accueil commercial
├── /creation-site-internet/         Service 1
├── /identite-visuelle/              Service 2 (logo, carte, flyer, charte)
├── /communication-publicite/        Service 3 (fiche Google, réseaux, publicité VM)
├── /realisations/                   Portfolio + études de cas
│   └── /realisations/[projet]/
├── /demos/                          Les 11 démos métiers (lien vers velocemercato.fr/demos/ ou copie)
├── /tarifs/                         Toutes les grilles au même endroit
├── /methode/                        Process en 5 étapes (peut être une section de l'accueil)
├── /a-propos/
├── /conseils/                       Blog (2 articles par mois maximum)
├── /faq/
├── /devis/                          Formulaire + prise de rendez-vous
├── /creation-site-internet-[ville]/ Pages locales (2 à 3 maximum, pas de page vide)
├── /projets-vm/                     L'annuaire actuel des projets VM (déplacé)
├── /mentions-legales/  /politique-de-confidentialite/  /cgv/
```

**Pour chaque page :**

| Page | Objectif | Intention / mots-clés | CTA principal | CTA secondaire | Contenu obligatoire | Preuve | À éviter |
|---|---|---|---|---|---|---|---|
| Accueil | Faire comprendre l’offre en 5 s et générer des devis | « création site internet [ville] », « site pour commerce » | Demander un devis | Essayer l’atelier en direct | Promesse, 3 services, prix « dès », démos, méthode, réalisations, FAQ courte | Démos testables, réalisations VM, prix écrits | Annuaire de projets en haut, pronos |
| Création de site | Vendre les 4 packs | « création site vitrine », « site internet artisan / restaurant » | Choisir mon pack | Tester une démo | Packs, ce qui est inclus ou non, délais, process, FAQ | Démos, 50/50, domaine au nom du client | Jargon technique |
| Identité visuelle | Vendre logo, carte et flyer | « création logo », « carte de visite », « flyer » | Créer ma carte en direct (atelier) | Devis identité complète | Offres, exemples (kit manga VM, VM Detailing) | Exemples imprimés | Promesse « logo IA » sans contrôle humain |
| Communication et publicité | Vendre la visibilité locale | « fiche Google My Business », « gestion réseaux sociaux commerce » | Demander un audit gratuit de ma fiche Google | Voir le kit réseaux | Fiche Google, kit réseaux, animation, publicité sur le réseau VM | Exemples de posts | Promettre des abonnés ou un classement |
| Réalisations | Prouver le savoir-faire | « exemples sites commerces » | Je veux le même | Tester la démo | Études de cas (projet, besoin, solution, résultat mesuré **ou** « à mesurer ») | Captures, liens vivants | Faux clients, faux avis |
| Tarifs | Lever l’objection prix | « prix site internet », « tarif création site vitrine » | Demander un devis | Voir les démos | Packs, options, maintenance, 50/50, ce qui est séparé | Transparence | Prix « à partir de » sans détail |
| Devis | Recueillir des demandes qualifiées | — | Envoyer ma demande | Appeler / WhatsApp | Formulaire court, délai de réponse, RGPD | « Réponse sous 48 h ouvrées » (si tenu) | Formulaire de 20 champs |
| À propos | Créer la confiance | « VM Univers » | Voir les réalisations | Devis | Qui, pourquoi, méthode, SIRET, zone | Visage ou nom, SIRET | Récit vague |
| FAQ | Répondre aux objections | Questions « combien coûte… », « combien de temps… » | Devis | Tarifs | 12 à 15 questions | — | Réponses évasives |
| Pages locales | SEO local | « création site internet Belfort » | Devis | Démos | Contenu propre à la ville (clients, zone, déplacements) | Projets locaux | Pages copiées-collées avec juste le nom de la ville |

---

## C. Offres et tarification (résumé, détail dans le fichier 10)

[FAIT] Il existe aujourd’hui trois grilles :
- les packs web-studio (Mini 290 €, Starter 590 €, Business 990 €, Max 1 490 €) ;
- l’atelier express (site 290, 410 ou 540 €, carte 29 €, flyer 39 €, affiche 49 €, post 19 €) ;
- vmunivers (« Carte QR 49 € », « VM Pro Local dès 9,90 €/mois »).

**Recommandation :**
- **Une seule grille de référence** sur `/tarifs/`, avec 3 offres principales et un Pack VM.
- **L’atelier en ligne devient l’« entrée rapide »** pour les visuels seuls (carte, flyer, post). Pour les sites, l’atelier renvoie vers les packs. Il faut aligner `prix.js` sur Mini, Starter et Business, ou présenter clairement l’atelier comme une « version express sans rendez-vous ».
- Les 3 offres et le Pack VM sont détaillés dans le fichier 10.

---

## D. Conversion

| Constat | Action | Priorité | Effort | KPI |
|---|---|---|---|---|
| [FAIT] Le formulaire `/professionnels/` est branché sur VM Studio (`/api/demande`), avec consentement et anti-spam | Le garder ; ajouter « budget » et « délai souhaité » (qualification) ; afficher le délai de réponse | Haute | Faible | Taux de conversion du formulaire |
| [FAIT] Pas de numéro de téléphone ni de WhatsApp visible | Ajouter un bouton WhatsApp Business si tu l’acceptes (beaucoup de TPE préfèrent) | Haute | Faible | Contacts WhatsApp |
| [FAIT] Pas d’avis clients | Récolter les avis Google des premiers clients ; ne **jamais** inventer de témoignage | Haute | Moyen | Nombre d’avis |
| [FAIT] Les démos sont sur velocemercato.fr | Les présenter sur vmunivers.fr (`/demos/`) avec le libellé « démo VM Univers » | Moyenne | Faible | Clics vers les démos |
| [HYPOTHÈSE] Pas de prise de rendez-vous | Lien vers un agenda (Cal.com gratuit) « Appel de 15 min » | Moyenne | Faible | Rendez-vous pris |

---

## E. SEO technique de vmunivers.fr

| Point | Constat | Action | Priorité | Effort |
|---|---|---|---|---|
| Sitemap | [FAIT] 6 adresses, dont météo et connect | Ne garder que les pages commerciales + réalisations + conseils | Haute | Faible |
| Données structurées | [FAIT] Aucune | `ProfessionalService` (nom, zone, SIRET, prix « à partir de »), `FAQPage`, `BreadcrumbList` | Haute | Faible |
| Titles | [FAIT] Corrects, mais orientés « projets VM » | Accueil : « Création de site internet et identité visuelle pour commerces — VM Univers » | Haute | Faible |
| Polices | [FAIT] Google Fonts externes | Les héberger sur le site | Moyenne | Faible |
| Pages hors sujet indexées | [FAIT] `/meteo/`, `/connect/`, `/telechargements/` | `noindex` ou retrait du sitemap | Moyenne | Faible |
| Mentions légales et confidentialité | [FAIT] Renvoi vers les mentions de velocemercato.fr ; pas de page confidentialité | Pages propres à vmunivers.fr (fichier 10) | Critique | Faible |
| CGV | [FAIT] Absentes, alors qu’il y a vente et paiement Stripe | Page `/cgv/` (prestations, 50/50, rétractation, délais, propriété) | Critique | Moyen |
