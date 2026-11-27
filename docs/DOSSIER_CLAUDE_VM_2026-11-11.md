# Dossier Claude — Véloce Mercato, site et réseaux

État établi le 2026-11-27T17:35+01:00.

Ce dossier remplace les anciennes consignes de restauration intégrale et les anciennes cadences. Il décrit le travail autorisé par Romain dans cette conversation. Les accès et conversations de ChatGPT ne sont pas automatiquement accessibles dans Claude.

## Guide des accès pour Claude

Lire [ACCES_CLAUDE_VM_2026-11-11.md](ACCES_CLAUDE_VM_2026-11-11.md) : dépôts, Cloudflare, connexions Meta, marque Metricool, programmateur TikTok, contrôles et accès à connecter dans Claude. Aucun secret n’est inclus et aucun accès Claude n’a été créé automatiquement.

## Priorités et périmètre

- Conserver l’accueil bureau et tous les boutons validés. Le site vitrine vmunivers.fr conserve sa présentation : seul son tableau de réseaux a été modifié à la demande suivante de Romain.
- Le volet Foot propose « Ouvrir la rubrique complète » vers https://velocemercato.fr/foot/. Cette page reprend index.html du commit d488e7e20ea3db047e026465139156f5dd109445, dernier changement de cette page avant 21 h Paris le 4 novembre 2026. Ses fichiers JSON sont les flux actuels, pas les informations figées du 4 novembre.
- Vérifier la rubrique Foot et ses lecteurs sur téléphone avant toute autre refonte. Ne pas remplacer le bureau par l’ancien accueil.
- Les conseils pronos restent gérés avec Romain ; le pouf VM Prono ouvre https://t.me/VMCONSEILSPRONOS. Ne pas inventer de conseil ou de résultat.

## Carte des accès du bureau

| Élément | Destination |
|---|---|
| Logo VM rond près du titre | https://vmunivers.fr/ |
| Micro | Facebook Véloce Mercato |
| Fauteuil, plaque Facebook VMunivers.fr | Facebook VM Univers |
| Globe, plaque Facebook VM Actus Pronos | Facebook VM Actus et Pronos |
| Pouf VM PRONO · TELEGRAM | https://t.me/VMCONSEILSPRONOS |
| Cadres | Foot, Multisport sans Foot, Actus et régions, Gaming, Manga & Séries, Studio, Pastilles |
| Réseaux en bas | Les deux Facebook et les Instagram/TikTok ajoutés par Romain ; YouTube, Snapchat, Discord, Twitch conservés |

## Correction complémentaire du tableau VM Univers

Sur vmunivers.fr, Romain a demandé : première case à gauche Facebook https://www.facebook.com/share/1FEt9Kprhi/ ; quatrième case à gauche Facebook VM Actus et Pronos https://www.facebook.com/share/1KCGttXow1/ ; cinquième case à droite TikTok https://www.tiktok.com/@vmunivers.fr. Il a confirmé que le deuxième lien était bien Facebook. Le reste de la vitrine est conservé. La correction est dans Velocemercato/vmunivers, commit 262e40c324ef3eb8bbd9ca028cb5286433ec4746.

## Publications dont les liens sont confirmés

| Destination | Nombre relevé dans les reçus de cette reprise |
|---|---|
| Véloce Mercato · facebook | 190 |
| Véloce Mercato · instagram | 127 |
| VM Actus et Pronos · facebook | 193 |
| VM Univers · facebook | 5 |
| VM Univers · instagram | 1 |

Ces nombres comptent les identifiants uniques avec confirmation et URL publique. Un statut programmé, envoi ou workflow réussi ne suffit pas. Les reçus détaillés sont dans studio/editorial-status.json et dans le kit https://velocemercato.fr/studio/kit-automatique.html.

## Programme actif et responsabilités

| Canal | Responsable technique | Objectif demandé |
|---|---|---|
| Facebook Véloce Mercato | editorial-vm.yml, connexion meta | Article Foot ou Multisport toutes les 10 minutes, 24 h/24 |
| Facebook VM Actus | editorial-vm.yml, connexion meta_pronos | Actualités variées toutes les 10 minutes, 24 h/24 |
| Facebook VM Univers | editorial-vm.yml, connexion meta_univers | Un projet chaque heure, 24 h/24 |
| Instagram veloce.mercato | Même circuit, identité vérifiée | Un contenu sport toutes les 15 minutes selon quota |
| Instagram vmunivers.fr | Même circuit, identité vérifiée | Un projet toutes les 15 minutes selon quota |
| Troisième Instagram | Aucun | Identité et connexion à fournir ; aucun envoi vers un compte supposé |
| TikTok @velocemercato | Tâche ChatGPT/Metricool b430a95c… | Trois vidéos par bloc, 9 h / 12 h / 20 h Paris, neuf par jour si disponibles |
| Rendus vidéo | teasers-vm.yml + chaîne des JT existante | Flashes originaux, voix Piper et musique VM, puis ajout au kit |
| YouTube | Workflows existants | Les JT existants sont conservés ; la production de flashes n’ajoute pas neuf uploads YouTube |
| Conseils pronos, choix éditoriaux et validation artistique | Romain | Garder sa maîtrise |

Un seul expéditeur TikTok est retenu : la tâche Metricool. Le workflow tiktok-metricool.yml reste un diagnostic privé. Ne pas le réactiver en production en parallèle. Les envois ont un accusé avant l’appel API ; une réponse ambiguë n’est jamais relancée automatiquement. Les anciens circuits d’articles cèdent la main uniquement après confirmation de la connexion du nouveau circuit. Les JT/Reels, campagnes et conseils existants gardent leurs propres reçus.

Les cadences sont des objectifs, pas une promesse de remplissage. Les plafonds de rédaction actuels restent 48 brèves Foot, 36 Actus et 16 Gaming par jour, plus les titres Multisport. S’il manque du contenu inédit ou un quota, laisser le créneau vide. GitHub peut retarder ses cron. Les quotas Instagram sont vérifiés au moment des envois.

## Sources envoyées par Romain

Les 30 références sont transcrites dans sources/demandees-romain.json. Les résultats de contrôle sont dans sources/flux-valides.json. Aucune source existante n’a été supprimée. Les ajouts ne sont activés qu’après validation du flux et respect des accès autorisés. L’Équipe, CIES et Reuters demandent une revue éditoriale ou contractuelle ; aucun accès payant n’est contourné. Les titres étrangers nécessitent une rédaction française, sans copie intégrale.

| Source | Résultat actuel |
|---|---|
| Jeuxvideo.com | deja_configuree_acces_non_verifie |
| Gamekult | deja_configuree_acces_non_verifie |
| IGN France | robots_ou_acces_non_autorise |
| Gameblog | robots_ou_acces_non_autorise |
| Canard PC | robots_ou_acces_non_autorise |
| L’Équipe | validation_editoriale_requise |
| Eurosport Football | robots_ou_acces_non_autorise |
| Goal | robots_ou_acces_non_autorise |
| Foot Mercato | valide |
| So Foot | robots_ou_acces_non_autorise |
| Top Mercato | robots_ou_acces_non_autorise |
| Maxifoot | robots_ou_acces_non_autorise |
| Observatoire CIES | validation_editoriale_requise |
| Le Monde | robots_ou_acces_non_autorise |
| Le Figaro | robots_ou_acces_non_autorise |
| Libération | robots_ou_acces_non_autorise |
| 20 Minutes | deja_configuree_acces_non_verifie |
| franceinfo | deja_configuree_acces_non_verifie |
| Ouest-France | deja_configuree_acces_non_verifie |
| BFMTV | robots_ou_acces_non_autorise |
| France 24 | deja_configuree_acces_non_verifie |
| Reuters | validation_editoriale_requise |
| Le Point | robots_ou_acces_non_autorise |
| ESPN | robots_ou_acces_non_autorise |
| Sports.fr | robots_ou_acces_non_autorise |
| Le Monde Sport | robots_ou_acces_non_autorise |
| Marca | robots_ou_acces_non_autorise |
| La Gazzetta dello Sport | robots_ou_acces_non_autorise |
| Corriere dello Sport | robots_ou_acces_non_autorise |
| Tuttosport | robots_ou_acces_non_autorise |

Pour Multisport, les flux français validés Sports.fr et Le Monde Sport sont raccordés. Les autres sources étrangères restent au catalogue pour ajout de la traduction dans la chaîne éditoriale. La dernière lettre isolée « S » de la photo multisport n’a pas été interprétée comme un média.

## Audit des pages, liens et classements

- Pages HTML examinées : 2132.
- URL interrogées : 2419.
- HTTP 404/410 confirmés : 14.
- Cibles internes absentes du dépôt : 86.
- Liens protégés/non vérifiables automatiquement : 867.
- Ancres à relire : 60. Certaines existent seulement après chargement JavaScript.
- Classements à relire : 0.

Le détail exhaustif des contrôles effectués, avec fichiers et lignes, est dans docs/AUDIT_CLAUDE_2026-11-11.json et son résumé Markdown. Un refus 403/429 ne prouve pas un lien mort. Cet audit ne certifie pas tous les faits d’actualité, la disponibilité géographique des vidéos, les paiements ou les espaces authentifiés.

## Vidéos, référence musicale et reste à faire

Le dernier rendu répertorie 3 nouveaux flashes, bloc 2026-11-25T20:00:00+01:00. Lire studio/teasers.json pour les URLs réelles.

Lire docs/CLAUDE_VIDEO_VM_2026-11-11.md : référence fournie, storyboard, paroles originales proposées, format de livraison, accès CapCut non vérifié, chant encore à produire et dixième clip promotionnel non programmé. Les neuf créneaux TikTok ne constituent pas neuf confirmations de publication.

## Reprise concrète pour Claude

1. Lire main et ce dossier ; conserver les changements récents des autres assistants. Ne pas faire de restauration globale ni de force-push.
2. Contrôler /foot/ : visuel du 4 novembre, flux du jour, ouverture des articles, filtres, scores, mobile, lisibilité et lien retour. Tester aussi le clic au doigt sur les cadres SVG du bureau : un ancien test de centre géométrique avait ouvert un autre volet, même si le clavier sélectionnait le bon.
3. Corriger les vrais liens morts, puis les cibles internes et ancres réellement manquantes. Lire les références du JSON ; ne pas supprimer un lien protégé sur la seule base de 403/429.
4. Relire les articles signalés, notamment un ancien One Piece mal placé dans Gaming. Le filtre Multisport exclut les jeux vidéo et ne charge plus les brèves Foot. Vérifier les cartes anciennes de type Coupe du monde de rugby 2023 dont un RSS annonce une date récente.
5. Vérifier les réservations et URLs de chaque réseau avant toute action ; ne pas remplacer la clé de l’état chiffré, ni effacer les reçus pour recommencer un lot.
6. Identifier le troisième Instagram avec Romain et vérifier son droit de publication avant de le raccorder. Les deux identités confirmées sont veloce.mercato et vmunivers.fr.
7. Améliorer les nouvelles animations et produire le refrain chanté original, puis le dixième clip promotionnel. Vérifier les propres accès de Claude à Metricool, GitHub et, si nécessaire, CapCut. Ne pas annoncer un accès hérité de ChatGPT.
8. Refaire les tests concernés, publier via deployer-accueil-cloudflare.yml, contrôler le domaine public et actualiser ce dossier à partir des reçus.

## Liens des publications confirmées

