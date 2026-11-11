# Dossier Claude — Véloce Mercato, site et réseaux

État établi le 2026-11-11T02:22+01:00.

Ce dossier remplace les anciennes consignes de restauration intégrale et les anciennes cadences. Il décrit le travail autorisé par Romain dans cette conversation. Les accès et conversations de ChatGPT ne sont pas automatiquement accessibles dans Claude.

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
| Véloce Mercato · facebook | 10 |
| Véloce Mercato · instagram | 10 |
| VM Actus et Pronos · facebook | 10 |
| VM Univers · facebook | 10 |
| VM Univers · instagram | 10 |

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

- Pages HTML examinées : 185.
- URL interrogées : 450.
- HTTP 404/410 confirmés : 0.
- Cibles internes absentes du dépôt : 0.
- Liens protégés/non vérifiables automatiquement : 93.
- Ancres à relire : 234. Certaines existent seulement après chargement JavaScript.
- Classements à relire : 1.

Le détail exhaustif des contrôles effectués, avec fichiers et lignes, est dans docs/AUDIT_CLAUDE_2026-11-11.json et son résumé Markdown. Un refus 403/429 ne prouve pas un lien mort. Cet audit ne certifie pas tous les faits d’actualité, la disponibilité géographique des vidéos, les paiements ou les espaces authentifiés.

## Vidéos, référence musicale et reste à faire

Le dernier rendu répertorie 3 nouveaux flashes, bloc 2026-11-11T09:00:00+01:00. Lire studio/teasers.json pour les URLs réelles.

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

