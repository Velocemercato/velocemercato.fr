# Dossier Claude — Véloce Mercato, site et réseaux

État établi le 2026-11-14T08:04+01:00.

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
| Véloce Mercato · facebook | 72 |
| Véloce Mercato · instagram | 71 |
| VM Actus et Pronos · facebook | 72 |
| VM Univers · facebook | 68 |
| VM Univers · instagram | 14 |

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

- Pages HTML examinées : 1394.
- URL interrogées : 1633.
- HTTP 404/410 confirmés : 11.
- Cibles internes absentes du dépôt : 76.
- Liens protégés/non vérifiables automatiquement : 596.
- Ancres à relire : 3120. Certaines existent seulement après chargement JavaScript.
- Classements à relire : 0.

Le détail exhaustif des contrôles effectués, avec fichiers et lignes, est dans docs/AUDIT_CLAUDE_2026-11-11.json et son résumé Markdown. Un refus 403/429 ne prouve pas un lien mort. Cet audit ne certifie pas tous les faits d’actualité, la disponibilité géographique des vidéos, les paiements ou les espaces authentifiés.

## Vidéos, référence musicale et reste à faire

Le dernier rendu répertorie 3 nouveaux flashes, bloc 2026-11-14T09:00:00+01:00. Lire studio/teasers.json pour les URLs réelles.

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

