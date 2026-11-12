# Dossier Claude — Véloce Mercato, site et réseaux

État établi le 2026-11-12T06:36+01:00.

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
| Véloce Mercato · facebook | 28 |
| Véloce Mercato · instagram | 27 |
| VM Actus et Pronos · facebook | 28 |
| VM Univers · facebook | 28 |
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

- Pages HTML examinées : 149.
- URL interrogées : 396.
- HTTP 404/410 confirmés : 4.
- Cibles internes absentes du dépôt : 4.
- Liens protégés/non vérifiables automatiquement : 87.
- Ancres à relire : 58. Certaines existent seulement après chargement JavaScript.
- Classements à relire : 0.

Le détail exhaustif des contrôles effectués, avec fichiers et lignes, est dans docs/AUDIT_CLAUDE_2026-11-11.json et son résumé Markdown. Un refus 403/429 ne prouve pas un lien mort. Cet audit ne certifie pas tous les faits d’actualité, la disponibilité géographique des vidéos, les paiements ou les espaces authentifiés.

## Vidéos, référence musicale et reste à faire

Le dernier rendu répertorie 3 nouveaux flashes, bloc 2026-11-11T20:00:00+01:00. Lire studio/teasers.json pour les URLs réelles.

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

- meta/facebook — Blessé au genou, Kawhi Leonard sera encore absent au moins une semaine avec les Toronto Raptors - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110128243520366
- meta/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/122106465861520366/posts/122110029345520366
- meta/facebook — Christophe Gleizes : une rencontre de soutien au pied de la Tour Eiffel réunit des personnalités — https://www.facebook.com/122106465861520366/posts/122110334295520366
- meta/facebook — Cyclisme. Anthony Ravard : « Être sur le Tour de France en 2032, mais je ne dis pas si c’est le Tour hommes ou femmes - maville.com — https://www.facebook.com/122106465861520366/posts/122110045671520366
- meta/facebook — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.facebook.com/122106465861520366/posts/122110066125520366
- meta/facebook — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.facebook.com/122106465861520366/posts/122110297641520366
- meta/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/122106465861520366/posts/122110029429520366
- meta/facebook — FC Barcelone : un projet de niches funéraires au Camp Nou pour les supporters — https://www.facebook.com/122106465861520366/posts/122110325613520366
- meta/facebook — Fiorèse évoque son passage compliqué à l'OM, où il dit avoir reçu des cailloux — https://www.facebook.com/122106465861520366/posts/122110079889520366
- meta/facebook — Forfait de Mbappé : Zidane doit innover en attaque face à l'Italie — https://www.facebook.com/122106465861520366/posts/122110345869520366
- meta/facebook — Fritz - Norrie, ATP 250, Stockholm, Deuxième tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110316919520366
- meta/facebook — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.facebook.com/122106465861520366/posts/122110029855520366
- meta/facebook — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.facebook.com/122106465861520366/posts/122110029765520366
- meta/facebook — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.facebook.com/122106465861520366/posts/122110258725520366
- meta/facebook — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.facebook.com/122106465861520366/posts/122110029567520366
- meta/facebook — Les Blazers surclassent le Thunder, les Knicks déroulent, Giannis Antetokounmpo porte le Heat - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110116987520366
- meta/facebook — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.facebook.com/122106465861520366/posts/122110029627520366
- meta/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/122106465861520366/posts/122110028151520366
- meta/facebook — Naples intéressé par Tylel Tati, défenseur de Nantes — https://www.facebook.com/122106465861520366/posts/122110055565520366
- meta/facebook — National 2 : Nicolas Jeannesson réélu à la tête de C'Chartres Football — https://www.facebook.com/122106465861520366/posts/122110092207520366
- meta/facebook — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122110029591520366
- meta/facebook — OM : Adidas prépare déjà ses futurs maillots, des fuites font surface — https://www.facebook.com/122106465861520366/posts/122110274829520366
- meta/facebook — Pickford face à la concurrence de Trafford chez les Three Lions — https://www.facebook.com/122106465861520366/posts/122110106493520366
- meta/facebook — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110029663520366
- meta/facebook — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.facebook.com/122106465861520366/posts/122110309569520366
- meta/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/122106465861520366/posts/122110029381520366
- meta/facebook — Écosse : McTominay révèle un choc électrique au cœur avant la Coupe du monde 2026 — https://www.facebook.com/122106465861520366/posts/122110038891520366
- meta/facebook — Équipe de France : Ibrahima Konaté de retour, lancé avec le Real Madrid — https://www.facebook.com/122106465861520366/posts/122110290489520366
- meta/instagram — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.instagram.com/p/DflPWi-FMD_/
- meta/instagram — Christophe Gleizes détenu depuis 500 jours en Algérie : le cri de son frère Maxime — https://www.instagram.com/p/DfmLIeGDV0U/
- meta/instagram — Cyclisme. Anthony Ravard : « Être sur le Tour de France en 2032, mais je ne dis pas si c’est le Tour hommes ou femmes - maville.com — https://www.instagram.com/p/DflVeMsF-xD/
- meta/instagram — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.instagram.com/p/DfmEqXRmAX2/
- meta/instagram — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.instagram.com/p/DfnwFajFnOW/
- meta/instagram — F1 : la Formule 1 renonce à son plan B pour les dernières courses de 2026 - Sports Auto Moto — https://www.instagram.com/p/DfluiRsGmoH/
- meta/instagram — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.instagram.com/p/DflPcSelKK7/
- meta/instagram — FC Barcelone : un projet de niches funéraires au Camp Nou pour les supporters — https://www.instagram.com/p/Dfn5JAPFIov/
- meta/instagram — Forfait de Mbappé : Zidane doit innover en attaque face à l'Italie — https://www.instagram.com/p/DfoTJRjidJM/
- meta/instagram — Fritz - Norrie, ATP 250, Stockholm, Deuxième tour : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DfoL4EalGEj/
- meta/instagram — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.instagram.com/p/DflPqlLG3xP/
- meta/instagram — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.instagram.com/p/DflPtQClIYj/
- meta/instagram — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.instagram.com/p/DfnqaLZjgb0/
- meta/instagram — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.instagram.com/p/DflPkBElFlE/
- meta/instagram — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.instagram.com/p/DflPn0nm9HT/
- meta/instagram — MIN@MTL : Ce que vous devez savoir | Canadiens de Montréal - NHL.com — https://www.instagram.com/p/DflnpJwjQP9/
- meta/instagram — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.instagram.com/p/DflPZyYFPC5/
- meta/instagram — National 2 : Nicolas Jeannesson réélu à la tête de C'Chartres Football — https://www.instagram.com/p/Dfl1NpVDfS0/
- meta/instagram — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.instagram.com/p/DflPhYjFIeR/
- meta/instagram — OM : Adidas prépare déjà ses futurs maillots, des fuites font surface — https://www.instagram.com/p/DfnUE6nF5Uf/
- meta/instagram — Pickford face à la concurrence de Trafford chez les Three Lions — https://www.instagram.com/p/Dfl-V3NFylt/
- meta/instagram — Pirelli travaille la montée en température de ses intermédiaires pour 2027 - F1 news — https://www.instagram.com/p/Dfnep96mAHU/
- meta/instagram — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DflPlwHlByv/
- meta/instagram — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.instagram.com/p/DfoFCgJD4s4/
- meta/instagram — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.instagram.com/p/DflPe1mFIHF/
- meta/instagram — Écosse : McTominay révèle un choc électrique au cœur avant la Coupe du monde 2026 — https://www.instagram.com/p/DflanbCly78/
- meta/instagram — Équipe de France : Ibrahima Konaté de retour, lancé avec le Real Madrid — https://www.instagram.com/p/Dfn_Pc7Dcge/
- meta_pronos/facebook — ATP Finals 2026 : Arthur Fils fera sa première apparition au Masters de fin d'année — https://www.facebook.com/1757379583055094/posts/1769936028466116
- meta_pronos/facebook — Affaire Epstein : un rapport du Congrès américain dénonce des « défaillances institutionnelles » — https://www.facebook.com/1757379583055094/posts/1769605958499123
- meta_pronos/facebook — Anthropic prévoit une introduction en Bourse pouvant lever jusqu'à 64 milliards de dollars — https://www.facebook.com/1757379583055094/posts/1769873471805705
- meta_pronos/facebook — Asie centrale et Chine : hausse des plafonds de vols aériens entre les pays — https://www.facebook.com/1757379583055094/posts/1769977358461983
- meta_pronos/facebook — Au Pérou, le pape Léon XIV appelle à surmonter les divisions du passé — https://www.facebook.com/1757379583055094/posts/1771069508352768
- meta_pronos/facebook — Black Forest Games devient indépendant et lance Third Signal — https://www.facebook.com/1757379583055094/posts/1770937858365933
- meta_pronos/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/1757379583055094/posts/1769605048499214
- meta_pronos/facebook — Brésil : le TSE inflige une amende de 7,5 millions de réais à Meta pour traitement inégal — https://www.facebook.com/1757379583055094/posts/1769778108481908
- meta_pronos/facebook — Christophe Gleizes détenu depuis 500 jours en Algérie : le cri de son frère Maxime — https://www.facebook.com/1757379583055094/posts/1770024758457243
- meta_pronos/facebook — DNCG : encadrement de la masse salariale pour Nîmes et Rouen — https://www.facebook.com/1757379583055094/posts/1769823808477338
- meta_pronos/facebook — Devolver Digital annonce All Army Attack, un jeu qu'il présente comme son premier AAA — https://www.facebook.com/1757379583055094/posts/1769605555165830
- meta_pronos/facebook — Ducks : Un premier match pour Troy Terry cette saison - NHL.com — https://www.facebook.com/1757379583055094/posts/1770841135042272
- meta_pronos/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/1757379583055094/posts/1769605735165812
- meta_pronos/facebook — Indonésie : la jeunesse de nouveau dans la rue contre la politique du gouvernement — https://www.facebook.com/1757379583055094/posts/1769606181832434
- meta_pronos/facebook — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.facebook.com/1757379583055094/posts/1769722321820820
- meta_pronos/facebook — Le PS s'oppose à la candidature de David Lisnard à la tête de l'AMF — https://www.facebook.com/1757379583055094/posts/1769605135165872
- meta_pronos/facebook — Le Top Instagram MotoGP de la semaine : Márquez fête son podium, Martín et Bezzecchi hilares, Lorenzo de retour dans le paddock... (2 au 8 novembre) - Paddock GP — https://www.facebook.com/1757379583055094/posts/1770802778379441
- meta_pronos/facebook — Lecornu formalise la création de 5 000 places supplémentaires en licence — https://www.facebook.com/1757379583055094/posts/1770632745063111
- meta_pronos/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/1757379583055094/posts/1769605231832529
- meta_pronos/facebook — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.facebook.com/1757379583055094/posts/1769649931828059
- meta_pronos/facebook — Pirelli travaille la montée en température de ses intermédiaires pour 2027 - F1 news — https://www.facebook.com/1757379583055094/posts/1770732515053134
- meta_pronos/facebook — PlayStation abandonne le jeu-service Fairgames de Haven Studios — https://www.facebook.com/1757379583055094/posts/1769591448500574
- meta_pronos/facebook — Pologne : Varsovie accueille la Marche de l'indépendance dans un climat tendu — https://www.facebook.com/1757379583055094/posts/1769605378499181
- meta_pronos/facebook — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/1757379583055094/posts/1769683108491408
- meta_pronos/facebook — The Elder Scrolls 6 : Bethesda ne prévoit pas de nouvelles sur Sentinel avant un long moment — https://www.facebook.com/1757379583055094/posts/1770975431695509
- meta_pronos/facebook — Une nouvelle allure pour les gobelets du Centre Bell | Canadiens de Montréal - NHL.com — https://www.facebook.com/1757379583055094/posts/1771020791690973
- meta_pronos/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/1757379583055094/posts/1769606088499110
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
- meta_univers/facebook — À retrouver dans notre univers AlloLivre — https://www.facebook.com/122098313661535169/posts/122107928649535169
- meta_univers/facebook — À retrouver dans notre univers La Pastille TV — https://www.facebook.com/122098313661535169/posts/122108255139535169
- meta_univers/facebook — À retrouver dans notre univers VM Actus — https://www.facebook.com/122098313661535169/posts/122107971759535169
- meta_univers/facebook — À retrouver dans notre univers VM CV — https://www.facebook.com/122098313661535169/posts/122108304801535169
- meta_univers/facebook — À retrouver dans notre univers VM Emploi — https://www.facebook.com/122098313661535169/posts/122107896411535169
- meta_univers/facebook — À retrouver dans notre univers VM Gaming — https://www.facebook.com/122098313661535169/posts/122108335707535169
- meta_univers/facebook — À retrouver dans notre univers VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122108406075535169
- meta_univers/facebook — À retrouver dans notre univers VM Pro Local — https://www.facebook.com/122098313661535169/posts/122108441817535169
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