- meta/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/122106465861520366/posts/122110029345520366
- meta/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/122106465861520366/posts/122110029429520366
- meta/facebook — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.facebook.com/122106465861520366/posts/122110029855520366
- meta/facebook — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.facebook.com/122106465861520366/posts/122110029765520366
- meta/facebook — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.facebook.com/122106465861520366/posts/122110029567520366
- meta/facebook — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.facebook.com/122106465861520366/posts/122110029627520366
- meta/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/122106465861520366/posts/122110028151520366
- meta/facebook — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.facebook.com/122106465861520366/posts/122110029591520366
- meta/facebook — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.facebook.com/122106465861520366/posts/122110029663520366
- meta/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/122106465861520366/posts/122110029381520366
- meta/instagram — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.instagram.com/p/DflPWi-FMD_/
- meta/instagram — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.instagram.com/p/DflPcSelKK7/
- meta/instagram — La F1 maintient Qatar et Abu Dhabi, Imola écarté comme solution de repli - F1 news — https://www.instagram.com/p/DflPqlLG3xP/
- meta/instagram — Le Bayern refuse de céder Jonathan Tah au Barça lors du mercato — https://www.instagram.com/p/DflPtQClIYj/
- meta/instagram — Leicester et Brentford U21 qualifiés pour les huitièmes du Jersey Mike's Trophy — https://www.instagram.com/p/DflPkBElFlE/
- meta/instagram — Ligue des Champions (F) : le PSG s’incline 2-1 face au Bayern au Parc — https://www.instagram.com/p/DflPn0nm9HT/
- meta/instagram — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.instagram.com/p/DflPZyYFPC5/
- meta/instagram — Nouvelle-Zélande à la Coupe du monde de rugby 2023 : actualités, matches en direct, joueurs, compositions, calendriers et résultats des All Blacks. - Rugbyrama — https://www.instagram.com/p/DflPhYjFIeR/
- meta/instagram — Rune - Bergs, ATP 250, Stockholm, Premier tour : 2-0, match terminé - L'Équipe — https://www.instagram.com/p/DflPlwHlByv/
- meta/instagram — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.instagram.com/p/DflPe1mFIHF/
- meta_pronos/facebook — Affaire Epstein : un rapport du Congrès américain dénonce des « défaillances institutionnelles » — https://www.facebook.com/1757379583055094/posts/1769605958499123
- meta_pronos/facebook — Bob Boone, champion des World Series et membre de la première famille de l’histoire de la MLB à compter 3 générations de joueurs, est mort à 78 - Mezha.net — https://www.facebook.com/1757379583055094/posts/1769605048499214
- meta_pronos/facebook — Devolver Digital annonce All Army Attack, un jeu qu'il présente comme son premier AAA — https://www.facebook.com/1757379583055094/posts/1769605555165830
- meta_pronos/facebook — F1 Academy : Budapest rejoint le calendrier 2027, finale à Las Vegas - f1news.fr — https://www.facebook.com/1757379583055094/posts/1769605735165812
- meta_pronos/facebook — Indonésie : la jeunesse de nouveau dans la rue contre la politique du gouvernement — https://www.facebook.com/1757379583055094/posts/1769606181832434
- meta_pronos/facebook — Le PS s'oppose à la candidature de David Lisnard à la tête de l'AMF — https://www.facebook.com/1757379583055094/posts/1769605135165872
- meta_pronos/facebook — Mercato : Arsenal s'intéresse à Endrick, Newcastle et Sunderland suivent Dion Beljo — https://www.facebook.com/1757379583055094/posts/1769605231832529
- meta_pronos/facebook — PlayStation abandonne le jeu-service Fairgames de Haven Studios — https://www.facebook.com/1757379583055094/posts/1769591448500574
- meta_pronos/facebook — Pologne : Varsovie accueille la Marche de l'indépendance dans un climat tendu — https://www.facebook.com/1757379583055094/posts/1769605378499181
- meta_pronos/facebook — Woodman évoque son départ de Bromley dans le podcast 72+ de la EFL — https://www.facebook.com/1757379583055094/posts/1769606088499110
- meta_univers/facebook — Découvre AlloLivre — https://www.facebook.com/122098313661535169/posts/122107745265535169
- meta_univers/facebook — Découvre La Pastille TV — https://www.facebook.com/122098313661535169/posts/122107745547535169
- meta_univers/facebook — Découvre VM Actus — https://www.facebook.com/122098313661535169/posts/122107745373535169
- meta_univers/facebook — Découvre VM CV — https://www.facebook.com/122098313661535169/posts/122107745733535169
- meta_univers/facebook — Découvre VM Gaming — https://www.facebook.com/122098313661535169/posts/122107745451535169
- meta_univers/facebook — Découvre VM Météo & Découverte — https://www.facebook.com/122098313661535169/posts/122107746051535169
- meta_univers/facebook — Découvre VM Recettes — https://www.facebook.com/122098313661535169/posts/122107745979535169
- meta_univers/facebook — Découvre VM Shop — https://www.facebook.com/122098313661535169/posts/122107745889535169
- meta_univers/facebook — Découvre VM Sport & randonnée — https://www.facebook.com/122098313661535169/posts/122107746195535169
- meta_univers/facebook — Découvre VM Studio — https://www.facebook.com/122098313661535169/posts/122107745307535169
- meta_univers/instagram — Découvre AlloLivre — https://www.instagram.com/p/DflOoUbCd6Y/
- meta_univers/instagram — Découvre La Pastille TV — https://www.instagram.com/p/DflOyFpiWwe/
- meta_univers/instagram — Découvre VM Actus — https://www.instagram.com/p/DflOtPXiVxY/
- meta_univers/instagram — Découvre VM CV — https://www.instagram.com/p/DflOzz5iSsu/
- meta_univers/instagram — Découvre VM Gaming — https://www.instagram.com/p/DflOvp_iQ4G/
- meta_univers/instagram — Découvre VM Météo & Découverte — https://www.instagram.com/p/DflO6tRkajm/
- meta_univers/instagram — Découvre VM Recettes — https://www.instagram.com/p/DflO4AKiQWR/
- meta_univers/instagram — Découvre VM Shop — https://www.instagram.com/p/DflO1q7iVBZ/
- meta_univers/instagram — Découvre VM Sport & randonnée — https://www.instagram.com/p/DflO8s1iXqq/
- meta_univers/instagram — Découvre VM Studio — https://www.instagram.com/p/DflOq1Zif-X/
