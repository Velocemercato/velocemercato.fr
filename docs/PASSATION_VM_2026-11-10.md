# Passation VM pour Claude et ChatGPT

Mise à jour du 10 novembre 2026, heure de Paris. Ce document décrit les demandes visibles dans cette conversation et les opérations vérifiées. Les consignes récentes ci-dessous remplacent les plans anciens de restauration ou de feuille blanche.

## Mission actuelle

Romain souhaite déléguer la gestion du média, du site et des publications à Claude et ChatGPT, en gardant la main sur les conseils pronos et les choix visuels. Il travaille depuis son téléphone et veut des réponses brèves, une étape à la fois. Il autorise la publication du nouvel accueil Véloce Mercato.

Le dépôt de référence est https://github.com/Velocemercato/velocemercato.fr. La branche main contient le nouvel accueil approuvé. Le commit b67c798b22ebba9717727f70fcb2b1195c6bf822 contient les derniers ajouts Manga. Lire ensuite les changements plus récents pour conserver les nouveaux articles et les corrections.

VM Univers, https://vmunivers.fr/, est la vitrine distincte. La demande actuelle de refonte porte sur l’accueil de velocemercato.fr. Conserver les pages existantes et leurs archives. Les anciennes demandes de restauration au 4 novembre servent de sauvegarde, elles ne décrivent plus le visuel souhaité.

## Accueil approuvé

L’accueil est un bureau de luxe au format téléphone, avec Paris et la tour Eiffel. Son fond et ses zones cliquables sont déjà codés dans index.html.

- Le titre Véloce Mercato ouvre https://vmunivers.fr/.
- Le micro ouvre la page Facebook Véloce Mercato.
- Le fauteuil ouvre la page Facebook VM Univers.
- Le globe ouvre la page Facebook VM Actus et pronos.
- Le pouf en cuir porte la broderie « LES CONSEILS PRONOS » et ouvre /pronos/.
- Les cadres ouvrent Foot, Multisport, Actus, Gaming, Manga & Séries, Studio et Pastille.
- Gaming est au milieu en haut et laisse visible la tour Eiffel.
- La bannière jeux d’argent 18+ et les logos sociaux sont présents en bas.

Les rubriques s’ouvrent dans des volets. assets/accueil-rubriques.js charge leurs sources et vérifie les nouveautés à l’ouverture puis toutes les dix minutes pendant que le volet reste ouvert.

## Contenus du site

- Foot utilise articles.json et les brèves françaises rédigées par le robot existant. Sources dont BBC Sport, The Guardian, RMC et Foot Mercato.
- Actus utilise actus/news.json. Le sélecteur de région présente les titres des 14 flux de France Télévisions, dont l’Outre-mer, via actus/regions-accueil.json et tools/accueil_regions.py. Belfort dispose aussi de belfort/actus.json.
- Gaming utilise vm-gaming/news.json. Eurogamer a été ajouté aux sources du robot update_gaming.py, qui doit rédiger en français même quand la source est étrangère.
- Multisport utilise multisport/actualites.json avec une sélection de médias et de spécialistes identifiés. Il s’agit de titres et liens sourcés, pas d’une traduction intégrale des articles étrangers.
- Les collectes Foot, Actus, Gaming et Multisport ont été programmées toutes les dix minutes dans les workflows existants. GitHub peut les retarder. Les nouveautés dépendent des sources et des limites des robots.
- Pastille est une rubrique de replay, avec une case par genre. Seules les vidéos marquées publiées avec un lien YouTube dans studio/diffusions.json sont affichées. Un genre vide reste signalé comme tel.
- Manga & Séries contient les documentaires sélectionnés et quinze collections officielles, décrites dans mangas/collections.json. Olive et Tom utilise sa playlist officielle, L’École des champions renvoie vers TF1+ et M6+, Cobra vers Mangas, onze collections vers TeamKids et Ulysse 31 vers CANAL+. Le catalogue consultable compte 72 titres. Les 72 titres ne correspondent pas à 72 intégrales disponibles. Les lecteurs de collections sont dans assets/mangas-collections.js et leur présentation dans assets/mangas-collections.css. Les conditions d’accès sont celles des diffuseurs.

## Publication du site et blocage vérifié

Les changements sont enregistrés sur main. Les déploiements GitHub Pages ont déclaré un succès, mais les derniers contrôles du domaine public renvoyaient encore l’ancienne page. Vérifier le contenu public et les nouveaux fichiers avant d’annoncer une publication réussie.