- meta/facebook — ATP 250 Stockholm : dates, programme, prize money, diffusion TV… tout savoir sur l’édition 2026 - Univers Tennis — https://www.facebook.com/122106465861520366/posts/122110843281520366
- meta/facebook — Allemagne : Brajan Gruda inscrit un but lors de sa première sélection contre la Serbie — https://www.facebook.com/122106465861520366/posts/122110860351520366
- meta/facebook — Andreeva - Muchova, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110685697520366
- meta/facebook — Andreeva - Shnaider, WTA Finals, Masters (Indian Wells), Groupe 2 : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110810995520366
- meta/facebook — Angleterre – Japon. Henry Pollock titulaire, Borthwick change dix joueurs : les compositions - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122110468743520366
- meta/facebook — Appel d’Audi sur Monza : audience le 25 novembre pour le dossier Tsunoda - F1 news — https://www.facebook.com/122106465861520366/posts/122110575537520366
- meta/facebook — Blessé au genou, Kawhi Leonard sera encore absent au moins une semaine avec les Toronto Raptors - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110128243520366
- meta/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/122106465861520366/posts/122110029345520366
- meta/facebook — Christophe Gleizes : une rencontre de soutien au pied de la Tour Eiffel réunit des personnalités — https://www.facebook.com/122106465861520366/posts/122110334295520366
- meta/facebook — Cyclisme. Anthony Ravard : « Être sur le Tour de France en 2032, mais je ne dis pas si c’est le Tour hommes ou femmes - maville.com — https://www.facebook.com/122106465861520366/posts/122110045671520366
- meta/facebook — Côte d'Ivoire : Yan Diomandé filmé en train de distribuer de l'argent à de jeunes supporters — https://www.facebook.com/122106465861520366/posts/122110405695520366
- meta/facebook — DIRECT. Pegula - Noskova, WTA Finals, Masters (Indian Wells), Groupe 1 : 7-6, 4-6, 5-5 en direct - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110583751520366
- meta/facebook — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.facebook.com/122106465861520366/posts/122110066125520366
- meta/facebook — Donnarumma en difficulté avec Manchester City, une erreur contre la France — https://www.facebook.com/122106465861520366/posts/122110716303520366
- meta/facebook — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.facebook.com/122106465861520366/posts/122110297641520366
- meta/facebook — F1 : Williams change ses plans à Las Vegas et fait confiance à Victor Martins - Sports Auto Moto — https://www.facebook.com/122106465861520366/posts/122110876017520366
- meta/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/122106465861520366/posts/122110029429520366
- meta/facebook — FC Barcelone : un projet de niches funéraires au Camp Nou pour les supporters — https://www.facebook.com/122106465861520366/posts/122110325613520366
- meta/facebook — Fiorèse évoque son passage compliqué à l'OM, où il dit avoir reçu des cailloux — https://www.facebook.com/122106465861520366/posts/122110079889520366
- meta/facebook — Forfait de Mbappé : Zidane doit innover en attaque face à l'Italie — https://www.facebook.com/122106465861520366/posts/122110345869520366
- meta/facebook — Fornaroli termine ses essais McLaren à Jerez, avec un premier roulage en intermédiaires - F1 news — https://www.facebook.com/122106465861520366/posts/122110599387520366
- meta/facebook — Fritz - Musetti, ATP 250, Stockholm, Demi-finales, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110744551520366
- meta/facebook — Fritz - Norrie, ATP 250, Stockholm, Deuxième tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110316919520366
- meta/facebook — Glentoran : Duncan Ferguson décroche sa première victoire comme entraîneur — https://www.facebook.com/122106465861520366/posts/122110817949520366
- meta/facebook — Héroïques ! Les Bleus réalisent l’exploit face à l’Afrique du Sud ! - Top 14 — https://www.facebook.com/122106465861520366/posts/122110851207520366
- meta/facebook — Infantino visé par une plainte aux États-Unis pour emploi illégal d'une employée de maison — https://www.facebook.com/122106465861520366/posts/122110457073520366
- meta/facebook — Italie-France (3-1) : la presse italienne épingle Raymond Domenech après ses critiques — https://www.facebook.com/122106465861520366/posts/122110763853520366
- meta/facebook — Italie-France : Cherki frustré après la défaite des Bleus face à la Squadra — https://www.facebook.com/122106465861520366/posts/122110572741520366
- meta/facebook — L'Argentine s'incline face à l'Uruguay, premier match sans Messi — https://www.facebook.com/122106465861520366/posts/122110891401520366
- meta/facebook — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.facebook.com/122106465861520366/posts/122110029855520366
- meta/facebook — La numéro 2 mondiale Aryna Sabalenka prend la porte dès la phase de groupes du Masters WTA après sa défaite face à Elina Svitolina - franceinfo — https://www.facebook.com/122106465861520366/posts/122110834731520366
- meta/facebook — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.facebook.com/122106465861520366/posts/122110029765520366
- meta/facebook — Le Paris FC ouvert à un éventuel accueil au Parc des Princes — https://www.facebook.com/122106465861520366/posts/122110629381520366
- meta/facebook — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.facebook.com/122106465861520366/posts/122110258725520366
- meta/facebook — Le champion NBA Josh Hart nouvel investisseur au Napoli Basket, futur membre de l'Euroligue - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110754433520366
- meta/facebook — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.facebook.com/122106465861520366/posts/122110029567520366
- meta/facebook — Les Blazers surclassent le Thunder, les Knicks déroulent, Giannis Antetokounmpo porte le Heat - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110116987520366
- meta/facebook — Les États-Unis renoncent à la Coupe du monde U17 au Qatar — https://www.facebook.com/122106465861520366/posts/122110379505520366
- meta/facebook — Les États-Unis voudraient Pep Guardiola pour succéder à Mauricio Pochettino — https://www.facebook.com/122106465861520366/posts/122110369617520366
- meta/facebook — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.facebook.com/122106465861520366/posts/122110029627520366
- meta/facebook — Ligue des Nations : les Pays-Bas écrasent la Grèce 7-0, l'Allemagne s'impose en Serbie — https://www.facebook.com/122106465861520366/posts/122110806051520366
- meta/facebook — Melville pionnier, De Villiers le plus capé… Ces Sud-Africains ayant marqué l’histoire des Bleus - Top 14 — https://www.facebook.com/122106465861520366/posts/122110392165520366
- meta/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/122106465861520366/posts/122110028151520366
- meta/facebook — MotoGP BREAKING NEWS : Ducati a déjà la tête en 2027 ! Marquez et Acosta attendus pour un grand rendez-vous en rouge à Madonna di Campiglio - Paddock GP — https://www.facebook.com/122106465861520366/posts/122110480683520366
- meta/facebook — MotoGP BREAKING NEWS : Yamaha refuse de courir au Qatar, la FIM désavoue Dorna… et présente la facture - Paddock GP — https://www.facebook.com/122106465861520366/posts/122110775685520366
- meta/facebook — MotoGP, Vu sur Instagram - Furieux, Jorge Lorenzo dénonce des propos sur Valentino Rossi qui lui ont été faussement attribués - Paddock GP — https://www.facebook.com/122106465861520366/posts/122110791651520366
- meta/facebook — NFL Munich : le retour aux racines d’Amon-Ra St. Brown - DAZN — https://www.facebook.com/122106465861520366/posts/122110436877520366
- meta/facebook — NHL Global Series 2026 résultats : les deux buts de Sebastian Aho permettent à Carolina de l'emporter sur Seattle - DAZN — https://www.facebook.com/122106465861520366/posts/122110589313520366
- meta/facebook — Naples intéressé par Tylel Tati, défenseur de Nantes — https://www.facebook.com/122106465861520366/posts/122110055565520366
- meta/facebook — National 1 : Nîmes leader après sa victoire sur Istres, Rumilly s'impose à Saint-Priest — https://www.facebook.com/122106465861520366/posts/122110618533520366
- meta/facebook — National 2 : Nicolas Jeannesson réélu à la tête de C'Chartres Football — https://www.facebook.com/122106465861520366/posts/122110092207520366
- meta/facebook — Nations League : McConville et Atcheson, la charnière la plus solide du tournoi — https://www.facebook.com/122106465861520366/posts/122110640679520366
- meta/facebook — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122110029591520366
- meta/facebook — OM : Adidas prépare déjà ses futurs maillots, des fuites font surface — https://www.facebook.com/122106465861520366/posts/122110274829520366
- meta/facebook — PL : Roberto De Zerbi élu entraîneur du mois de octobre avec Tottenham — https://www.facebook.com/122106465861520366/posts/122110734423520366
- meta/facebook — Palmowski décroche un baquet financé en Formula Regional pour 2027 - F1 news — https://www.facebook.com/122106465861520366/posts/122110782873520366
- meta/facebook — Paris FC : Naples s'intéresserait à Patrick Zabi, selon la Gazzetta dello Sport — https://www.facebook.com/122106465861520366/posts/122110884141520366
- meta/facebook — Pickford face à la concurrence de Trafford chez les Three Lions — https://www.facebook.com/122106465861520366/posts/122110106493520366
- meta/facebook — Pourquoi tant de joueurs des Bleus ont-ils grandi au Stade Rennais ? — https://www.facebook.com/122106465861520366/posts/122110357455520366
- meta/facebook — Prestianni : Rui Costa se dit optimiste sur une prolongation à Benfica — https://www.facebook.com/122106465861520366/posts/122110826655520366
- meta/facebook — Qualifs CAN 2027 : l'Egypte écrase le Malawi 5-0, le Mali renverse le Rwanda 3-2 — https://www.facebook.com/122106465861520366/posts/122110869045520366
- meta/facebook — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110029663520366
- meta/facebook — Sabalenka - Svitolina, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110725393520366
- meta/facebook — Tabilo - Tirante, ATP 250, Stockholm, Demi-finales, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110674099520366
- meta/facebook — Transferts Grenoble : Plusieurs joueurs convoités en Top 14 - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122110661373520366
- meta/facebook — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.facebook.com/122106465861520366/posts/122110309569520366
- meta/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/122106465861520366/posts/122110029381520366
- meta/facebook — XV de France : comment William Servat a aidé Kalvin Gourgues à se libérer - Rugby Scope — https://www.facebook.com/122106465861520366/posts/122110417503520366
- meta/facebook — Écosse : McTominay révèle un choc électrique au cœur avant la Coupe du monde 2026 — https://www.facebook.com/122106465861520366/posts/122110038891520366
- meta/facebook — Équipe de France : Dayot Upamecano quitte le rassemblement pour raison personnelle — https://www.facebook.com/122106465861520366/posts/122110651749520366
- meta/facebook — Équipe de France : Ibrahima Konaté de retour, lancé avec le Real Madrid — https://www.facebook.com/122106465861520366/posts/122110290489520366
- meta/facebook — Équipe de France : Mbappé veut l'axe, Dembélé menacé selon Lizarazu — https://www.facebook.com/122106465861520366/posts/122110610721520366
- meta/instagram — ATP 250 Stockholm : dates, programme, prize money, diffusion TV… tout savoir sur l’édition 2026 - Univers Tennis — https://www.instagram.com/p/DftExy-FeCD/
- meta/instagram — Andreeva - Muchova, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.instagram.com/p/Dfr8hlQFySs/
- meta/instagram — Andreeva - Shnaider, WTA Finals, Masters (Indian Wells), Groupe 2 : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DfsvoEwGoYO/
- meta/instagram — Appel d’Audi sur Monza : audience le 25 novembre pour le dossier Tsunoda - F1 news — https://www.instagram.com/p/DfqWLf9lwYI/
- meta/instagram — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.instagram.com/p/DflPWi-FMD_/
- meta/instagram — Calendrier World Tour 2027 : toutes les dates des courses cyclistes - TotalVelo - Toute l'actualité cyclisme — https://www.instagram.com/p/DftV41loVXK/
- meta/instagram — Christophe Gleizes détenu depuis 500 jours en Algérie : le cri de son frère Maxime — https://www.instagram.com/p/DfmLIeGDV0U/
- meta/instagram — Cyclisme : 30 histoires de légendes, le livre de Cédric Leroy - Velo-Club — https://www.instagram.com/p/DfoaNCIFx9m/
- meta/instagram — Cyclisme. Anthony Ravard : « Être sur le Tour de France en 2032, mais je ne dis pas si c’est le Tour hommes ou femmes - maville.com — https://www.instagram.com/p/DflVeMsF-xD/
- meta/instagram — Côte d'Ivoire : Yan Diomandé filmé en train de distribuer de l'argent à de jeunes supporters — https://www.instagram.com/p/Dfo3VYrmAbK/
- meta/instagram — DIRECT. Pegula - Noskova, WTA Finals, Masters (Indian Wells), Groupe 1 : 7-6, 4-6, 5-5 en direct - L'Équipe — https://www.instagram.com/p/Dfqf4AQlwe9/
- meta/instagram — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.instagram.com/p/DfmEqXRmAX2/
- meta/instagram — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.instagram.com/p/DfnwFajFnOW/
- meta/instagram — EdF : Dugarry réclame des explications de Zidane sur son choix à droite — https://www.instagram.com/p/DfriInUm-Dd/
- meta/instagram — F1 : Williams change ses plans à Las Vegas et fait confiance à Victor Martins - Sports Auto Moto — https://www.instagram.com/p/Dftb27ll9cA/
- meta/instagram — F1 : la Formule 1 renonce à son plan B pour les dernières courses de 2026 - Sports Auto Moto — https://www.instagram.com/p/DfluiRsGmoH/
- meta/instagram — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.instagram.com/p/DflPcSelKK7/
- meta/instagram — FC Barcelone : un projet de niches funéraires au Camp Nou pour les supporters — https://www.instagram.com/p/Dfn5JAPFIov/
- meta/instagram — Forfait de Mbappé : Zidane doit innover en attaque face à l'Italie — https://www.instagram.com/p/DfoTJRjidJM/
- meta/instagram — Fritz - Musetti, ATP 250, Stockholm, Demi-finales, match en direct le 13-11-2026 - L'Équipe — https://www.instagram.com/p/DfsCnwQD5w4/
- meta/instagram — Fritz - Norrie, ATP 250, Stockholm, Deuxième tour : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DfoL4EalGEj/
- meta/instagram — Glentoran : Duncan Ferguson décroche sa première victoire comme entraîneur — https://www.instagram.com/p/Dfs34iZDEgV/
- meta/instagram — Héroïques ! Les Bleus réalisent l’exploit face à l’Afrique du Sud ! - Top 14 — https://www.instagram.com/p/DfszyyumGd4/
- meta/instagram — Italie-France (3-1) : la presse italienne épingle Raymond Domenech après ses critiques — https://www.instagram.com/p/DfsOtSyj7pv/
- meta/instagram — Italie-France : Cherki frustré après la défaite des Bleus face à la Squadra — https://www.instagram.com/p/Dfqk1VDDaPJ/
- meta/instagram — L'Argentine s'incline face à l'Uruguay, premier match sans Messi — https://www.instagram.com/p/DftnrJil_aM/
- meta/instagram — L'OM contacte l'agent de Santiago Hezze, milieu de l'Olympiakos valorisé 14 M€ — https://www.instagram.com/p/Dfrb3oilNdX/
- meta/instagram — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.instagram.com/p/DflPqlLG3xP/
- meta/instagram — La FIA retire l’accréditation de McEvoy, la Society of Editors conteste - F1 news — https://www.instagram.com/p/DftPgEnCfL-/
- meta/instagram — La numéro 2 mondiale Aryna Sabalenka prend la porte dès la phase de groupes du Masters WTA après sa défaite face à Elina Svitolina - franceinfo — https://www.instagram.com/p/Dfs-MVQl-YC/
- meta/instagram — Lassine Sinayoko, en vedette au Paris FC, attire déjà l'intérêt de clubs anglais — https://www.instagram.com/p/DfrVFHzl90k/
- meta/instagram — LdC : PSG-Rome classé à haut risque, parcage visiteur réduit — https://www.instagram.com/p/Dfr3KFBF7HA/
- meta/instagram — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.instagram.com/p/DflPtQClIYj/
- meta/instagram — Le PSG toujours intéressé par Upamecano, une clause libératoire à 65 M€ évoquée — https://www.instagram.com/p/DfpSsPOFL87/
- meta/instagram — Le Paris FC ouvert à un éventuel accueil au Parc des Princes — https://www.instagram.com/p/Dfq_Wlal4Hr/
- meta/instagram — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.instagram.com/p/DfnqaLZjgb0/
- meta/instagram — Le champion NBA Josh Hart nouvel investisseur au Napoli Basket, futur membre de l'Euroligue - L'Équipe — https://www.instagram.com/p/DfsJR5jDDu0/
- meta/instagram — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.instagram.com/p/DflPkBElFlE/
- meta/instagram — Lens : l'agent de Thiago Motta dément les accusations sur son salaire — https://www.instagram.com/p/Dfo9qbPl3uu/
- meta/instagram — Les Canadiens s'imposent devant les Bruins - NHL.com — https://www.instagram.com/p/DfrIeveDiCe/
- meta/instagram — Les États-Unis renoncent à la Coupe du monde U17 au Qatar — https://www.instagram.com/p/Dfop-sEjYyX/
- meta/instagram — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.instagram.com/p/DflPn0nm9HT/
- meta/instagram — Ligue des Nations : les Pays-Bas écrasent la Grèce 7-0, l'Allemagne s'impose en Serbie — https://www.instagram.com/p/Dfsq5h1GMnD/
- meta/instagram — MIN@MTL : Ce que vous devez savoir | Canadiens de Montréal - NHL.com — https://www.instagram.com/p/DflnpJwjQP9/
- meta/instagram — Materazzi revient sur le coup de tête de Zidane en lien avec la mort de Jesus de Miguel — https://www.instagram.com/p/DfpELmOlHhK/
- meta/instagram — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.instagram.com/p/DflPZyYFPC5/
- meta/instagram — MotoGP BREAKING NEWS : Yamaha refuse de courir au Qatar, la FIM désavoue Dorna… et présente la facture - Paddock GP — https://www.instagram.com/p/DfsUWZfDWRW/
- meta/instagram — NBA : au moins deux semaines d’absence pour Stephen Curry - Le Figaro — https://www.instagram.com/p/DfqYt-1l9QD/
- meta/instagram — National 1 : Nîmes leader après sa victoire sur Istres, Rumilly s'impose à Saint-Priest — https://www.instagram.com/p/Dfq4kRRF-oL/
- meta/instagram — National 2 : Nicolas Jeannesson réélu à la tête de C'Chartres Football — https://www.instagram.com/p/Dfl1NpVDfS0/
- meta/instagram — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.instagram.com/p/DflPhYjFIeR/
- meta/instagram — OM : Adidas prépare déjà ses futurs maillots, des fuites font surface — https://www.instagram.com/p/DfnUE6nF5Uf/
- meta/instagram — Palmer engagé avec l'Angleterre, assure Morgan Rogers — https://www.instagram.com/p/Dfqq3fAjbf0/
- meta/instagram — Paris FC : Naples s'intéresserait à Patrick Zabi, selon la Gazzetta dello Sport — https://www.instagram.com/p/DfthePBDc8J/
- meta/instagram — Pickford face à la concurrence de Trafford chez les Three Lions — https://www.instagram.com/p/Dfl-V3NFylt/
- meta/instagram — Pirelli travaille la montée en température de ses intermédiaires pour 2027 - F1 news — https://www.instagram.com/p/Dfnep96mAHU/
- meta/instagram — Prestianni : Rui Costa se dit optimiste sur une prolongation à Benfica — https://www.instagram.com/p/DftJ30NiTVV/
- meta/instagram — Ronaldinho titularisé avec Ravenna, son premier match officiel depuis 2015 — https://www.instagram.com/p/DfsZ1x0mHTb/
- meta/instagram — Rossi dénonce un calendrier MotoGP épuisant, Bagnaia blessé et l'avenir d'Aldeguer incertain - Motorcycle Sports — https://www.instagram.com/p/DfpM5aBGxnA/
- meta/instagram — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DflPlwHlByv/
- meta/instagram — Sabalenka - Svitolina, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.instagram.com/p/DfrxOJ5jtbL/
- meta/instagram — Sepang dément l’hypothèse d’une ouverture de saison F1 en 2027 - F1 news — https://www.instagram.com/p/DfojeRklOPd/
- meta/instagram — Serbie : crise institutionnelle et résultats en berne pour les Aigles Blancs — https://www.instagram.com/p/Dfsf6BTF6Wv/
- meta/instagram — Tuchel s'engage à rester sélectionneur de l'Angleterre jusqu'à l'Euro 2028 — https://www.instagram.com/p/DfowXpkFwTN/
- meta/instagram — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.instagram.com/p/DfoFCgJD4s4/
- meta/instagram — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.instagram.com/p/DflPe1mFIHF/
- meta/instagram — Yaya Fofana, révélation de Reims, appelé en équipe de Côte d'Ivoire — https://www.instagram.com/p/DfpZL93FO4f/
- meta/instagram — Écosse : McTominay révèle un choc électrique au cœur avant la Coupe du monde 2026 — https://www.instagram.com/p/DflanbCly78/
- meta/instagram — Équipe de France : Dayot Upamecano quitte le rassemblement pour raison personnelle — https://www.instagram.com/p/DfrOj0FF5H9/
- meta/instagram — Équipe de France : Ibrahima Konaté de retour, lancé avec le Real Madrid — https://www.instagram.com/p/Dfn_Pc7Dcge/
- meta/instagram — Équipe de France : Mbappé veut l'axe, Dembélé menacé selon Lizarazu — https://www.instagram.com/p/DfqxzT5F5vm/
- meta_pronos/facebook — ATP Finals 2026 : Arthur Fils fera sa première apparition au Masters de fin d'année — https://www.facebook.com/1757379583055094/posts/1769936028466116
- meta_pronos/facebook — Affaire Epstein : un rapport du Congrès américain dénonce des « défaillances institutionnelles » — https://www.facebook.com/1757379583055094/posts/1769605958499123
- meta_pronos/facebook — Allemagne : Brajan Gruda inscrit un but lors de sa première sélection contre la Serbie — https://www.facebook.com/1757379583055094/posts/1773541664772219
- meta_pronos/facebook — Andreeva - Muchova, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/1757379583055094/posts/1772844108175308
- meta_pronos/facebook — Andreeva - Shnaider, WTA Finals, Masters (Indian Wells), Groupe 2 : 2-0, match terminé - L'Équipe — https://www.facebook.com/1757379583055094/posts/1773295121463540
- meta_pronos/facebook — Anthropic prévoit une introduction en Bourse pouvant lever jusqu'à 64 milliards de dollars — https://www.facebook.com/1757379583055094/posts/1769873471805705
- meta_pronos/facebook — Appel d’Audi sur Monza : audience le 25 novembre pour le dossier Tsunoda - F1 news — https://www.facebook.com/1757379583055094/posts/1772117471581305
- meta_pronos/facebook — Ardèche : un commerçant de 55 ans tué à l'arme blanche à Largentière — https://www.facebook.com/1757379583055094/posts/1773209518138767
- meta_pronos/facebook — Asie centrale et Chine : hausse des plafonds de vols aériens entre les pays — https://www.facebook.com/1757379583055094/posts/1769977358461983
- meta_pronos/facebook — Au Pérou, le pape Léon XIV appelle à surmonter les divisions du passé — https://www.facebook.com/1757379583055094/posts/1771069508352768
- meta_pronos/facebook — BALL x PIT : le DLC Risen Ballbylon est disponible depuis le 12 novembre — https://www.facebook.com/1757379583055094/posts/1772187648240954
- meta_pronos/facebook — Black Forest Games devient indépendant et lance Third Signal — https://www.facebook.com/1757379583055094/posts/1770937858365933
- meta_pronos/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/1757379583055094/posts/1769605048499214
- meta_pronos/facebook — Brésil : le TSE inflige une amende de 7,5 millions de réais à Meta pour traitement inégal — https://www.facebook.com/1757379583055094/posts/1769778108481908
- meta_pronos/facebook — Christophe Gleizes détenu depuis 500 jours en Algérie : le cri de son frère Maxime — https://www.facebook.com/1757379583055094/posts/1770024758457243
- meta_pronos/facebook — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.facebook.com/1757379583055094/posts/1769823808477338
- meta_pronos/facebook — Des seniors bousculent les idées reçues sur la vieillesse, de la musique aux jeux vidéo — https://www.facebook.com/1757379583055094/posts/1773349718124747
- meta_pronos/facebook — Devolver Digital annonce All Army Attack, un jeu qu'il présente comme son premier AAA — https://www.facebook.com/1757379583055094/posts/1769605555165830
- meta_pronos/facebook — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.facebook.com/1757379583055094/posts/1770841135042272
- meta_pronos/facebook — EdF : Dugarry réclame des explications de Zidane sur son choix à droite — https://www.facebook.com/1757379583055094/posts/1772654964860889
- meta_pronos/facebook — Europe : vers un encadrement des loot boxes et des monnaies virtuelles dans les jeux — https://www.facebook.com/1757379583055094/posts/1772269141566138
- meta_pronos/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/1757379583055094/posts/1769605735165812
- meta_pronos/facebook — Fibre Excellence : la liquidation judiciaire de l'usine de Saint-Gaudens définitivement prononcée — https://www.facebook.com/1757379583055094/posts/1771281104998275
- meta_pronos/facebook — Fonction publique : les syndicats reçus à Matignon avant une grève le 17 novembre — https://www.facebook.com/1757379583055094/posts/1772609681532084
- meta_pronos/facebook — Fritz - Musetti, ATP 250, Stockholm, Demi-finales, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/1757379583055094/posts/1772893048170414
- meta_pronos/facebook — Glentoran : Duncan Ferguson décroche sa première victoire comme entraîneur — https://www.facebook.com/1757379583055094/posts/1773376074788778
- meta_pronos/facebook — Gérard Depardieu renonce à son procès en appel pour agressions sexuelles — https://www.facebook.com/1757379583055094/posts/1771608041632248
- meta_pronos/facebook — Indonésie : la jeunesse de nouveau dans la rue contre la politique du gouvernement — https://www.facebook.com/1757379583055094/posts/1769606181832434
- meta_pronos/facebook — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.facebook.com/1757379583055094/posts/1769722321820820
- meta_pronos/facebook — La FCPE appelle à entendre les revendications des lycéens — https://www.facebook.com/1757379583055094/posts/1773067778152941
- meta_pronos/facebook — Le PS s'oppose à la candidature de David Lisnard à la tête de l'AMF — https://www.facebook.com/1757379583055094/posts/1769605135165872
- meta_pronos/facebook — Le RN annonce une plainte en diffamation contre Marine Tondelier après l'attentat de Trappes — https://www.facebook.com/1757379583055094/posts/1772320938227625
- meta_pronos/facebook — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.facebook.com/1757379583055094/posts/1770802778379441
- meta_pronos/facebook — Le fisc utilise l'IA pour repérer les abris de jardin non déclarés — https://www.facebook.com/1757379583055094/posts/1771539741639078
- meta_pronos/facebook — Le pétrole africain redevient attractif pour la Chine avec la baisse du fret maritime — https://www.facebook.com/1757379583055094/posts/1772230451570007
- meta_pronos/facebook — Lecornu formalise la création de 5 000 places supplémentaires en licence — https://www.facebook.com/1757379583055094/posts/1770632745063111
- meta_pronos/facebook — Les Canadiens s'imposent devant les Bruins - NHL.com — https://www.facebook.com/1757379583055094/posts/1772468864879499
- meta_pronos/facebook — Ligue des Nations : les Pays-Bas écrasent la Grèce 7-0, l'Allemagne s'impose en Serbie — https://www.facebook.com/1757379583055094/posts/1773502048109514
- meta_pronos/facebook — Mali : des civils frappés par un drone au marché de Nampala, selon RFI — https://www.facebook.com/1757379583055094/posts/1773638631429189
- meta_pronos/facebook — Marvel 1943 : Rise of Hydra n'est pas annulé, selon Gamekult — https://www.facebook.com/1757379583055094/posts/1771444778315241
- meta_pronos/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/1757379583055094/posts/1769605231832529
- meta_pronos/facebook — Mobilisation contre la vie chère : des mesures antiterroristes visant des manifestants dénoncées — https://www.facebook.com/1757379583055094/posts/1772408638218855
- meta_pronos/facebook — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.facebook.com/1757379583055094/posts/1769649931828059
- meta_pronos/facebook — Palmowski décroche un baquet financé en Formula Regional pour 2027 - F1 news — https://www.facebook.com/1757379583055094/posts/1773160278143691
- meta_pronos/facebook — Panne de Microsoft 365 et d'Outlook touchant des dizaines de milliers d'utilisateurs — https://www.facebook.com/1757379583055094/posts/1772137764912609
- meta_pronos/facebook — Paris Photo 2026 : la foire du Grand Palais célèbre le bicentenaire de la photographie — https://www.facebook.com/1757379583055094/posts/1772361404890245
- meta_pronos/facebook — Pirelli travaille la montée en température de ses intermédiaires pour 2027 - F1 news — https://www.facebook.com/1757379583055094/posts/1770732515053134
- meta_pronos/facebook — PlayStation abandonne le jeu-service Fairgames de Haven Studios — https://www.facebook.com/1757379583055094/posts/1769591448500574
- meta_pronos/facebook — Pologne : Varsovie accueille la Marche de l'indépendance dans un climat tendu — https://www.facebook.com/1757379583055094/posts/1769605378499181
- meta_pronos/facebook — Pourquoi tant de joueurs des Bleus ont-ils grandi au Stade Rennais ? — https://www.facebook.com/1757379583055094/posts/1771118881681164
- meta_pronos/facebook — Prestianni : Rui Costa se dit optimiste sur une prolongation à Benfica — https://www.facebook.com/1757379583055094/posts/1773417618117957
- meta_pronos/facebook — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/1757379583055094/posts/1769683108491408
- meta_pronos/facebook — Sabalenka - Svitolina, WTA Finals, Masters (Indian Wells), Groupe 2, match en direct le 13-11-2026 - L'Équipe — https://www.facebook.com/1757379583055094/posts/1772785828181136
- meta_pronos/facebook — Seahawks-Raiders : l’avant-match de la Week 10 | DAZN News Belgique - DAZN — https://www.facebook.com/1757379583055094/posts/1772952991497753
- meta_pronos/facebook — Sepang dément l’hypothèse d’une ouverture de saison F1 en 2027 - F1 news — https://www.facebook.com/1757379583055094/posts/1771179308341788
- meta_pronos/facebook — Sonic Spinball : un spin-off développé en neuf mois pour Noël 1993 — https://www.facebook.com/1757379583055094/posts/1773733248086394
- meta_pronos/facebook — Soudan du Sud : Amnesty dénonce l'inaction des autorités et de l'ONU avant un massacre — https://www.facebook.com/1757379583055094/posts/1771338654992520
- meta_pronos/facebook — The Elder Scrolls 6 : Bethesda ne prévoit pas de nouvelles sur Sentinel avant un long moment — https://www.facebook.com/1757379583055094/posts/1770975431695509
- meta_pronos/facebook — Transferts Grenoble : Plusieurs joueurs convoités en Top 14 - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1772557571537295
- meta_pronos/facebook — Trappes : Fabien Roussel dénonce les violences visant les élus après l'attentat raciste — https://www.facebook.com/1757379583055094/posts/1771386628321056
- meta_pronos/facebook — Trump, Xi et Poutine doivent se rencontrer jeudi en Chine, selon la Maison Blanche — https://www.facebook.com/1757379583055094/posts/1773590001434052
- meta_pronos/facebook — Ukraine : des coupures d'électricité prolongées face aux frappes russes sur le réseau — https://www.facebook.com/1757379583055094/posts/1771227678336951
- meta_pronos/facebook — Ukraine : à Lozova, des déplacés traumatisés par l'évacuation du Donetsk — https://www.facebook.com/1757379583055094/posts/1773465318113187
- meta_pronos/facebook — Une exposition au MAD rend hommage au créateur de mode Yohan Serfaty — https://www.facebook.com/1757379583055094/posts/1773681684758217
- meta_pronos/facebook — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.facebook.com/1757379583055094/posts/1771020791690973
- meta_pronos/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/1757379583055094/posts/1769606088499110
- meta_pronos/facebook — XV de France : Julien Marchand forfait de dernière minute, Peato Mauvaka titulaire - Rugby Scope — https://www.facebook.com/1757379583055094/posts/1773325711460481
- meta_pronos/facebook — Yaya Fofana, révélation de Reims, appelé en équipe de Côte d'Ivoire — https://www.facebook.com/1757379583055094/posts/1771673538292365
- meta_pronos/facebook — Yordan Alvarez (Houston Astros) et Pete Crow-Armstrong (Chicago Cubs) élus MVP de la saison de MLB - L'Équipe — https://www.facebook.com/1757379583055094/posts/1772508004875585
- meta_pronos/facebook — À Bordeaux, un sapin de Noël naturel de retour place Pey-Berland — https://www.facebook.com/1757379583055094/posts/1773013148158404
- meta_pronos/facebook — Éliminatoires CAN 2027 : le Gabon et le Burkina Faso gagnent, la Tunisie battue par la Libye — https://www.facebook.com/1757379583055094/posts/1773110071482045
- meta_pronos/facebook — Équipe de France : Mbappé déclare forfait contre l’Italie en Ligue des nations — https://www.facebook.com/1757379583055094/posts/1770896008370118
- meta_univers/facebook — Découvre AlloLivre — https://www.facebook.com/122098313661535169/posts/122107745265535169
- meta_univers/facebook — Découvre La Pastille TV — https://www.facebook.com/122098313661535169/posts/122107745547535169
- meta_univers/facebook — Découvre Pépite FC — https://www.facebook.com/122098313661535169/posts/122107844757535169
- meta_univers/facebook — Découvre VM Actus — https://www.facebook.com/122098313661535169/posts/122107745373535169
- meta_univers/facebook — Découvre VM Belfort — https://www.facebook.com/122098313661535169/posts/122107825557535169
- meta_univers/facebook — Découvre VM CV — https://www.facebook.com/122098313661535169/posts/122107745733535169
- meta_univers/facebook — Découvre VM Emploi — https://www.facebook.com/122098313661535169/posts/122108326677535169
- meta_univers/facebook — Découvre VM Gaming — https://www.facebook.com/122098313661535169/posts/122107745451535169
- meta_univers/facebook — Découvre VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122107746051535169
- meta_univers/facebook — Découvre VM Pro Local — https://www.facebook.com/122098313661535169/posts/122107786449535169
- meta_univers/facebook — Découvre VM Produits locaux — https://www.facebook.com/122098313661535169/posts/122107806243535169
- meta_univers/facebook — Découvre VM Radio — https://www.facebook.com/122098313661535169/posts/122107872087535169
- meta_univers/facebook — Découvre VM Recettes — https://www.facebook.com/122098313661535169/posts/122107745979535169
- meta_univers/facebook — Découvre VM Shop — https://www.facebook.com/122098313661535169/posts/122107745889535169
- meta_univers/facebook — Découvre VM Sport & randonnée — https://www.facebook.com/122098313661535169/posts/122107746195535169
- meta_univers/facebook — Découvre VM Studio — https://www.facebook.com/122098313661535169/posts/122107745307535169
- meta_univers/facebook — Focus sur AlloLivre — https://www.facebook.com/122098313661535169/posts/122109442845535169
- meta_univers/facebook — Focus sur VM Actus — https://www.facebook.com/122098313661535169/posts/122109477039535169
- meta_univers/facebook — Focus sur VM Emploi — https://www.facebook.com/122098313661535169/posts/122109427719535169
- meta_univers/facebook — Focus sur VM Studio — https://www.facebook.com/122098313661535169/posts/122109464049535169
- meta_univers/facebook — Le saviez-vous ? Notre projet AlloLivre — https://www.facebook.com/122098313661535169/posts/122109099279535169
- meta_univers/facebook — Le saviez-vous ? Notre projet La Pastille TV — https://www.facebook.com/122098313661535169/posts/122109213795535169
- meta_univers/facebook — Le saviez-vous ? Notre projet Pépite FC — https://www.facebook.com/122098313661535169/posts/122109394557535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Actus — https://www.facebook.com/122098313661535169/posts/122109175695535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Belfort — https://www.facebook.com/122098313661535169/posts/122109383019535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM CV — https://www.facebook.com/122098313661535169/posts/122109230889535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Emploi — https://www.facebook.com/122098313661535169/posts/122109080175535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Gaming — https://www.facebook.com/122098313661535169/posts/122109196461535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122109300195535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Pro Local — https://www.facebook.com/122098313661535169/posts/122109339819535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Produits locaux — https://www.facebook.com/122098313661535169/posts/122109347493535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Radio — https://www.facebook.com/122098313661535169/posts/122109410565535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Recettes — https://www.facebook.com/122098313661535169/posts/122109283851535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Shop — https://www.facebook.com/122098313661535169/posts/122109246525535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Sport & randonnée — https://www.facebook.com/122098313661535169/posts/122109324861535169
- meta_univers/facebook — Le saviez-vous ? Notre projet VM Studio — https://www.facebook.com/122098313661535169/posts/122109159339535169
- meta_univers/facebook — Un projet VM à explorer AlloLivre — https://www.facebook.com/122098313661535169/posts/122108652837535169
- meta_univers/facebook — Un projet VM à explorer La Pastille TV — https://www.facebook.com/122098313661535169/posts/122108740479535169
- meta_univers/facebook — Un projet VM à explorer Pépite FC — https://www.facebook.com/122098313661535169/posts/122109041871535169
- meta_univers/facebook — Un projet VM à explorer VM Actus — https://www.facebook.com/122098313661535169/posts/122108701455535169
- meta_univers/facebook — Un projet VM à explorer VM Belfort — https://www.facebook.com/122098313661535169/posts/122109023421535169
- meta_univers/facebook — Un projet VM à explorer VM CV — https://www.facebook.com/122098313661535169/posts/122108901033535169
- meta_univers/facebook — Un projet VM à explorer VM Emploi — https://www.facebook.com/122098313661535169/posts/122108630727535169
- meta_univers/facebook — Un projet VM à explorer VM Gaming — https://www.facebook.com/122098313661535169/posts/122108721519535169
- meta_univers/facebook — Un projet VM à explorer VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122108942595535169
- meta_univers/facebook — Un projet VM à explorer VM Pro Local — https://www.facebook.com/122098313661535169/posts/122108987337535169
- meta_univers/facebook — Un projet VM à explorer VM Produits locaux — https://www.facebook.com/122098313661535169/posts/122109003117535169
- meta_univers/facebook — Un projet VM à explorer VM Radio — https://www.facebook.com/122098313661535169/posts/122109058977535169
- meta_univers/facebook — Un projet VM à explorer VM Recettes — https://www.facebook.com/122098313661535169/posts/122108930805535169
- meta_univers/facebook — Un projet VM à explorer VM Shop — https://www.facebook.com/122098313661535169/posts/122108921295535169
- meta_univers/facebook — Un projet VM à explorer VM Sport & randonnée — https://www.facebook.com/122098313661535169/posts/122108960985535169
- meta_univers/facebook — Un projet VM à explorer VM Studio — https://www.facebook.com/122098313661535169/posts/122108673519535169
- meta_univers/facebook — À retrouver dans notre univers AlloLivre — https://www.facebook.com/122098313661535169/posts/122107928649535169
- meta_univers/facebook — À retrouver dans notre univers La Pastille TV — https://www.facebook.com/122098313661535169/posts/122108255139535169
- meta_univers/facebook — À retrouver dans notre univers Pépite FC — https://www.facebook.com/122098313661535169/posts/122108582103535169
- meta_univers/facebook — À retrouver dans notre univers VM Actus — https://www.facebook.com/122098313661535169/posts/122107971759535169
- meta_univers/facebook — À retrouver dans notre univers VM Belfort — https://www.facebook.com/122098313661535169/posts/122108544111535169
- meta_univers/facebook — À retrouver dans notre univers VM CV — https://www.facebook.com/122098313661535169/posts/122108304801535169
- meta_univers/facebook — À retrouver dans notre univers VM Emploi — https://www.facebook.com/122098313661535169/posts/122107896411535169
- meta_univers/facebook — À retrouver dans notre univers VM Gaming — https://www.facebook.com/122098313661535169/posts/122108335707535169
- meta_univers/facebook — À retrouver dans notre univers VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122108406075535169
- meta_univers/facebook — À retrouver dans notre univers VM Pro Local — https://www.facebook.com/122098313661535169/posts/122108441817535169
- meta_univers/facebook — À retrouver dans notre univers VM Produits locaux — https://www.facebook.com/122098313661535169/posts/122108487543535169
- meta_univers/facebook — À retrouver dans notre univers VM Radio — https://www.facebook.com/122098313661535169/posts/122108603337535169
- meta_univers/facebook — À retrouver dans notre univers VM Recettes — https://www.facebook.com/122098313661535169/posts/122108388645535169
- meta_univers/facebook — À retrouver dans notre univers VM Shop — https://www.facebook.com/122098313661535169/posts/122108376777535169
- meta_univers/facebook — À retrouver dans notre univers VM Sport & randonnée — https://www.facebook.com/122098313661535169/posts/122108422851535169
- meta_univers/facebook — À retrouver dans notre univers VM Studio — https://www.facebook.com/122098313661535169/posts/122107951359535169
- meta_univers/instagram — Découvre AlloLivre — https://www.instagram.com/p/DflOoUbCd6Y/
- meta_univers/instagram — Découvre La Pastille TV — https://www.instagram.com/p/DflOyFpiWwe/
- meta_univers/instagram — Découvre Pépite FC — https://www.instagram.com/p/Dflnut6lD20/
- meta_univers/instagram — Découvre VM Actus — https://www.instagram.com/p/DflOtPXiVxY/
- meta_univers/instagram — Découvre VM Belfort — https://www.instagram.com/p/DflgxLxFxCu/
- meta_univers/instagram — Découvre VM CV — https://www.instagram.com/p/DflOzz5iSsu/
- meta_univers/instagram — Découvre VM Gaming — https://www.instagram.com/p/DflOvp_iQ4G/
- meta_univers/instagram — Découvre VM Météo & Découverte — https://www.instagram.com/p/DflO6tRkajm/
- meta_univers/instagram — Découvre VM Pro Local — https://www.instagram.com/p/DflVkKdl_Vo/
- meta_univers/instagram — Découvre VM Produits locaux — https://www.instagram.com/p/DflasS9lwRv/
- meta_univers/instagram — Découvre VM Recettes — https://www.instagram.com/p/DflO4AKiQWR/
- meta_univers/instagram — Découvre VM Shop — https://www.instagram.com/p/DflO1q7iVBZ/
- meta_univers/instagram — Découvre VM Sport & randonnée — https://www.instagram.com/p/DflO8s1iXqq/
- meta_univers/instagram — Découvre VM Studio — https://www.instagram.com/p/DflOq1Zif-X/