- meta/facebook —  — https://www.facebook.com/122106465861520366/posts/122113259493520366
- meta/facebook — "C'est un honneur que le Mali intègre World Rugby", apprécie l'international français et malien Camara - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122112749895520366
- meta/facebook — AC Milan : Gonçalo Ramos traverse une passe très difficile devant le but — https://www.facebook.com/122106465861520366/posts/122113068327520366
- meta/facebook — AS Monaco : Filipe Luis répond aux propos de Folarin Balogun — https://www.facebook.com/122106465861520366/posts/122112937077520366
- meta/facebook — ASSE à Reims : des supporters stéphanois interdits de déplacement veulent malgré tout se rendre au stade — https://www.facebook.com/122106465861520366/posts/122112988269520366
- meta/facebook — Acosta peine avec le ressenti du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112785811520366
- meta/facebook — Adrien Rabiot évoque à nouveau son départ de l’OM, qu’il dit avoir tourné la page — https://www.facebook.com/122106465861520366/posts/122113167927520366
- meta/facebook — Affaire Negreira : Florentino Pérez attaque le Barça et Javier Tebas — https://www.facebook.com/122106465861520366/posts/122112972123520366
- meta/facebook — Alex Marquez domine la séance d'essai au Portugal tandis que Martin se qualifie pour la Q2 à la dixième place, avec les dix premiers coureurs séparés par seulement quatre dixièmes - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112845601520366
- meta/facebook — Alex Marquez prend la tête des essais MotoGP au Portugal lors de son retour après une opération de l'épaule - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112766275520366
- meta/facebook — Alexander Zverev rejoint sans surprise Carlos Alcaraz en finale du Masters de Turin - franceinfo — https://www.facebook.com/122106465861520366/posts/122113079799520366
- meta/facebook — Alexandre Lafitte prend en charge Al-Hilal au Soudan, dans un contexte de guerre civile — https://www.facebook.com/122106465861520366/posts/122112919353520366
- meta/facebook — Alicia Keys et John Legend annoncés, possible apparition de Rihanna : le show de la mi-temps du Super Bowl de Jay-Z se précise - L'Équipe — https://www.facebook.com/122106465861520366/posts/122113009233520366
- meta/facebook — Angers SCO : Mael Gernigon, 17 ans, déjà titulaire face à l'OM en Ligue 1 — https://www.facebook.com/122106465861520366/posts/122113007829520366
- meta/facebook — Aprilia Racing remporte le Championnat des Équipes MotoGP grâce à la victoire de Bezzecchi lors du sprint au Portugal - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113018137520366
- meta/facebook — Avant-match : Spurs-Clippers, informations de diffusion - Média sportif — https://www.facebook.com/122106465861520366/posts/122112777249520366
- meta/facebook — Barcelone : Baldé pourrait quitter le club dès le mercato hivernal — https://www.facebook.com/122106465861520366/posts/122112843729520366
- meta/facebook — Bayern : Kane et Olise sortis blessés avant Lille en Ligue des champions — https://www.facebook.com/122106465861520366/posts/122112788019520366
- meta/facebook — Bayern : Max Eberl ne sait pas encore la gravité de la blessure d'Olise — https://www.facebook.com/122106465861520366/posts/122112807129520366
- meta/facebook — Ben White, de la critique au retour en force avec l'Angleterre — https://www.facebook.com/122106465861520366/posts/122112894285520366
- meta/facebook — Biathlon : Grand-Bornand, de nouvelles places en vente lundi 23 novembre à 9h - ski-nordique.net — https://www.facebook.com/122106465861520366/posts/122112980247520366
- meta/facebook — Billet d’humeur. Rugby : on attend quoi, exactement ? - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122112929907520366
- meta/facebook — Blackburn : Johnson salue l'impact de Mowbray, en retrait pour raisons de santé — https://www.facebook.com/122106465861520366/posts/122112737355520366
- meta/facebook — Bordeaux revendique près de 6.000 abonnés en Régional 1 avant Boulazac — https://www.facebook.com/122106465861520366/posts/122112964893520366
- meta/facebook — Botman suspendu six mois du permis après une utilisation de téléphone au volant — https://www.facebook.com/122106465861520366/posts/122114313693520366
- meta/facebook — Briatore vise une Alpine à deux ou trois dixièmes de McLaren en 2027 - f1news.fr — https://www.facebook.com/122106465861520366/posts/122112808431520366
- meta/facebook — Brighton : Luka Vušković, la recrue à 55 M€ qui s'impose en Premier League — https://www.facebook.com/122106465861520366/posts/122113038219520366
- meta/facebook — Bundesliga : Dortmund prend la tête, Leverkusen écrase Paderborn avec un doublé de Moreira — https://www.facebook.com/122106465861520366/posts/122113061271520366
- meta/facebook — CAF Awards 2026 : la CAF dévoile les finalistes masculins, le Cap-Vert en lice — https://www.facebook.com/122106465861520366/posts/122113912017520366
- meta/facebook — CAN 2025 : Mendy raconte comment il a déstabilisé Brahim Diaz avant sa panenka ratée — https://www.facebook.com/122106465861520366/posts/122112948507520366
- meta/facebook — CHOC ! La légende de la NFL Tom Brady pourrait devenir un nouveau propriétaire de Chelsea après son départ de Birmingham - Dailysports — https://www.facebook.com/122106465861520366/posts/122112790119520366
- meta/facebook — Carlos Alcaraz s'impose au tie-break contre Ben Shelton et rallie la finale des Finales ATP - L'Équipe — https://www.facebook.com/122106465861520366/posts/122113057323520366
- meta/facebook — Celtic : Mika Baur absent environ 10 semaines, selon O'Neill — https://www.facebook.com/122106465861520366/posts/122112878481520366
- meta/facebook — Championnat des Nations - À quelle heure et sur quelle chaîne voir le duel au sommet Angleterre - Nouvelle-Zélande - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122112942219520366
- meta/facebook — Championnat du monde de MotoGP™ | Calendrier | Résultats | Streaming en direct - MotoGP — https://www.facebook.com/122106465861520366/posts/122112787245520366
- meta/facebook — Charlton toujours sans point en WSL après dix journées — https://www.facebook.com/122106465861520366/posts/122112876783520366
- meta/facebook — Chelsea condamné à une amende de 150 000 livres pour chants discriminatoires — https://www.facebook.com/122106465861520366/posts/122112865197520366
- meta/facebook — Cherki sur le banc ? Chanot conseille Zidane avant l'Espagne — https://www.facebook.com/122106465861520366/posts/122112944643520366
- meta/facebook — Christian Bale cite Rossi, Márquez et Agostini, ces dieux du MotoGP qu’il rêve d’incarner - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112849813520366
- meta/facebook — Christian Bale nomme Valentino Rossi, Marc Marquez et Giacomo Agostini comme des dieux de MotoGP qu'il souhaite interpréter - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112738417520366
- meta/facebook — Commotion à l’échauffement : World Rugby change la règle - Quinze Ovalie — https://www.facebook.com/122106465861520366/posts/122112793731520366
- meta/facebook — Coupe du Portugal : Francisco Moura marque contre son camp avec Porto — https://www.facebook.com/122106465861520366/posts/122112928419520366
- meta/facebook — Coventry réclame l'équité après un penalty refusé face à Everton — https://www.facebook.com/122106465861520366/posts/122112809877520366
- meta/facebook — DNCG : trois clubs placés en sursis à statuer, d'autres soumis à un encadrement — https://www.facebook.com/122106465861520366/posts/122113767021520366
- meta/facebook — Daouda Weidmann, ancien du PSG, s'illustre à Twente et attire des clubs européens — https://www.facebook.com/122106465861520366/posts/122112962787520366
- meta/facebook — David Almansa mène la séance d'entraînement Moto3 au Portugal devant Máximo Quiles de 0,048 secondes - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112736569520366
- meta/facebook — Diogo Moreira, meilleur rookie MotoGP malgré sa chute au GP du Portugal - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113985913520366
- meta/facebook — Dortmund : Joane Gadou rêve de l'Équipe de France et de titres avec le BVB — https://www.facebook.com/122106465861520366/posts/122112875379520366
- meta/facebook — Décès de Roy Coyle, le manager le plus titré de l'histoire de l'Irish League — https://www.facebook.com/122106465861520366/posts/122112739665520366
- meta/facebook — Eredivisie : Mohamed Ihattaren retrouve son football au Fortuna Sittard — https://www.facebook.com/122106465861520366/posts/122112847191520366
- meta/facebook — Eric Perrot, « oui, je gagne très bien ma vie » - www.ski-nordique.net — https://www.facebook.com/122106465861520366/posts/122113060041520366
- meta/facebook — Exclu Midol. Transferts/Top 14 - L’international italien, Paolo Garbisi, prolonge l’aventure avec Perpignan - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122112996759520366
- meta/facebook — Foot: la légende de la NFL Tom Brady en pourparlers pour entrer au capital de Chelsea (médias) - TradingView — https://www.facebook.com/122106465861520366/posts/122112779499520366
- meta/facebook — France U17 : Alcocer regrette la défaite face à l'Arabie saoudite — https://www.facebook.com/122106465861520366/posts/122113286307520366
- meta/facebook — Franck Haise répond aux critiques de Nicolas de Tavernost sur les résultats du Stade Rennais — https://www.facebook.com/122106465861520366/posts/122112914289520366
- meta/facebook — Fulham : Benjamin Lecomte victime d'une rupture du tendon d'Achille — https://www.facebook.com/122106465861520366/posts/122112868359520366
- meta/facebook — GP de Las Vegas de F1 - La réaction d'Isack Hadjar après les qualifications : "Ça va être la guerre demain avec toutes les lignes droites" - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113006089520366
- meta/facebook — GP de Las Vegas de F1 - La réaction de Charles Leclerc après les qualifications : "Ça va être extrêmement compliqué" - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112998691520366
- meta/facebook — GP de Las Vegas de F1 - La réaction de Flavio Briatore à l'arrivée de la course : "De nombreuses raisons d'être optimistes - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113687479520366
- meta/facebook — GP de Las Vegas de F1 - La réaction de Frédéric Vasseur après les qualifications : "On s'attendait à souffrir, mais pas à ce point-là" - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113023075520366
- meta/facebook — GP de Las Vegas de F1 - La réaction de Pierre Gasly après les qualifications : "La bagarre se fera avec les Racing Bulls" - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112992637520366
- meta/facebook — GP de Las Vegas de F1 : la grille de départ, Isack Hadjar en retrait, énorme coup dur pour Lewis Hamilton - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112887841520366
- meta/facebook — GP de Las Vegas de F1 : le classement des Essais Libres 3, Isack Hadjar manque son coup, Lewis Hamilton discret - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112891525520366
- meta/facebook — GP du Portugal de MotoGP - La réaction de Johann Zarco à l'arrivée de la course Sprint : "Sans cette chute, nous aurions pu terminer 6e" - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113076523520366
- meta/facebook — GP du Portugal de MotoGP : Le crash de Diogo Moreira en vidéo en Q1 - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112973941520366
- meta/facebook — GP du Portugal de MotoGP : chaînes TV et horaires du week-end pour la France, le Sprint avancé de 30 minutes - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113011933520366
- meta/facebook — GP du Portugal de MotoGP : la grille de départ, pas de coup d'éclat pour Johann Zarco, Fabio Quartararo nulle part - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112978261520366
- meta/facebook — GP du Portugal de MotoGP : le classement des Essais Libres 1, encore du travail pour Johann Zarco, Fabio Quartararo démarre mal - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112743283520366
- meta/facebook — GP du Portugal de MotoGP : le classement des Essais Libres 2, Johann Zarco se rassure sur le mouillé, bilan plus mitigé pour Fabio Quartararo - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112990003520366
- meta/facebook — GP du Portugal de MotoGP : le classement des Essais, Johann Zarco brillamment qualifié en Q2, pas de bonne surprise pour Fabio Quartararo - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122112754197520366
- meta/facebook — GP du Portugal de MotoGP : le classement final de la course Sprint, Johann Zarco part à la faute, Fabio Quartararo dans les points - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113015065520366
- meta/facebook — GP du Portugal de MotoGP : le classement final de la course Sprint, Johann Zarco part à la faute, la solide remontée de Fabio Quartararo - Turbo.fr — https://www.facebook.com/122106465861520366/posts/122113066935520366
- meta/facebook — GP du Portugal – Sprint : Bezzecchi vainqueur, Márquez au tapis ! - AutoHebdo — https://www.facebook.com/122106465861520366/posts/122113028097520366
- meta/facebook — Ghislain Printant de retour sur le banc de Bastia jusqu'à la fin de saison — https://www.facebook.com/122106465861520366/posts/122112744447520366
- meta/facebook — Glentoran s'incline 3-2 face à Cliftonville, première défaite et premier carton rouge pour Ferguson — https://www.facebook.com/122106465861520366/posts/122112799143520366
- meta/facebook — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - F1 news — https://www.facebook.com/122106465861520366/posts/122113063137520366
- meta/facebook — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - f1news.fr — https://www.facebook.com/122106465861520366/posts/122113040175520366
- meta/facebook — HAC : Rauzier annonce un mercato hivernal agité après la défaite contre Troyes — https://www.facebook.com/122106465861520366/posts/122112960657520366
- meta/facebook — Huberdeau et la longue route vers la guérison - NHL.com — https://www.facebook.com/122106465861520366/posts/122112853539520366
- meta/facebook — Jamal Musiala : Rummenigge doute d'un retour à son meilleur niveau au Bayern — https://www.facebook.com/122106465861520366/posts/122113010667520366
- meta/facebook — Jesús Owono réapparaît en public après le drame ayant coûté la vie à Jesús de Miguel — https://www.facebook.com/122106465861520366/posts/122112773673520366
- meta/facebook — Joan Mir quitte Honda pour Ducati et met en garde contre le succès immédiat en MotoGP - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112769785520366
- meta/facebook — Johnstone Burgh évite un double match en une journée après un report — https://www.facebook.com/122106465861520366/posts/122112870615520366
- meta/facebook — Jordan Spence en voie d’atteindre ses objectifs - NHL.com — https://www.facebook.com/122106465861520366/posts/122112859401520366
- meta/facebook — Jules Koundé de retour dans le groupe du Barça face à Villarreal — https://www.facebook.com/122106465861520366/posts/122112995151520366
- meta/facebook — L'Américain Jimmy Connors, ancien numéro 1 mondial de tennis, souffre d'un cancer de l'oreille - franceinfo — https://www.facebook.com/122106465861520366/posts/122112986541520366
- meta/facebook — L'OL chambre Jérémy Janot, qui répond du tac au tac — https://www.facebook.com/122106465861520366/posts/122112854673520366
- meta/facebook — L'OL intéressé par Matvey Kislyak, jeune milieu du CSKA Moscou — https://www.facebook.com/122106465861520366/posts/122112771333520366
- meta/facebook — LOSC : Tanguy Nianzou sort en pleurs lors du match face à Lyon — https://www.facebook.com/122106465861520366/posts/122113081119520366
- meta/facebook — La LFP lance « Ligue 1 Africa » pour renforcer son développement sur le continent — https://www.facebook.com/122106465861520366/posts/122112759393520366
- meta/facebook — La NFL envisage d’instaurer des règles de déplacement pour les matchs internationaux - Flashscore.fr — https://www.facebook.com/122106465861520366/posts/122112856125520366
- meta/facebook — La nuit des Français en NBA : Moussa Diabaté égale son record, Nolan Traoré sort sur blessure - L'Équipe — https://www.facebook.com/122106465861520366/posts/122112982869520366
- meta/facebook — Lamine Camara : Liverpool prépare une offre de 70 M€ à Monaco — https://www.facebook.com/122106465861520366/posts/122113046115520366
- meta/facebook — Lamine Diack, payé sans jouer depuis trois ans au FC Nantes — https://www.facebook.com/122106465861520366/posts/122112872055520366
- meta/facebook — Lamouchi raconte son éviction express de la Tunisie après le Mondial 2026 — https://www.facebook.com/122106465861520366/posts/122114191875520366
- meta/facebook — Las Vegas — EL3 : George Russell signe le meilleur temps - f1news.fr — https://www.facebook.com/122106465861520366/posts/122112861567520366
- meta/facebook — Las Vegas — Qualifications : Max Verstappen signe le meilleur temps - F1 news — https://www.facebook.com/122106465861520366/posts/122112889503520366
- meta/facebook — Le Mans : Sébastien Sirot annonce son départ du club après sept saisons — https://www.facebook.com/122106465861520366/posts/122113020237520366
- meta/facebook — Le Rochelais Andjisseramatchi prêté à un club de Pro D2 - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122112829773520366
- meta/facebook — Le circuit ATP va considérablement augmenter ses récompenses pour tous les joueurs à partir de 2028 - franceinfo — https://www.facebook.com/122106465861520366/posts/122112740841520366
- meta/facebook — Les Hawks d'Atlanta s'imposent face aux Pistons de Detroit en NBA, match manqué pour Cade Cunningham - L'Équipe — https://www.facebook.com/122106465861520366/posts/122113406931520366
- meta/facebook — Lewis Hamilton révèle un double revers pour Ferrari au Grand Prix de Las Vegas - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113069905520366
- meta/facebook — Liga : Séville arrache le nul dans le derby face au Betis (1-1) — https://www.facebook.com/122106465861520366/posts/122113058619520366
- meta/facebook — Ligue 1 : Lassine Sinayoko élu joueur du mois d’octobre — https://www.facebook.com/122106465861520366/posts/122112762195520366
- meta/facebook — Ligue 2 (J13) : Nancy s'impose, Metz renverse Boulogne, Annecy bat Clermont — https://www.facebook.com/122106465861520366/posts/122112840915520366
- meta/facebook — Ligue 2 : Montpellier surpris 1-0 à Laval, Kanté décisif à la 21e minute — https://www.facebook.com/122106465861520366/posts/122113013709520366
- meta/facebook — Ligue 2 : Noah Fatar ouvre le score d'une frappe somptueuse à Metz — https://www.facebook.com/122106465861520366/posts/122112966135520366
- meta/facebook — Ligue 2 : Saint-Étienne s'impose à Reims et reste leader — https://www.facebook.com/122106465861520366/posts/122113071543520366
- meta/facebook — Ligue 3 : La Roche-sur-Yon prend le large, Versailles grimpe sur le podium — https://www.facebook.com/122106465861520366/posts/122113016577520366
- meta/facebook — Lille-Lyon : l'OL prend les devants avant la pause grâce à Bidstrup — https://www.facebook.com/122106465861520366/posts/122113066281520366
- meta/facebook — Liverpool : Hugo Ekitike devrait revenir en janvier, selon Foot Mercato — https://www.facebook.com/122106465861520366/posts/122113025739520366
- meta/facebook — L’Angleterre surclasse les All Blacks et met la pression sur le XV de France - Quinze Mondial — https://www.facebook.com/122106465861520366/posts/122113047603520366
- meta/facebook — Mac Allister (Liverpool) : le PSG et le Barça intéressés par un départ libre en 2028 — https://www.facebook.com/122106465861520366/posts/122112860409520366
- meta/facebook — Manchester City - Fulham : Anderson sauve un point d'une volée somptueuse — https://www.facebook.com/122106465861520366/posts/122113004067520366
- meta/facebook — Mara Guth - Maria Andrienko EN DIRECT 22/11/2026 | Tennis - Flashscore.fr — https://www.facebook.com/122106465861520366/posts/122113072989520366
- meta/facebook — Marc Marquez chute à un tour et demi du titre tandis que Bezzecchi remporte le sprint au Portugal et maintient le championnat en vie - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113032759520366
- meta/facebook — Medvedev domine Tiafoe et complète le dernier carré des cracks aux ATP Finals - Tennis Majors — https://www.facebook.com/122106465861520366/posts/122112812277520366
- meta/facebook — Mercato : l'Atlético Madrid relancerait son intérêt pour Mason Greenwood — https://www.facebook.com/122106465861520366/posts/122112958833520366
- meta/facebook — Monaco-Auxerre : Faivre ouvre le score pour l'AJA sur une frappe puissante — https://www.facebook.com/122106465861520366/posts/122113064415520366
- meta/facebook — MotoGP BREAKING NEWS : Maverick Vinales ne peut plus continuer au Portugal, terrible nouvelle - Paddock GP — https://www.facebook.com/122106465861520366/posts/122112760677520366
- meta/facebook — NBA : L'action inédite de Wembanyama, qui fait le tour du monde : Sports - Orange - Sports - Orange — https://www.facebook.com/122106465861520366/posts/122112758007520366
- meta/facebook — NBA : Résultats des matches de jeudi - mapsport.ma — https://www.facebook.com/122106465861520366/posts/122112866715520366
- meta/facebook — National 1 : Angoulême renverse Granville dans le temps additionnel — https://www.facebook.com/122106465861520366/posts/122112852015520366
- meta/facebook — National 1 : Montlouis arrache la victoire contre Borgo dans le temps additionnel — https://www.facebook.com/122106465861520366/posts/122112780897520366
- meta/facebook — National 2 : Cestas change d'entraîneur, Philippe Ollier remplace Vincent Bourhis — https://www.facebook.com/122106465861520366/posts/122112991263520366
- meta/facebook — Nice : Elye Wahi se dit épanoui et ouvert à un avenir au Gym — https://www.facebook.com/122106465861520366/posts/122112957729520366
- meta/facebook — Nice-PSG : Désiré Doué se blesse gravement au genou après avoir marqué — https://www.facebook.com/122106465861520366/posts/122113034199520366
- meta/facebook — Nice-PSG : Marquinhos et Dembélé de retour dans le groupe parisien — https://www.facebook.com/122106465861520366/posts/122112954357520366
- meta/facebook — Nicolas Bruna - Lorenzo Gagliardo EN DIRECT 27/11/2026 | Tennis - Flashscore.fr — https://www.facebook.com/122106465861520366/posts/122114281779520366
- meta/facebook — OGC Nice : Olivier Pantaloni a transformé les Aiglons, désormais 6es de Ligue 1 — https://www.facebook.com/122106465861520366/posts/122112752235520366
- meta/facebook — OM : De Zerbi évoque des tensions entre Longoria et Benatia pendant son passage — https://www.facebook.com/122106465861520366/posts/122112976425520366
- meta/facebook — Ohtani, joueur vedette de la MLB, revient sur sa saison décevante - NHKニュース — https://www.facebook.com/122106465861520366/posts/122114117247520366
- meta/facebook — PSG : Ibrahim Rabbaj, le jeune ailier suivi de près au Mondial U17 — https://www.facebook.com/122106465861520366/posts/122112879699520366
- meta/facebook — PSG : Rothen et Larqué émettent des réserves sur la vague de prolongations — https://www.facebook.com/122106465861520366/posts/122112814443520366
- meta/facebook — PSG : Willian Pacho explique les raisons de sa prolongation — https://www.facebook.com/122106465861520366/posts/122112742083520366
- meta/facebook — Pablo Pagis impressionné par Kylian Mbappé avant sa première sélection en Bleus — https://www.facebook.com/122106465861520366/posts/122112764715520366
- meta/facebook — Pablo Pagis, première sélection en Bleu : « Je n'ai encore rien fait » — https://www.facebook.com/122106465861520366/posts/122112873453520366
- meta/facebook — Packers contre Bears : le match de Noël de NFL Gameday sur Netflix - Sortir à Paris — https://www.facebook.com/122106465861520366/posts/122112791325520366
- meta/facebook — Pedro Acosta a des difficultés avec la sensation du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112772695520366
- meta/facebook — Pedro Acosta – « Il avait déjà assez sur la moto pour atteindre le prochain virage. » - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113065759520366
- meta/facebook — Penalty contre Chelsea : la décision de l'arbitre Michael Oliver expliquée — https://www.facebook.com/122106465861520366/posts/122113049685520366
- meta/facebook — Pochettino prend les commandes de Manchester United, Bruno Fernandes reste capitaine — https://www.facebook.com/122106465861520366/posts/122112911361520366
- meta/facebook — Premier League : Chelsea s'effondre face à Leeds, Tottenham s'impose — https://www.facebook.com/122106465861520366/posts/122113030557520366
- meta/facebook — Premier League : La légende du football américain Tom Brady devient actionnaire de Chelsea - DHnet — https://www.facebook.com/122106465861520366/posts/122112946821520366
- meta/facebook — Premier League : la légende de la NFL Tom Brady, en discussion pour entrer au capital de Chelsea - Le Figaro — https://www.facebook.com/122106465861520366/posts/122112788919520366
- meta/facebook — Pro D2. Dix défaites et un vestiaire à reconstruire : les coulisses du réveil de Nevers - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122112955857520366
- meta/facebook — Protoxyde d'azote dans le football : un usage jugé répandu chez les pros — https://www.facebook.com/122106465861520366/posts/122114079657520366
- meta/facebook — Pérez durcit le ton chez Cadillac : être en F1 ne suffit plus - F1 news — https://www.facebook.com/122106465861520366/posts/122112969897520366
- meta/facebook — Qatar : Pirelli limite chaque train de pneus à 27 tours - F1 news — https://www.facebook.com/122106465861520366/posts/122112935883520366
- meta/facebook — Rafael Nadal proposé au conseil d'administration du Real Madrid — https://www.facebook.com/122106465861520366/posts/122112940695520366
- meta/facebook — Raul Fernandez deuxième du Sprint MotoGP du Portugal à Portimão - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113054509520366
- meta/facebook — Raul Fernandez prend la deuxième place dans le Sprint MotoGP du Portugal à Portimão - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113051233520366
- meta/facebook — Real Madrid - Celta Vigo : les compositions annoncées par Foot Mercato — https://www.facebook.com/122106465861520366/posts/122113052577520366
- meta/facebook — Real Madrid : Mourinho ferme la porte à un départ d'Endrick en janvier — https://www.facebook.com/122106465861520366/posts/122112869331520366
- meta/facebook — Real Madrid-Celta Vigo : Mbappé et les Merengues reprennent la Liga ce samedi — https://www.facebook.com/122106465861520366/posts/122113042497520366
- meta/facebook — Red Star - Pau : match interrompu par une panne d'éclairage au stade Bauer — https://www.facebook.com/122106465861520366/posts/122112783945520366
- meta/facebook — Reims-ASSE : près de 1.000 supporters stéphanois empêchés d'entrer au stade — https://www.facebook.com/122106465861520366/posts/122113055673520366
- meta/facebook — Rennes : Nordin, Merlin et Blas pourraient quitter le club au mercato d'hiver — https://www.facebook.com/122106465861520366/posts/122112933687520366
- meta/facebook — Ronaldo inscrit son 986e but en carrière avec Al-Nassr — https://www.facebook.com/122106465861520366/posts/122112862911520366
- meta/facebook — Russell hausse le ton face à Verstappen après leur accrochage à Las Vegas - F1 news — https://www.facebook.com/122106465861520366/posts/122112926661520366
- meta/facebook — Ryan Kavuma-McQueen, 17 ans, impressionne en prêt à Portsmouth — https://www.facebook.com/122106465861520366/posts/122112931065520366
- meta/facebook — Santos : Neymar critique sévèrement l'arbitre après la défaite face à Grêmio — https://www.facebook.com/122106465861520366/posts/122113646103520366
- meta/facebook — Sarr tourne la page Liverpool et se concentre sur Crystal Palace — https://www.facebook.com/122106465861520366/posts/122112858147520366
- meta/facebook — Senna Agius prend la pole au Portugal en Moto2 alors que Guevara devance González - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122113035849520366
- meta/facebook — Senna Agius prend la tête lors des essais de Moto2 au Grand Prix du Portugal - Motorcycle Sports — https://www.facebook.com/122106465861520366/posts/122112842427520366
- meta/facebook — Senny Mayulu raconte sa première sélection en équipe de France et son échange avec Zidane — https://www.facebook.com/122106465861520366/posts/122112756153520366
- meta/facebook — Serie A : l'Inter Milan accroché 4-4 par l'Atalanta après avoir mené 3-1 à deux reprises — https://www.facebook.com/122106465861520366/posts/122113447539520366
- meta/facebook — Serie A : la Lazio s'impose 3-0 contre Lecce, Côme bat Cagliari 2-0 — https://www.facebook.com/122106465861520366/posts/122113077945520366
- meta/facebook — Serie A : le Napoli s'impose 1-0 face au Torino grâce à McTominay — https://www.facebook.com/122106465861520366/posts/122113074531520366
- meta/facebook — Stefan Bradl nommé coordinateur sportif de HRC pour 2027 - MotoGP — https://www.facebook.com/122106465861520366/posts/122112784851520366
- meta/facebook — Stoke City - Birmingham : un choc au sommet de la Championship — https://www.facebook.com/122106465861520366/posts/122112747891520366
- meta/facebook — Tennis : Les joueurs ATP se partageront plus de 350 millions de dollars à partir de 2028 - Flashscore.fr — https://www.facebook.com/122106465861520366/posts/122112863961520366
- meta/facebook — Tennis : Medvedev complète le tableau s’invite en demies du Masters ATP - Le Figaro — https://www.facebook.com/122106465861520366/posts/122112782433520366
- meta/facebook — Tom Brady pourrait entrer au capital de Chelsea — https://www.facebook.com/122106465861520366/posts/122112792279520366
- meta/facebook — Tom Brady, légende du football américain, souhaiterait devenir actionnaire de Chelsea, en Premier League - Ouest-France — https://www.facebook.com/122106465861520366/posts/122112745869520366
- meta/facebook — Troyes - Le Havre : duel de bas de classement ce vendredi à l'Aube — https://www.facebook.com/122106465861520366/posts/122112768099520366
- meta/facebook — UFC Qatar – Procházka vs Stirling : Tous les résultats - ActuMMA — https://www.facebook.com/122106465861520366/posts/122112984657520366
- meta/facebook — Un ancien entraineur du Top 14 estime que l’arbitre Piardi ne voulait pas faire perdre la France - Blog RCT — https://www.facebook.com/122106465861520366/posts/122112775839520366
- meta/facebook — Un combattant de MMA provoque la controverse en utilisant son... aine pour mettre son adversaire KO. - Vietnam.vn — https://www.facebook.com/122106465861520366/posts/122113868553520366
- meta/facebook — Un highside à plus de 200 km/h au MotoGP du Portugal : les images du vol plané vertigineux de Diogo Moreira - Actu.fr — https://www.facebook.com/122106465861520366/posts/122113001997520366
- meta/facebook — VM · Bilan du 21 novembre — https://www.facebook.com/122106465861520366/posts/122113255347520366
- meta/facebook — Verstappen à Antonelli : rester bien entouré pour continuer à gagner - F1 news — https://www.facebook.com/122106465861520366/posts/122112805401520366
- meta/facebook — XV de France : vers un forfait de Jean-Baptiste Gros, Rodrigue Neti titulaire ? - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122113044321520366
- meta/facebook — Yan Diomandé, de Leganés au Real Madrid en moins de deux ans selon RMC Sport — https://www.facebook.com/122106465861520366/posts/122112923895520366
- meta/facebook — Zverev - Alcaraz, ATP Finals, Masters (Turin), Finale, match en direct le 22-11-2026 - L'Équipe — https://www.facebook.com/122106465861520366/posts/122113207611520366
- meta/facebook — « C’est le yin et le yang » : Luis Enrique réagit aux licenciements en Ligue 1 — https://www.facebook.com/122106465861520366/posts/122112921837520366
- meta/facebook — « Je ne vais pas répondre à Contepomi » : Bernard Laporte réagit aux accusations de Felipe Contepomi - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122112763629520366
- meta/facebook — À quelle heure et sur quelle chaîne voir Philadephia Sixers - Milwaukee Bucks en NBA ? - L'Équipe — https://www.facebook.com/122106465861520366/posts/122112932481520366
- meta/facebook — À quelle heure et sur quelle chaîne voir San Antonio Spurs - New Orleans Pelicans en NBA ? - L'Équipe — https://www.facebook.com/122106465861520366/posts/122112952077520366
- meta/facebook — À quelle heure et sur quelle chaîne voir pays de Galles - Australie, le match de la sixième journée - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122112939159520366
- meta/instagram — "C'est un honneur que le Mali intègre World Rugby", apprécie l'international français et malien Camara - Rugbyrama — https://www.instagram.com/p/Df-VxlFGs91/
- meta/instagram — ASSE à Reims : des supporters stéphanois interdits de déplacement veulent malgré tout se rendre au stade — https://www.instagram.com/p/DgAXI5ajPk-/
- meta/instagram — Acosta peine avec le ressenti du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.instagram.com/p/Df-0rL3mB33/
- meta/instagram — Affaire Negreira : Florentino Pérez attaque le Barça et Javier Tebas — https://www.instagram.com/p/DgAPEzcl3vK/
- meta/instagram — Alex Marquez prend la tête des essais MotoGP au Portugal lors de son retour après une opération de l'épaule - Motorcycle Sports — https://www.instagram.com/p/Df-gFwhmGk7/
- meta/instagram — Alexandre Lafitte prend en charge Al-Hilal au Soudan, dans un contexte de guerre civile — https://www.instagram.com/p/Df_sv5RjuAp/
- meta/instagram — Angers SCO : Mael Gernigon, 17 ans, déjà titulaire face à l'OM en Ligue 1 — https://www.instagram.com/p/DgAjsGLjRWd/
- meta/instagram — Aprilia Racing remporte le Championnat des Équipes MotoGP grâce à la victoire de Bezzecchi lors du sprint au Portugal - Motorcycle Sports — https://www.instagram.com/p/DgAs2BPlybq/
- meta/instagram — Auxerre : Will Still salue la réaction de ses joueurs après le nul à Monaco — https://www.instagram.com/p/DgCpkiElfGy/
- meta/instagram — Avant-match : Spurs-Clippers, informations de diffusion - Média sportif — https://www.instagram.com/p/Df_FkctIDFj/
- meta/instagram — Barcelone : Baldé pourrait quitter le club dès le mercato hivernal — https://www.instagram.com/p/Df_Kas3DYKF/
- meta/instagram — Basket : le Paris Basketball écrase Dunkerque et conforte sa place de leader - Le Figaro — https://www.instagram.com/p/DgDggVbGDTz/
- meta/instagram — Bayern : Kane et Olise sortis blessés avant Lille en Ligue des champions — https://www.instagram.com/p/Df-u9JOlwZG/
- meta/instagram — Bayern : Max Eberl ne sait pas encore la gravité de la blessure d'Olise — https://www.instagram.com/p/Df-8r28DXcv/
- meta/instagram — Ben White, de la critique au retour en force avec l'Angleterre — https://www.instagram.com/p/Df_l4RJDX6_/
- meta/instagram — Billet d’humeur. Rugby : on attend quoi, exactement ? - Rugby Scope — https://www.instagram.com/p/Df_15aejens/
- meta/instagram — Blackburn : Johnson salue l'impact de Mowbray, en retrait pour raisons de santé — https://www.instagram.com/p/Df-JMHTkXIw/
- meta/instagram — Brest : Giovani Versini évoque son passé à l'OM avant le choc de janvier — https://www.instagram.com/p/DgLO44CCQmz/
- meta/instagram — Briatore vise une Alpine à deux ou trois dixièmes de McLaren en 2027 - f1news.fr — https://www.instagram.com/p/Df-7iyqjcd3/
- meta/instagram — Brighton : Luka Vušković, la recrue à 55 M€ qui s'impose en Premier League — https://www.instagram.com/p/DgA03PSDf4w/
- meta/instagram — CHOC ! La légende de la NFL Tom Brady pourrait devenir un nouveau propriétaire de Chelsea après son départ de Birmingham - Dailysports — https://www.instagram.com/p/Df_TknsCWxt/
- meta/instagram — Championnat des Nations - À quelle heure et sur quelle chaîne voir le duel au sommet Angleterre - Nouvelle-Zélande - Rugbyrama — https://www.instagram.com/p/DgAKhSbF8HX/
- meta/instagram — Championnat du monde de MotoGP™ | Calendrier | Résultats | Streaming en direct - MotoGP — https://www.instagram.com/p/Df_CbKKjn_p/
- meta/instagram — Chelsea condamné à une amende de 150 000 livres pour chants discriminatoires — https://www.instagram.com/p/Df_bmCGkhG5/
- meta/instagram — Cherki sur le banc ? Chanot conseille Zidane avant l'Espagne — https://www.instagram.com/p/Df_96GmlKMp/
- meta/instagram — Christian Bale nomme Valentino Rossi, Marc Marquez et Giacomo Agostini comme des dieux de MotoGP qu'il souhaite interpréter - Motorcycle Sports — https://www.instagram.com/p/Df-O6AnjVB2/
- meta/instagram — Colombie-Maroc au Mondial de personnes de petite taille : bagarre générale après le coup de sifflet final — https://www.instagram.com/p/DgHzMEjkr7C/
- meta/instagram — Coventry réclame l'équité après un penalty refusé face à Everton — https://www.instagram.com/p/Df_AH39FyPD/
- meta/instagram — Daouda Weidmann, ancien du PSG, s'illustre à Twente et attire des clubs européens — https://www.instagram.com/p/DgAINZcF4zG/
- meta/instagram — David Almansa mène la séance d'entraînement Moto3 au Portugal devant Máximo Quiles de 0,048 secondes - Motorcycle Sports — https://www.instagram.com/p/Df-LftWCU4t/
- meta/instagram — Eredivisie : Mohamed Ihattaren retrouve son football au Fortuna Sittard — https://www.instagram.com/p/Df_N2R4lKs8/
- meta/instagram — Eric Perrot, « oui, je gagne très bien ma vie » - www.ski-nordique.net — https://www.instagram.com/p/DgBE4EkF6-V/
- meta/instagram — Exclu Midol. Transferts/Top 14 - L’international italien, Paolo Garbisi, prolonge l’aventure avec Perpignan - Rugbyrama — https://www.instagram.com/p/DgAfGgWjbKQ/
- meta/instagram — Fulham : Benjamin Lecomte victime d'une rupture du tendon d'Achille — https://www.instagram.com/p/Df_d4v3l_LS/
- meta/instagram — GP de Las Vegas de F1 - La réaction de Charles Leclerc après les qualifications : "Ça va être extrêmement compliqué" - Turbo.fr — https://www.instagram.com/p/DgAiitEF7ts/
- meta/instagram — GP de Las Vegas de F1 - La réaction de Frédéric Vasseur après les qualifications : "On s'attendait à souffrir, mais pas à ce point-là" - Turbo.fr — https://www.instagram.com/p/DgAwRwNFPE2/
- meta/instagram — GP de Las Vegas de F1 - La réaction de Pierre Gasly après les qualifications : "La bagarre se fera avec les Racing Bulls" - Turbo.fr — https://www.instagram.com/p/DgAbrOHDQRf/
- meta/instagram — GP de Las Vegas de F1 : la grille de départ, Isack Hadjar en retrait, énorme coup dur pour Lewis Hamilton - Turbo.fr — https://www.instagram.com/p/Df_kvrujbke/
- meta/instagram — GP de Las Vegas de F1 : le classement des Essais Libres 3, Isack Hadjar manque son coup, Lewis Hamilton discret - Turbo.fr — https://www.instagram.com/p/Df_vC2tGxSs/
- meta/instagram — GP du Portugal de MotoGP - La réaction de Johann Zarco à l'arrivée de la course Sprint : "Sans cette chute, nous aurions pu terminer 6e" - Turbo.fr — https://www.instagram.com/p/DgBSm8sDY8L/
- meta/instagram — GP du Portugal de MotoGP : Le crash de Diogo Moreira en vidéo en Q1 - Turbo.fr — https://www.instagram.com/p/DgARXeQiUN6/
- meta/instagram — GP du Portugal de MotoGP : la grille de départ, pas de coup d'éclat pour Johann Zarco, Fabio Quartararo nulle part - Turbo.fr — https://www.instagram.com/p/DgAYO8HCbiX/
- meta/instagram — GP du Portugal de MotoGP : le classement des Essais, Johann Zarco brillamment qualifié en Q2, pas de bonne surprise pour Fabio Quartararo - Turbo.fr — https://www.instagram.com/p/Df-ZQSGk0yN/
- meta/instagram — GP du Portugal de MotoGP : le classement final de la course Sprint, Johann Zarco part à la faute, Fabio Quartararo dans les points - Turbo.fr — https://www.instagram.com/p/DgApZ0dHNuo/
- meta/instagram — GP du Portugal – Sprint : Bezzecchi vainqueur, Márquez au tapis ! - AutoHebdo — https://www.instagram.com/p/DgAzs2ijXwS/
- meta/instagram — Ghislain Printant de retour sur le banc de Bastia jusqu'à la fin de saison — https://www.instagram.com/p/Df-QGEBEp2B/
- meta/instagram — Glentoran s'incline 3-2 face à Cliftonville, première défaite et premier carton rouge pour Ferguson — https://www.instagram.com/p/Df-10PJEpdv/
- meta/instagram — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - F1 news — https://www.instagram.com/p/DgBIS9kJXlH/
- meta/instagram — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - f1news.fr — https://www.instagram.com/p/DgA3JL1F6Ck/
- meta/instagram — Huberdeau et la longue route vers la guérison - NHL.com — https://www.instagram.com/p/Df_JR0vCdNy/
- meta/instagram — Jamal Musiala : Rummenigge doute d'un retour à son meilleur niveau au Bayern — https://www.instagram.com/p/DgAnI5-Eouu/
- meta/instagram — Jesús Owono réapparaît en public après le drame ayant coûté la vie à Jesús de Miguel — https://www.instagram.com/p/Df-krIdFyZF/
- meta/instagram — Joan Mir quitte Honda pour Ducati et met en garde contre le succès immédiat en MotoGP - Motorcycle Sports — https://www.instagram.com/p/Df-i_iyF4Xl/
- meta/instagram — Johnstone Burgh évite un double match en une journée après un report — https://www.instagram.com/p/Df_hTCAiRhk/
- meta/instagram — Jordie Barrett capitaine des All Blacks contre l’Angleterre - Quinze Ovalie — https://www.instagram.com/p/DgNztl2jdxR/
- meta/instagram — Jules Koundé de retour dans le groupe du Barça face à Villarreal — https://www.instagram.com/p/DgAc2oukpWr/
- meta/instagram — L'OL chambre Jérémy Janot, qui répond du tac au tac — https://www.instagram.com/p/Df_UuQnkpKO/
- meta/instagram — LOSC : Tanguy Nianzou sort en pleurs lors du match face à Lyon — https://www.instagram.com/p/DgBTwgpkocj/
- meta/instagram — La Géorgie et les États-Unis intenables, le Portugal en souffrance... Découvrez tous les résultats du week-end - Rugbyrama — https://www.instagram.com/p/Df-xPbYCR6c/
- meta/instagram — La NFL envisage d’instaurer des règles de déplacement pour les matchs internationaux - Flashscore.fr — https://www.instagram.com/p/Df_MtFcF5Oq/
- meta/instagram — Lamine Camara : Liverpool prépare une offre de 70 M€ à Monaco — https://www.instagram.com/p/DgA4SP-oz4E/
- meta/instagram — Lamine Diack, payé sans jouer depuis trois ans au FC Nantes — https://www.instagram.com/p/Df_ibwZGmtG/
- meta/instagram — Las Vegas — EL3 : George Russell signe le meilleur temps - f1news.fr — https://www.instagram.com/p/Df_QJV7jRXw/
- meta/instagram — Las Vegas — Qualifications : Max Verstappen signe le meilleur temps - F1 news — https://www.instagram.com/p/Df_oK3RCf2X/
- meta/instagram — Le Mans : Sébastien Sirot annonce son départ du club après sept saisons — https://www.instagram.com/p/DgAqjwgF3Ff/
- meta/instagram — Les Hawks d'Atlanta s'imposent face aux Pistons de Detroit en NBA, match manqué pour Cade Cunningham - L'Équipe — https://www.instagram.com/p/DgFOX5iF29a/
- meta/instagram — Liga : Séville arrache le nul dans le derby face au Betis (1-1) — https://www.instagram.com/p/DgBClckH-yp/
- meta/instagram — Ligue 1 : Lassine Sinayoko élu joueur du mois d’octobre — https://www.instagram.com/p/Df-aXQUDz-L/
- meta/instagram — Ligue 2 (J13) : Nancy s'impose, Metz renverse Boulogne, Annecy bat Clermont — https://www.instagram.com/p/Df_G-WkjLpa/
- meta/instagram — Ligue 2 : Saint-Étienne s'impose à Reims et reste leader — https://www.instagram.com/p/DgBM4R2GoyE/
- meta/instagram — Liverpool : Hugo Ekitike devrait revenir en janvier, selon Foot Mercato — https://www.instagram.com/p/DgAt_ebjSW5/
- meta/instagram — L’Angleterre surclasse les All Blacks et met la pression sur le XV de France - Quinze Mondial — https://www.instagram.com/p/DgA-AlqF1UL/
- meta/instagram — Mac Allister (Liverpool) : le PSG et le Barça intéressés par un départ libre en 2028 — https://www.instagram.com/p/Df_YJ3-IM2x/
- meta/instagram — Manchester City - Fulham : Anderson sauve un point d'une volée somptueuse — https://www.instagram.com/p/DgAgQSKlyLQ/
- meta/instagram — Medvedev domine Tiafoe et complète le dernier carré des cracks aux ATP Finals - Tennis Majors — https://www.instagram.com/p/Df---FeIDEl/
- meta/instagram — Mercato : l'Atlético Madrid relancerait son intérêt pour Mason Greenwood — https://www.instagram.com/p/DgALoTNF4KT/
- meta/instagram — Monaco-Auxerre : Faivre ouvre le score pour l'AJA sur une frappe puissante — https://www.instagram.com/p/DgBGBEWjXfD/
- meta/instagram — NBA : L'action inédite de Wembanyama, qui fait le tour du monde : Sports - Orange - Sports - Orange — https://www.instagram.com/p/Df-cpDxoxlu/
- meta/instagram — National 1 : Angoulême renverse Granville dans le temps additionnel — https://www.instagram.com/p/Df_RSUjCbZ6/
- meta/instagram — National 1 : Montlouis arrache la victoire contre Borgo dans le temps additionnel — https://www.instagram.com/p/Df-oG9vFxwv/
- meta/instagram — National 2 : Cestas change d'entraîneur, Philippe Ollier remplace Vincent Bourhis — https://www.instagram.com/p/DgAZYCsFy54/
- meta/instagram — Nice : Elye Wahi se dit épanoui et ouvert à un avenir au Gym — https://www.instagram.com/p/DgAEzF3ErfK/
- meta/instagram — Nice-PSG : Désiré Doué se blesse gravement au genou après avoir marqué — https://www.instagram.com/p/DgAxbORl4rN/
- meta/instagram — Nice-PSG : Marquinhos et Dembélé de retour dans le groupe parisien — https://www.instagram.com/p/DgABXafl9P_/
- meta/instagram — OGC Nice : Olivier Pantaloni a transformé les Aiglons, désormais 6es de Ligue 1 — https://www.instagram.com/p/Df-TfiWmvU7/
- meta/instagram — OM : De Zerbi évoque des tensions entre Longoria et Benatia pendant son passage — https://www.instagram.com/p/DgASh1hoanI/
- meta/instagram — OM : Genesio écarte toujours Valero et Leccese du groupe professionnel — https://www.instagram.com/p/Df-yYbojPfi/
- meta/instagram — PSG : Rothen et Larqué émettent des réserves sur la vague de prolongations — https://www.instagram.com/p/Df_DjAfFx65/
- meta/instagram — PSG : Senny Mayulu impliqué sur sept buts en six matchs, selon Foot Mercato — https://www.instagram.com/p/DgM8w7PoFZZ/
- meta/instagram — PSG : Willian Pacho explique les raisons de sa prolongation — https://www.instagram.com/p/Df-MoXvmMOV/
- meta/instagram — Pablo Pagis impressionné par Kylian Mbappé avant sa première sélection en Bleus — https://www.instagram.com/p/Df-dzeel1dR/
- meta/instagram — Pedro Acosta a des difficultés avec la sensation du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.instagram.com/p/Df-m8c0mF9G/
- meta/instagram — Pedro Acosta – « Il avait déjà assez sur la moto pour atteindre le prochain virage. » - Motorcycle Sports — https://www.instagram.com/p/DgBO6QInw4d/
- meta/instagram — Penalty contre Chelsea : la décision de l'arbitre Michael Oliver expliquée — https://www.instagram.com/p/DgA7udIDM3J/
- meta/instagram — Pierre Gasly avant le GP du Qatar de F1 : "J'espère que nous pourrons conserver cette dynamique" - Turbo.fr — https://www.instagram.com/p/DgKX-MvoMg4/
- meta/instagram — Pochettino prend les commandes de Manchester United, Bruno Fernandes reste capitaine — https://www.instagram.com/p/Df_pUiZnBHZ/
- meta/instagram — Premier League : La légende du football américain Tom Brady devient actionnaire de Chelsea - DHnet — https://www.instagram.com/p/DgAANFDEm1Q/
- meta/instagram — Pro D2. Dix défaites et un vestiaire à reconstruire : les coulisses du réveil de Nevers - Rugby Scope — https://www.instagram.com/p/DgAHFjrgIat/
- meta/instagram — Pérez durcit le ton chez Cadillac : être en F1 ne suffit plus - F1 news — https://www.instagram.com/p/DgAN8EIIGFg/
- meta/instagram — Qatar : Pirelli limite chaque train de pneus à 27 tours - F1 news — https://www.instagram.com/p/Df_8xDml0kN/
- meta/instagram — Rafael Nadal proposé au conseil d'administration du Real Madrid — https://www.instagram.com/p/Df_6fK_jPxf/
- meta/instagram — Raul Fernandez prend la deuxième place dans le Sprint MotoGP du Portugal à Portimão - Motorcycle Sports — https://www.instagram.com/p/DgBBcWXDYSa/
- meta/instagram — Real Madrid : Mourinho ferme la porte à un départ d'Endrick en janvier — https://www.instagram.com/p/Df_e_jTF87j/
- meta/instagram — Red Star - Pau : match interrompu par une panne d'éclairage au stade Bauer — https://www.instagram.com/p/Df-rhZnmllf/
- meta/instagram — Reims-ASSE : près de 1.000 supporters stéphanois empêchés d'entrer au stade — https://www.instagram.com/p/DgA_KA7kbpc/
- meta/instagram — Rennes : Nordin, Merlin et Blas pourraient quitter le club au mercato d'hiver — https://www.instagram.com/p/Df_3DdUmtB_/
- meta/instagram — Ronaldo inscrit son 986e but en carrière avec Al-Nassr — https://www.instagram.com/p/Df_ab4Ej7t-/
- meta/instagram — Russell hausse le ton face à Verstappen après leur accrochage à Las Vegas - F1 news — https://www.instagram.com/p/Df_yeFimjRs/
- meta/instagram — Ryan Kavuma-McQueen, 17 ans, impressionne en prêt à Portsmouth — https://www.instagram.com/p/Df_znGLGj4f/
- meta/instagram — Sarr tourne la page Liverpool et se concentre sur Crystal Palace — https://www.instagram.com/p/Df_XAgHDimA/
- meta/instagram — Senny Mayulu raconte sa première sélection en équipe de France et son échange avec Zidane — https://www.instagram.com/p/Df-W7ICFSlN/
- meta/instagram — Serie A : le Napoli s'impose 1-0 face au Torino grâce à McTominay — https://www.instagram.com/p/DgBQTzECX8i/
- meta/instagram — Stefan Bradl nommé coordinateur sportif de HRC pour 2027 - MotoGP — https://www.instagram.com/p/Df-tz9XGoyU/
- meta/instagram — Tardozzi confirme que Marc Márquez restera chez Ducati après 2026 - Motorcycle Sports — https://www.instagram.com/p/Df-IDK6lDLC/
- meta/instagram — Tennis : Medvedev complète le tableau s’invite en demies du Masters ATP - Le Figaro — https://www.instagram.com/p/Df-qXlakcIH/
- meta/instagram — Tom Brady pourrait entrer au capital de Chelsea — https://www.instagram.com/p/Df-5P8FiV_x/
- meta/instagram — Tom Brady, légende du football américain, souhaiterait devenir actionnaire de Chelsea, en Premier League - Ouest-France — https://www.instagram.com/p/Df-SX7Gl7Ic/
- meta/instagram — Top 14 : Lyon a-t-il un vrai coup à jouer cette saison ? - Rugby Scope — https://www.instagram.com/p/DgPhikKDmW3/
- meta/instagram — Troyes - Le Havre : duel de bas de classement ce vendredi à l'Aube — https://www.instagram.com/p/Df-hOL4F6UA/
- meta/instagram — Un ancien entraineur du Top 14 estime que l’arbitre Piardi ne voulait pas faire perdre la France - Blog RCT — https://www.instagram.com/p/Df-4JiwEia7/
- meta/instagram — Un highside à plus de 200 km/h au MotoGP du Portugal : les images du vol plané vertigineux de Diogo Moreira - Actu.fr — https://www.instagram.com/p/DgAl-QVIWzT/
- meta/instagram — VM · Bilan du 21 novembre — https://www.instagram.com/p/DgDIb2aF1HI/
- meta/instagram — Will Jordan forfait pour Angleterre – All Blacks - Quinze Ovalie — https://www.instagram.com/p/DgIqGmRoOdE/
- meta/instagram — XV de France : vers un forfait de Jean-Baptiste Gros, Rodrigue Neti titulaire ? - Rugby Scope — https://www.instagram.com/p/DgA6k1ZF3Dn/
- meta/instagram — Yan Diomandé, de Leganés au Real Madrid en moins de deux ans selon RMC Sport — https://www.instagram.com/p/Df_wJ8wlx1Y/
- meta/instagram — À quelle heure et sur quelle chaîne voir Philadephia Sixers - Milwaukee Bucks en NBA ? - L'Équipe — https://www.instagram.com/p/Df_5V46CZFc/
- meta/instagram — À quelle heure et sur quelle chaîne voir San Antonio Spurs - New Orleans Pelicans en NBA ? - L'Équipe — https://www.instagram.com/p/DgADoyjl4eK/
- meta_pronos/facebook —  — https://www.facebook.com/1757379583055094/posts/1784276200365432
- meta_pronos/facebook — "C'est un honneur que le Mali intègre World Rugby", apprécie l'international français et malien Camara - Rugbyrama — https://www.facebook.com/1757379583055094/posts/1782046350588417
- meta_pronos/facebook — ASSE à Reims : des supporters stéphanois interdits de déplacement veulent malgré tout se rendre au stade — https://www.facebook.com/1757379583055094/posts/1782973883828997
- meta_pronos/facebook — Acosta peine avec le ressenti du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1782239023902483
- meta_pronos/facebook — Affaire Negreira : Florentino Pérez attaque le Barça et Javier Tebas — https://www.facebook.com/1757379583055094/posts/1782914030501649
- meta_pronos/facebook — Afrique du Sud : l'audience sur l'extradition de Kemi Seba reportée au 3 février 2027 — https://www.facebook.com/1757379583055094/posts/1782168517242867
- meta_pronos/facebook — Airbnb encadre les règles des propriétaires : ménage, vaisselle et poubelles — https://www.facebook.com/1757379583055094/posts/1782113960581656
- meta_pronos/facebook — Alex Marquez prend la tête des essais MotoGP au Portugal lors de son retour après une opération de l'épaule - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1782145670578485
- meta_pronos/facebook — Alexander Zverev rejoint sans surprise Carlos Alcaraz en finale du Masters de Turin - franceinfo — https://www.facebook.com/1757379583055094/posts/1783428427116876
- meta_pronos/facebook — Angers SCO : Mael Gernigon, 17 ans, déjà titulaire face à l'OM en Ligue 1 — https://www.facebook.com/1757379583055094/posts/1783077180485334
- meta_pronos/facebook — Anthropic : des centaines d'employés deviennent millionnaires après l'entrée en bourse — https://www.facebook.com/1757379583055094/posts/1782462913880094
- meta_pronos/facebook — Aprilia Racing remporte le Championnat des Équipes MotoGP grâce à la victoire de Bezzecchi lors du sprint au Portugal - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1783202150472837
- meta_pronos/facebook — Atlus promet des délais plus courts pour les prochains Persona — https://www.facebook.com/1757379583055094/posts/1782139003912485
- meta_pronos/facebook — Au Zimbabwe, une jeune génération d'artistes renouvelle la scène musicale — https://www.facebook.com/1757379583055094/posts/1782348697224849
- meta_pronos/facebook — Avant-match : Spurs-Clippers, informations de diffusion - Média sportif — https://www.facebook.com/1757379583055094/posts/1782289247230794
- meta_pronos/facebook — Bahreïn accuse l'Iran d'une frappe ayant causé un incendie sur un site industriel — https://www.facebook.com/1757379583055094/posts/1783415957118123
- meta_pronos/facebook — Barcelone : Baldé pourrait quitter le club dès le mercato hivernal — https://www.facebook.com/1757379583055094/posts/1782491023877283
- meta_pronos/facebook — Bayern : Kane et Olise sortis blessés avant Lille en Ligue des champions — https://www.facebook.com/1757379583055094/posts/1782232440569808
- meta_pronos/facebook — Bayern : Max Eberl ne sait pas encore la gravité de la blessure d'Olise — https://www.facebook.com/1757379583055094/posts/1782333360559716
- meta_pronos/facebook — Ben White, de la critique au retour en force avec l'Angleterre — https://www.facebook.com/1757379583055094/posts/1782600290533023
- meta_pronos/facebook — Berlin : des jeunes manifestent contre le réarmement et le retour possible du service militaire — https://www.facebook.com/1757379583055094/posts/1782259090567143
- meta_pronos/facebook — Billet d’humeur. Rugby : on attend quoi, exactement ? - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1782691300523922
- meta_pronos/facebook — Blackburn : Johnson salue l'impact de Mowbray, en retrait pour raisons de santé — https://www.facebook.com/1757379583055094/posts/1781936707266048
- meta_pronos/facebook — Briatore vise une Alpine à deux ou trois dixièmes de McLaren en 2027 - f1news.fr — https://www.facebook.com/1757379583055094/posts/1782324667227252
- meta_pronos/facebook — Brésil : une quinzaine d'Awás-Guajás sort de l'isolement en Amazonie, selon franceinfo — https://www.facebook.com/1757379583055094/posts/1783329560460096
- meta_pronos/facebook — Budget de l'UE : Antonio Costa propose 204 milliards d'euros d'économies, rejeté par la France — https://www.facebook.com/1757379583055094/posts/1782859657173753
- meta_pronos/facebook — Bundesliga : Dortmund prend la tête, Leverkusen écrase Paderborn avec un doublé de Moreira — https://www.facebook.com/1757379583055094/posts/1783173330475719
- meta_pronos/facebook — CAN 2025 : le TAS attribue le titre au Sénégal, le Maroc va contester — https://www.facebook.com/1757379583055094/posts/1786777323448653
- meta_pronos/facebook — COP31 : les négociations sur le climat se prolongent au-delà de la date prévue — https://www.facebook.com/1757379583055094/posts/1782274703898915
- meta_pronos/facebook — Calendrier de l'avent : une tradition religieuse devenue tendance commerciale — https://www.facebook.com/1757379583055094/posts/1782557993870586
- meta_pronos/facebook — Cameroun : il y a dix ans, la colère anglophone éclate dans les rues de Bamenda — https://www.facebook.com/1757379583055094/posts/1782506763875709
- meta_pronos/facebook — Carlos Alcaraz s'impose au tie-break contre Ben Shelton et rallie la finale des Finales ATP - L'Équipe — https://www.facebook.com/1757379583055094/posts/1783395153786870
- meta_pronos/facebook — Championnat du monde de MotoGP™ | Calendrier | Résultats | Streaming en direct - MotoGP — https://www.facebook.com/1757379583055094/posts/1782252497234469
- meta_pronos/facebook — Cherki sur le banc ? Chanot conseille Zidane avant l'Espagne — https://www.facebook.com/1757379583055094/posts/1782782837181435
- meta_pronos/facebook — Christian Bale nomme Valentino Rossi, Marc Marquez et Giacomo Agostini comme des dieux de MotoGP qu'il souhaite interpréter - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1781964797263239
- meta_pronos/facebook — Colombie-Maroc au Mondial de personnes de petite taille : bagarre générale après le coup de sifflet final — https://www.facebook.com/1757379583055094/posts/1786313996828319
- meta_pronos/facebook — Coventry réclame l'équité après un penalty refusé face à Everton — https://www.facebook.com/1757379583055094/posts/1782340930558959
- meta_pronos/facebook — Cybersécurité : l'intelligence artificielle, un outil de plus en plus utilisé par les cybercriminels — https://www.facebook.com/1757379583055094/posts/1782791260513926
- meta_pronos/facebook — Daouda Weidmann, ancien du PSG, s'illustre à Twente et attire des clubs européens — https://www.facebook.com/1757379583055094/posts/1782868943839491
- meta_pronos/facebook — David Almansa mène la séance d'entraînement Moto3 au Portugal devant Máximo Quiles de 0,048 secondes - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1781955503930835
- meta_pronos/facebook — Des animaux de compagnie autorisés en réanimation dans des hôpitaux parisiens — https://www.facebook.com/1757379583055094/posts/1782477153878670
- meta_pronos/facebook — Des missiles russes tombent en Pologne, les dirigeants européens dénoncent une provocation — https://www.facebook.com/1757379583055094/posts/1782448373881548
- meta_pronos/facebook — Députés et sénateurs trouvent un accord sur le projet de loi de fin de gestion 2026 — https://www.facebook.com/1757379583055094/posts/1782963887163330
- meta_pronos/facebook — Ebola en RDC : MSF demande un accès élargi au vaccin Ervebo dans l'est du pays — https://www.facebook.com/1757379583055094/posts/1782498660543186
- meta_pronos/facebook — En Espagne, Santiago Abascal (Vox) en position de faiseur de roi avant les législatives — https://www.facebook.com/1757379583055094/posts/1784440650348987
- meta_pronos/facebook — Eredivisie : Mohamed Ihattaren retrouve son football au Fortuna Sittard — https://www.facebook.com/1757379583055094/posts/1782514180541634
- meta_pronos/facebook — Eric Perrot, « oui, je gagne très bien ma vie » - www.ski-nordique.net — https://www.facebook.com/1757379583055094/posts/1783344410458611
- meta_pronos/facebook — Exclu Midol. Transferts/Top 14 - L’international italien, Paolo Garbisi, prolonge l’aventure avec Perpignan - Rugbyrama — https://www.facebook.com/1757379583055094/posts/1783033177156401
- meta_pronos/facebook — Exportations d'armes vers Israël : une association devant la cour administrative d'appel — https://www.facebook.com/1757379583055094/posts/1782572810535771
- meta_pronos/facebook — Fallout 1 : un fan développe un remaster HD complet, seul — https://www.facebook.com/1757379583055094/posts/1783229937136725
- meta_pronos/facebook — GP de Las Vegas de F1 - La réaction d'Isack Hadjar après les qualifications : "Ça va être la guerre demain avec toutes les lignes droites" - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783106980482354
- meta_pronos/facebook — GP de Las Vegas de F1 - La réaction de Charles Leclerc après les qualifications : "Ça va être extrêmement compliqué" - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783045473821838
- meta_pronos/facebook — GP de Las Vegas de F1 - La réaction de Pierre Gasly après les qualifications : "La bagarre se fera avec les Racing Bulls" - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783001137159605
- meta_pronos/facebook — GP de Las Vegas de F1 : la grille de départ, Isack Hadjar en retrait, énorme coup dur pour Lewis Hamilton - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1782579530535099
- meta_pronos/facebook — GP de Las Vegas de F1 : le classement des Essais Libres 3, Isack Hadjar manque son coup, Lewis Hamilton discret - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1782615167198202
- meta_pronos/facebook — GP du Portugal de MotoGP - La réaction de Johann Zarco à l'arrivée de la course Sprint : "Sans cette chute, nous aurions pu terminer 6e" - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783422363784149
- meta_pronos/facebook — GP du Portugal de MotoGP : Le crash de Diogo Moreira en vidéo en Q1 - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1782900483836337
- meta_pronos/facebook — GP du Portugal de MotoGP : le classement des Essais, Johann Zarco brillamment qualifié en Q2, pas de bonne surprise pour Fabio Quartararo - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1782056123920773
- meta_pronos/facebook — GP du Portugal de MotoGP : le classement final de la course Sprint, Johann Zarco part à la faute, Fabio Quartararo dans les points - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783156060477446
- meta_pronos/facebook — GP du Portugal de MotoGP : le classement final de la course Sprint, Johann Zarco part à la faute, la solide remontée de Fabio Quartararo - Turbo.fr — https://www.facebook.com/1757379583055094/posts/1783387753787610
- meta_pronos/facebook — GTA 6 : 32,5 millions de précommandes et 3,79 milliards de dollars de chiffre d'affaires en 24 heures — https://www.facebook.com/1757379583055094/posts/1782282697231449
- meta_pronos/facebook — GTA 6 : 32,5 millions de précommandes et 3,79 milliards de dollars le premier jour — https://www.facebook.com/1757379583055094/posts/1782355583890827
- meta_pronos/facebook — GTA 6 : Rockstar Games annonce 3,79 milliards de dollars de ventes en 24 heures — https://www.facebook.com/1757379583055094/posts/1782189063907479
- meta_pronos/facebook — GTA 6 : Vicki, la barmaid gothique, séduit déjà les joueurs — https://www.facebook.com/1757379583055094/posts/1782891427170576
- meta_pronos/facebook — GTA 6 : des joueurs découvrent un hommage à Dexter à Vice City — https://www.facebook.com/1757379583055094/posts/1782037557255963
- meta_pronos/facebook — GTA 6 : l'actrice Jesse James Rose révèle jouer le premier personnage non-binaire de la série — https://www.facebook.com/1757379583055094/posts/1782991983827187
- meta_pronos/facebook — GTA 6 : la version japonaise censure nudité et violence, selon Jeuxvideo.com — https://www.facebook.com/1757379583055094/posts/1782840280509024
- meta_pronos/facebook — GTA 6 : les Français plus impatients que les Américains, selon une étude — https://www.facebook.com/1757379583055094/posts/1782317737227945
- meta_pronos/facebook — GTA 6 : les joueurs multiplient déjà les cascades spectaculaires — https://www.facebook.com/1757379583055094/posts/1782392680553784
- meta_pronos/facebook — GTA 6 : où trouver la Mitsubishi Eclipse façon Fast and Furious — https://www.facebook.com/1757379583055094/posts/1782943223832063
- meta_pronos/facebook — GTA 6 : un OVNI et un mystère extraterrestre à découvrir à Kelly County — https://www.facebook.com/1757379583055094/posts/1783147673811618
- meta_pronos/facebook — GTA 6 et Zelda visés par une guerre de notes sur Metacritic — https://www.facebook.com/1757379583055094/posts/1783193793807006
- meta_pronos/facebook — GTA 6 sur PC : aucune annonce officielle à ce jour, selon JV France — https://www.facebook.com/1757379583055094/posts/1783316800461372
- meta_pronos/facebook — GTA VI réalise un lancement record avec plus de 3,79 milliards de dollars en 24 heures — https://www.facebook.com/1757379583055094/posts/1783097477149971
- meta_pronos/facebook — Glentoran s'incline 3-2 face à Cliftonville, première défaite et premier carton rouge pour Ferguson — https://www.facebook.com/1757379583055094/posts/1782266557233063
- meta_pronos/facebook — Gran Turismo 7 à 33,49 € sur PS5 pendant le Black Friday 2026 — https://www.facebook.com/1757379583055094/posts/1788009926658726
- meta_pronos/facebook — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - F1 news — https://www.facebook.com/1757379583055094/posts/1783350653791320
- meta_pronos/facebook — Grille définitive à Las Vegas : Verstappen en pole, les Ferrari 10e et 11e - f1news.fr — https://www.facebook.com/1757379583055094/posts/1783237563802629
- meta_pronos/facebook — Guatemala : le gang Barrio 18 désigné auteur matériel du meurtre d'un ancien procureur — https://www.facebook.com/1757379583055094/posts/1782522963874089
- meta_pronos/facebook — Guinée-Burkina Faso : Conakry coupe le signal de la RTB après une caricature de Mamadi Doumbouya — https://www.facebook.com/1757379583055094/posts/1782484040544648
- meta_pronos/facebook — Hassan Hajjaj expose « My Rock Stars » au Musée de la musique à Paris — https://www.facebook.com/1757379583055094/posts/1782982927161426
- meta_pronos/facebook — Huberdeau et la longue route vers la guérison - NHL.com — https://www.facebook.com/1757379583055094/posts/1782400260553026
- meta_pronos/facebook — Inde : la communauté des Bnei Menashe en route vers Israël — https://www.facebook.com/1757379583055094/posts/1782310810561971
- meta_pronos/facebook — Jamal Musiala : Rummenigge doute d'un retour à son meilleur niveau au Bayern — https://www.facebook.com/1757379583055094/posts/1783119963814389
- meta_pronos/facebook — Jesús Owono réapparaît en public après le drame ayant coûté la vie à Jesús de Miguel — https://www.facebook.com/1757379583055094/posts/1782153103911075
- meta_pronos/facebook — Joan Mir quitte Honda pour Ducati et met en garde contre le succès immédiat en MotoGP - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1782174683908917
- meta_pronos/facebook — Jordie Barrett capitaine des All Blacks contre l’Angleterre - Quinze Ovalie — https://www.facebook.com/1757379583055094/posts/1789238953202490
- meta_pronos/facebook — Jules Koundé de retour dans le groupe du Barça face à Villarreal — https://www.facebook.com/1757379583055094/posts/1783023150490737
- meta_pronos/facebook — L'UE et l'Indonésie signent un accord commercial visant à ouvrir leurs marchés — https://www.facebook.com/1757379583055094/posts/1783294967130222
- meta_pronos/facebook — La CIJ reconnaît un génocide commis contre les Rohingyas en Birmanie — https://www.facebook.com/1757379583055094/posts/1782668650526187
- meta_pronos/facebook — La NFL envisage d’instaurer des règles de déplacement pour les matchs internationaux - Flashscore.fr — https://www.facebook.com/1757379583055094/posts/1782469923879393
- meta_pronos/facebook — La princesse Kate partage son expérience du cancer dans le documentaire « Heal » — https://www.facebook.com/1757379583055094/posts/1783086710484381
- meta_pronos/facebook — Lamine Camara : Liverpool prépare une offre de 70 M€ à Monaco — https://www.facebook.com/1757379583055094/posts/1783262627133456
- meta_pronos/facebook — Lana Nusseibeh, candidate à l'ONU, promet une diplomatie infatigable — https://www.facebook.com/1757379583055094/posts/1782132500579802
- meta_pronos/facebook — Las Vegas — EL3 : George Russell signe le meilleur temps - f1news.fr — https://www.facebook.com/1757379583055094/posts/1782439527215766
- meta_pronos/facebook — Las Vegas — Qualifications : Max Verstappen signe le meilleur temps - F1 news — https://www.facebook.com/1757379583055094/posts/1782586233867762
- meta_pronos/facebook — Le Pape ouvre ses bras au monde du cyclisme - Vatican News — https://www.facebook.com/1757379583055094/posts/1782660697193649
- meta_pronos/facebook — Le Parlement adopte définitivement une présomption d'usage légal des armes par les forces de l'ordre — https://www.facebook.com/1757379583055094/posts/1782064280586624
- meta_pronos/facebook — Le Real Madrid dépasse le Bayern avec plus de 1,2 milliard d'euros de revenus — https://www.facebook.com/1757379583055094/posts/1783184523807933
- meta_pronos/facebook — Le circuit ATP va considérablement augmenter ses récompenses pour tous les joueurs à partir de 2028 - franceinfo — https://www.facebook.com/1757379583055094/posts/1781999737259745
- meta_pronos/facebook — Le nageur britannique Lewis Pugh a nagé dans le détroit d'Ormuz pour alerter sur la guerre — https://www.facebook.com/1757379583055094/posts/1783254100467642
- meta_pronos/facebook — Le testament de Gaudí, rendu public, révèle qu'il a légué ses biens à la Sagrada Familia — https://www.facebook.com/1757379583055094/posts/1787526366707082
- meta_pronos/facebook — Le « splunch », spa et déjeuner en journée, attire des clients dans les hôtels de luxe — https://www.facebook.com/1757379583055094/posts/1782593003867085
- meta_pronos/facebook — Les Etats-Unis publient une nouvelle série de documents sur les ovnis et les phénomènes anormaux — https://www.facebook.com/1757379583055094/posts/1783138307145888
- meta_pronos/facebook — Liga : Séville arrache le nul dans le derby face au Betis (1-1) — https://www.facebook.com/1757379583055094/posts/1783337330459319
- meta_pronos/facebook — Ligue 1 : Lassine Sinayoko élu joueur du mois d’octobre — https://www.facebook.com/1757379583055094/posts/1782564817203237
- meta_pronos/facebook — Ligue 2 (J13) : Nancy s'impose, Metz renverse Boulogne, Annecy bat Clermont — https://www.facebook.com/1757379583055094/posts/1782455650547487
- meta_pronos/facebook — Ligue 2 : Saint-Étienne s'impose à Reims et reste leader — https://www.facebook.com/1757379583055094/posts/1783434553782930
- meta_pronos/facebook — Ligue 3 : La Roche-sur-Yon prend le large, Versailles grimpe sur le podium — https://www.facebook.com/1757379583055094/posts/1783129243813461
- meta_pronos/facebook — Lille-Lyon : l'OL prend les devants avant la pause grâce à Bidstrup — https://www.facebook.com/1757379583055094/posts/1783363037123415
- meta_pronos/facebook — Liverpool : Hugo Ekitike devrait revenir en janvier, selon Foot Mercato — https://www.facebook.com/1757379583055094/posts/1783164240476628
- meta_pronos/facebook — Lyon : les commerçants de Bellecour inquiets du retour des manifestations en centre-ville — https://www.facebook.com/1757379583055094/posts/1782773550515697
- meta_pronos/facebook — L’Angleterre surclasse les All Blacks et met la pression sur le XV de France - Quinze Mondial — https://www.facebook.com/1757379583055094/posts/1783279577131761
- meta_pronos/facebook — Malaisie : hausse de la haine en ligne visant les Rohingyas et expulsions de Birmans — https://www.facebook.com/1757379583055094/posts/1785149140278138
- meta_pronos/facebook — Medvedev domine Tiafoe et complète le dernier carré des cracks aux ATP Finals - Tennis Majors — https://www.facebook.com/1757379583055094/posts/1782362423890143
- meta_pronos/facebook — Mercato : l'Atlético Madrid relancerait son intérêt pour Mason Greenwood — https://www.facebook.com/1757379583055094/posts/1782823557177363
- meta_pronos/facebook — Mexique : arrestation d'un chef de cartel suivie de violences à Guasave — https://www.facebook.com/1757379583055094/posts/1783066390486413
- meta_pronos/facebook — Minecraft Dungeons II : l'extension The Humblers Awaken plonge dans le Sift — https://www.facebook.com/1757379583055094/posts/1782206560572396
- meta_pronos/facebook — Monaco-Auxerre : Faivre ouvre le score pour l'AJA sur une frappe puissante — https://www.facebook.com/1757379583055094/posts/1783369863789399
- meta_pronos/facebook — MotoGP : Marc Marquez peut décrocher un 8e titre au Grand Prix du Portugal — https://www.facebook.com/1757379583055094/posts/1782550923871293
- meta_pronos/facebook — MotoGP BREAKING NEWS : Maverick Vinales ne peut plus continuer au Portugal, terrible nouvelle - Paddock GP — https://www.facebook.com/1757379583055094/posts/1782088323917553
- meta_pronos/facebook — Mémoire cash : Castle of Illusion, le premier grand jeu Disney de la Mega Drive — https://www.facebook.com/1757379583055094/posts/1782544753871910
- meta_pronos/facebook — NBA : L'action inédite de Wembanyama, qui fait le tour du monde : Sports - Orange - Sports - Orange — https://www.facebook.com/1757379583055094/posts/1782080853918300
- meta_pronos/facebook — National 1 : Angoulême renverse Granville dans le temps additionnel — https://www.facebook.com/1757379583055094/posts/1782530533873332
- meta_pronos/facebook — National 1 : Montlouis arrache la victoire contre Borgo dans le temps additionnel — https://www.facebook.com/1757379583055094/posts/1782377563888629
- meta_pronos/facebook — Nice-PSG : Désiré Doué se blesse gravement au genou après avoir marqué — https://www.facebook.com/1757379583055094/posts/1783221723804213
- meta_pronos/facebook — Nioh 3 : une Complete Edition repérée sur des classifications en Corée du Sud et au Japon — https://www.facebook.com/1757379583055094/posts/1783271110465941
- meta_pronos/facebook — OGC Nice : Olivier Pantaloni a transformé les Aiglons, désormais 6es de Ligue 1 — https://www.facebook.com/1757379583055094/posts/1782029040590148
- meta_pronos/facebook — OM : De Zerbi évoque des tensions entre Longoria et Benatia pendant son passage — https://www.facebook.com/1757379583055094/posts/1782924313833954
- meta_pronos/facebook — PSG : Rothen et Larqué émettent des réserves sur la vague de prolongations — https://www.facebook.com/1757379583055094/posts/1782415637218155
- meta_pronos/facebook — PSG : Willian Pacho explique les raisons de sa prolongation — https://www.facebook.com/1757379583055094/posts/1781981283928257
- meta_pronos/facebook — Pablo Pagis impressionné par Kylian Mbappé avant sa première sélection en Bleus — https://www.facebook.com/1757379583055094/posts/1782161183910267
- meta_pronos/facebook — Pas-de-Calais : la Canche atteint son maximum, vigilance orange aux crues — https://www.facebook.com/1757379583055094/posts/1782623533864032
- meta_pronos/facebook — Pedro Acosta a des difficultés avec la sensation du pneu avant mais fait confiance à son nouveau technicien à Portimão - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1782181363908249
- meta_pronos/facebook — Pedro Acosta – « Il avait déjà assez sur la moto pour atteindre le prochain virage. » - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1783356383790747
- meta_pronos/facebook — Premier League : La légende du football américain Tom Brady devient actionnaire de Chelsea - DHnet — https://www.facebook.com/1757379583055094/posts/1782807637178955
- meta_pronos/facebook — Présidentielle 2027 : des maires réticents à apporter leur parrainage — https://www.facebook.com/1757379583055094/posts/1782369827222736
- meta_pronos/facebook — Présidentielle 2027 : Éric Zemmour officialise sa candidature, Sarah Knafo en soutien clé — https://www.facebook.com/1757379583055094/posts/1782748097184909
- meta_pronos/facebook — Présidentielle : Bruno Retailleau envisage une primaire à droite selon RFI — https://www.facebook.com/1757379583055094/posts/1782683090524743
- meta_pronos/facebook — Présomption d'usage légal des armes : le syndicat Unsa Police réagit — https://www.facebook.com/1757379583055094/posts/1782630330530019
- meta_pronos/facebook — Pérez durcit le ton chez Cadillac : être en F1 ne suffit plus - F1 news — https://www.facebook.com/1757379583055094/posts/1782954430497609
- meta_pronos/facebook — Qatar : Pirelli limite chaque train de pneus à 27 tours - F1 news — https://www.facebook.com/1757379583055094/posts/1782756180517434
- meta_pronos/facebook — Quand Sochaux a changé le foot français — https://www.facebook.com/1757379583055094/posts/1784313670361685
- meta_pronos/facebook — Rafael Nadal proposé au conseil d'administration du Real Madrid — https://www.facebook.com/1757379583055094/posts/1782740493852336
- meta_pronos/facebook — Raul Fernandez deuxième du Sprint MotoGP du Portugal à Portimão - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1783323277127391
- meta_pronos/facebook — Raul Fernandez prend la deuxième place dans le Sprint MotoGP du Portugal à Portimão - Motorcycle Sports — https://www.facebook.com/1757379583055094/posts/1783286863797699
- meta_pronos/facebook — Red Dead Redemption 2 reçoit un mod ajoutant le ray tracing sur PC — https://www.facebook.com/1757379583055094/posts/1782799280513124
- meta_pronos/facebook — Red Star - Pau : match interrompu par une panne d'éclairage au stade Bauer — https://www.facebook.com/1757379583055094/posts/1782198153906570
- meta_pronos/facebook — Reims-ASSE : près de 1.000 supporters stéphanois empêchés d'entrer au stade — https://www.facebook.com/1757379583055094/posts/1783302440462808
- meta_pronos/facebook — Riyad dit avoir intercepté trois missiles houthis tirés vers la capitale — https://www.facebook.com/1757379583055094/posts/1782645070528545
- meta_pronos/facebook — Romancing SaGa 3 : Destinies United sortira le 4 février avec cinq compagnons présentés — https://www.facebook.com/1757379583055094/posts/1788757609917291
- meta_pronos/facebook — Russell hausse le ton face à Verstappen après leur accrochage à Las Vegas - F1 news — https://www.facebook.com/1757379583055094/posts/1782652870527765
- meta_pronos/facebook — Ryan Kavuma-McQueen, 17 ans, impressionne en prêt à Portsmouth — https://www.facebook.com/1757379583055094/posts/1782675373858848
- meta_pronos/facebook — Saint-Étienne : des chèques-cadeaux à moitié prix pour soutenir les commerces du centre-ville — https://www.facebook.com/1757379583055094/posts/1783012130491839
- meta_pronos/facebook — Sainte-Sophie : 420 mètres de galeries souterraines dégagés à Istanbul — https://www.facebook.com/1757379583055094/posts/1782878720505180
- meta_pronos/facebook — Senny Mayulu raconte sa première sélection en équipe de France et son échange avec Zidane — https://www.facebook.com/1757379583055094/posts/1782072517252467
- meta_pronos/facebook — Serie A : le Napoli s'impose 1-0 face au Torino grâce à McTominay — https://www.facebook.com/1757379583055094/posts/1783408097118909
- meta_pronos/facebook — Solange Alexandre, résistante française ayant mené des actions contre les troupes allemandes, est morte à 104 ans — https://www.facebook.com/1757379583055094/posts/1781990427260676
- meta_pronos/facebook — Soupçonné de fuites liées au RN, le préfet Hugues Moutouh demande à être relevé de ses fonctions — https://www.facebook.com/1757379583055094/posts/1783380007121718
- meta_pronos/facebook — Star Academy 2026 : deux élèves reprennent Las Ketchup devant Georges-Alain — https://www.facebook.com/1757379583055094/posts/1782384040554648
- meta_pronos/facebook — Stefan Bradl nommé coordinateur sportif de HRC pour 2027 - MotoGP — https://www.facebook.com/1757379583055094/posts/1782220370571015
- meta_pronos/facebook — TeddyBear évoque les médicaments qui aident à vivre dans son titre « Les Monstres » — https://www.facebook.com/1757379583055094/posts/1783212893805096
- meta_pronos/facebook — Tennis : Medvedev complète le tableau s’invite en demies du Masters ATP - Le Figaro — https://www.facebook.com/1757379583055094/posts/1782213687238350
- meta_pronos/facebook — The Chronicles of Riddick : l'annulation cachée aux développeurs — https://www.facebook.com/1757379583055094/posts/1782934730499579
- meta_pronos/facebook — Tir de mortier contre la députée Farida Amrani : son auteur condamné à 18 mois de prison — https://www.facebook.com/1757379583055094/posts/1782226103903775
- meta_pronos/facebook — Tom Brady pourrait entrer au capital de Chelsea — https://www.facebook.com/1757379583055094/posts/1782304067229312
- meta_pronos/facebook — Tom Brady, légende du football américain, souhaiterait devenir actionnaire de Chelsea, en Premier League - Ouest-France — https://www.facebook.com/1757379583055094/posts/1782010383925347
- meta_pronos/facebook — Top 14 : Lyon a-t-il un vrai coup à jouer cette saison ? - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1789977089795343
- meta_pronos/facebook — Treize arrestations à Shanghai pour une contrefaçon de figurine Tifa de Final Fantasy VII — https://www.facebook.com/1757379583055094/posts/1781946527265066
- meta_pronos/facebook — Troyes - Le Havre : duel de bas de classement ce vendredi à l'Aube — https://www.facebook.com/1757379583055094/posts/1782124120580640
- meta_pronos/facebook — Tunisie : Sihem Bensedrine condamnée à cinq ans de prison, selon RFI — https://www.facebook.com/1757379583055094/posts/1782424013883984
- meta_pronos/facebook — Ukraine : Macron dénonce un « agenda agressif » de la Russie après des incidents en Pologne et au Danemark — https://www.facebook.com/1757379583055094/posts/1782537970539255
- meta_pronos/facebook — Un ancien entraineur du Top 14 estime que l’arbitre Piardi ne voulait pas faire perdre la France - Blog RCT — https://www.facebook.com/1757379583055094/posts/1782245713901814
- meta_pronos/facebook — Un cargo russe attaqué par drone dans le golfe de Finlande — https://www.facebook.com/1757379583055094/posts/1783309480462104
- meta_pronos/facebook — Un chauffeur VTC reconnu coupable dans l'incendie de Pacific Palisades à Los Angeles — https://www.facebook.com/1757379583055094/posts/1782832130509839
- meta_pronos/facebook — Un condamné à mort exécuté au Texas après plus d'une heure de tentatives — https://www.facebook.com/1757379583055094/posts/1782407243885661
- meta_pronos/facebook — Un highside à plus de 200 km/h au MotoGP du Portugal : les images du vol plané vertigineux de Diogo Moreira - Actu.fr — https://www.facebook.com/1757379583055094/posts/1783056177154101
- meta_pronos/facebook — Un joueur affirme avoir trouvé un glitch donnant une vue à la première personne dans GTA 6 — https://www.facebook.com/1757379583055094/posts/1782431450549907
- meta_pronos/facebook — Un missile russe tombe en Pologne, selon Donald Tusk une provocation — https://www.facebook.com/1757379583055094/posts/1781973607262358
- meta_pronos/facebook — Un policier condamné à 18 mois de prison ferme pour un tir mortel à Sevran en 2022 — https://www.facebook.com/1757379583055094/posts/1782728997186819
- meta_pronos/facebook — Une comédienne accuse Depardieu, Houellebecq et Nicloux de viol en réunion — https://www.facebook.com/1757379583055094/posts/1782019860591066
- meta_pronos/facebook — VM · Bilan du 21 novembre — https://www.facebook.com/1757379583055094/posts/1784251100367942
- meta_pronos/facebook — XV de France : vers un forfait de Jean-Baptiste Gros, Rodrigue Neti titulaire ? - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1783245773801808
- meta_pronos/facebook — Yan Diomandé, de Leganés au Real Madrid en moins de deux ans selon RMC Sport — https://www.facebook.com/1757379583055094/posts/1782637690529283
- meta_pronos/facebook — Zverev - Alcaraz, ATP Finals, Masters (Turin), Finale, match en direct le 22-11-2026 - L'Équipe — https://www.facebook.com/1757379583055094/posts/1784002537059465
- meta_pronos/facebook — « Je ne vais pas répondre à Contepomi » : Bernard Laporte réagit aux accusations de Felipe Contepomi - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1782102353916150
- meta_pronos/facebook — « Robots tueurs » : les États de l'ONU s'accordent sur l'élaboration d'un instrument international — https://www.facebook.com/1757379583055094/posts/1782607557198963
- meta_pronos/facebook — À Saint-Étienne, des chèques-cadeaux pour relancer le commerce avant Noël — https://www.facebook.com/1757379583055094/posts/1783401330452919
- meta_pronos/facebook — À quelle heure et sur quelle chaîne voir Philadephia Sixers - Milwaukee Bucks en NBA ? - L'Équipe — https://www.facebook.com/1757379583055094/posts/1782698810523171
- meta_pronos/facebook — À quelle heure et sur quelle chaîne voir San Antonio Spurs - New Orleans Pelicans en NBA ? - L'Équipe — https://www.facebook.com/1757379583055094/posts/1782848590508193
- meta_pronos/facebook — À quelle heure et sur quelle chaîne voir pays de Galles - Australie, le match de la sixième journée - Rugbyrama — https://www.facebook.com/1757379583055094/posts/1782763917183327
- meta_pronos/facebook — Égypte : le média indépendant Mada Masr visé par une fermeture ordonnée par la justice — https://www.facebook.com/1757379583055094/posts/1782815987178120
- meta_pronos/facebook — États-Unis : les démocrates envisagent le budget comme levier sur la guerre en Iran — https://www.facebook.com/1757379583055094/posts/1782296633896722
- meta_univers/facebook —  — https://www.facebook.com/122098313661535169/posts/122112986463535169
- meta_univers/facebook — Celtic : Camilo Duran décisif face à Torreense, mais des doutes persistent — https://www.facebook.com/122098313661535169/posts/122114687643535169
- meta_univers/facebook — Un village du Maine-et-Loire reçoit un legs de 400 000 euros pour l'entretien de son église — https://www.facebook.com/122098313661535169/posts/122114750451535169
- meta_univers/facebook — VM Studio · Votre activité en ligne — https://www.facebook.com/122098313661535169/posts/122112997491535169
- meta_univers/facebook — VM · Bilan du 21 novembre — https://www.facebook.com/122098313661535169/posts/122112980025535169
- meta_univers/instagram — VM · Bilan du 21 novembre — https://www.instagram.com/p/DgDIei3CcY3/