Le projet Cloudflare Pages observé dans les captures de Romain se nomme velocemercato. Le domaine cible est velocemercato.fr. Le navigateur de ChatGPT a reçu une erreur 403 pendant la connexion Cloudflare, y compris pendant la tentative assistée par Romain. Aucun accès connecté au tableau de bord n’a été confirmé.

.github/workflows/deployer-accueil-cloudflare.yml est préparé pour publier la version courante sur ce projet. Sa tentative du 10 novembre a échoué car les secrets CLOUDFLARE_API_TOKEN et CLOUDFLARE_ACCOUNT_ID étaient absents. Ne pas utiliser restauration-cloudflare.yml pour le nouvel accueil, ce fichier cible un ancien commit.

La priorité de Claude est de connecter Cloudflare par son intégration officielle, inspecter le projet et la route du domaine, puis publier main et contrôler le domaine. L’autorisation dans ChatGPT ne connecte pas automatiquement le compte dans Claude.

## Accès vérifiés ici et connexions à établir dans Claude

GitHub permet actuellement à ChatGPT de lire et modifier ce dépôt.

Metricool répond ici avec une marque nommée velocemercato, identifiant 7762102. Le retour vérifié contient une page Facebook, Instagram vmunivers.fr, TikTok velocemercato et une chaîne YouTube. Ce contrôle ne confirme pas les trois pages Facebook et les deux Instagram demandés. Vérifier chaque destination et son droit de publication avant de programmer.

Claude doit valider ses connexions séparément.

- Metricool figure dans le répertoire des connecteurs Claude. Adresse officielle du serveur https://ai.metricool.com/mcp. Guide https://help.metricool.com/fr/comment-connecter-le-mcp-de-metricool-a-claude-0l84v.
- L’intégration GitHub de connaissance fournit le contenu du dépôt. Pour modifier et publier le code, vérifier qu’un outil d’écriture GitHub ou Claude Code est réellement disponible. Guide https://support.claude.com/en/articles/10167454-use-the-github-integration.
- Cloudflare propose ses serveurs officiels avec connexion de compte. Guide https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/.

Les secrets de connexion doivent rester dans les formulaires de connexion ou le gestionnaire de secrets du service. Ce document ne contient aucun mot de passe ni jeton.

## Objectifs réseaux demandés, réalisation à contrôler

Les destinations demandées sont les pages Facebook Véloce Mercato, VM Actus et pronos et VM Univers, les Instagram veloce.mercato et vmunivers.fr, les TikTok correspondants et YouTube.

Les demandes récentes visaient des publications toutes les trente minutes sur les trois pages Facebook. Véloce Mercato couvre le foot et les autres sports. VM Actus couvre France, monde, régions, gaming et insolite. VM Univers présente les projets, les services et les réseaux de la marque. Romain souhaite également des Pastilles à midi et à 20 h. Plusieurs horaires plus anciens figurent dans l’historique, vérifier le planning actuellement programmé avant de compléter des créneaux.

Pour TikTok, Romain a demandé des Pastilles Foot, Actus et Gaming à 9 h, 12 h et 20 h, ainsi que deux promotions quotidiennes, l’une pour VM Univers et l’autre pour Véloce Mercato. Ce document n’atteste pas que tous ces créneaux sont programmés ni que tous les rendus vidéo existent.

Les conseils pronos et le message VIP dépendent des contenus fournis et validés par Romain.

## Travail à deux et automatisation

Utiliser ce dépôt et un planning partagé comme références. Avant une modification, lire le dernier état de main et les travaux en cours de l’autre assistant. Avant une publication sociale, lire les éléments déjà programmés, les reçus existants et les derniers contenus publiés. Un seul mécanisme envoie chaque publication vers chaque destination. Toute reprise doit conserver le suivi des doublons existant, notamment la branche broadcast-state quand elle est utilisée.

Les assistants ne partagent pas automatiquement leurs conversations, accès ou sessions. La continuité passe par les fichiers partagés, les commits et les outils connectés. Le fonctionnement récurrent doit être confié aux robots, aux tâches programmées ou au planning Metricool déjà configurés, avec suivi des échecs. Les connexions expirées et certaines validations du compte peuvent demander l’intervention de Romain.

Confirmer une publication sociale avec son identifiant et son lien public. Confirmer la mise en ligne du site avec le nouvel accueil et ses fichiers accessibles sur le domaine. Rapporter brièvement ce qui est fait, ce qui reste et l’éventuel blocage concret.
